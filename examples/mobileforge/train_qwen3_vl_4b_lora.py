#!/usr/bin/env python3
"""LoRA SFT for Qwen3-VL-4B using positive MobileForge action steps."""

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import torch
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from PIL import Image
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

IMAGE_GRID_KEY = "".join(("image_grid_", "t", "h", "w"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LoRA SFT for Qwen3-VL-4B on MobileForge data"
    )
    parser.add_argument("--model-path", default="Qwen/Qwen3-VL-4B-Instruct")
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=2000)
    parser.add_argument("--max-image-size", type=int, default=768)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--num-epochs", type=float, default=2)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=8192)
    parser.add_argument("--use-4bit", action="store_true")
    return parser.parse_args()


def load_positive_samples(path: Path, max_samples: int) -> list[dict[str, Any]]:
    """Load positive conversation records without exposing their contents."""
    with path.open(encoding="utf-8") as data_file:
        data = json.load(data_file)
    if not isinstance(data, list):
        raise ValueError("Training data must be a JSON list")
    positive = [sample for sample in data if sample.get("is_positive", False)]
    if not positive:
        raise ValueError("Training data contains no positive samples")
    return positive[:max_samples] if max_samples > 0 else positive


def resolve_image(image_dir: Path, reference: str) -> Path:
    """Resolve a relative image reference without allowing path traversal."""
    root = image_dir.resolve()
    candidate = (root / reference).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Image reference escapes --image-dir: {reference}")
    return candidate


def prepare_sample(
    sample: dict[str, Any], image_dir: Path, max_image_size: int
) -> tuple[list[dict[str, Any]], str]:
    """Convert one MobileForge conversation into prompt messages and target."""
    input_messages: list[dict[str, Any]] = []
    target_text = ""

    for message in sample["conversations"]:
        role = message["role"]
        content = message["content"]
        if role == "assistant":
            if isinstance(content, list):
                target_text = content[0].get("text", "")
            else:
                target_text = str(content)
            continue

        if not isinstance(content, list):
            input_messages.append({"role": role, "content": content})
            continue

        converted: list[dict[str, Any]] = []
        for part in content:
            if part.get("type") == "text":
                converted.append({"type": "text", "text": part["text"]})
            elif part.get("type") == "image_url":
                reference = part["image_url"]["url"]
                image_path = resolve_image(image_dir, reference)
                if not image_path.is_file():
                    raise FileNotFoundError(f"Training image not found: {reference}")
                with Image.open(image_path) as source:
                    image = source.convert("RGB")
                image.thumbnail((max_image_size, max_image_size))
                converted.append({"type": "image", "image": image})
        input_messages.append({"role": role, "content": converted})

    if not target_text:
        raise ValueError("Sample has no assistant target")
    return input_messages, target_text


class MobileForgeLoRADataset(torch.utils.data.Dataset):
    """Tokenize MobileForge conversations and mask prompt tokens."""

    def __init__(
        self,
        samples: list[dict[str, Any]],
        processor: Any,
        image_dir: Path,
        max_image_size: int,
        max_length: int,
    ):
        self.samples = samples
        self.processor = processor
        self.image_dir = image_dir
        self.max_image_size = max_image_size
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        input_messages, target = prepare_sample(
            self.samples[index], self.image_dir, self.max_image_size
        )
        full_messages = input_messages + [{"role": "assistant", "content": target}]
        full_text = self.processor.apply_chat_template(
            full_messages, tokenize=False, add_generation_prompt=False
        )
        prompt_text = self.processor.apply_chat_template(
            input_messages, tokenize=False, add_generation_prompt=True
        )
        images = [
            part["image"]
            for message in input_messages
            if isinstance(message.get("content"), list)
            for part in message["content"]
            if part.get("type") == "image"
        ]
        image_input = images or None
        inputs = self.processor(
            text=[full_text],
            images=image_input,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
        )
        prompt = self.processor(
            text=[prompt_text],
            images=image_input,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
        )

        input_ids = inputs["input_ids"].squeeze(0)
        labels = input_ids.clone()
        labels[: prompt["input_ids"].shape[1]] = -100
        item = {
            "input_ids": input_ids,
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "labels": labels,
        }
        for key in ("pixel_values", IMAGE_GRID_KEY):
            if key in inputs:
                item[key] = inputs[key]
        return item


class MobileForgeCollator:
    """Pad text tensors and combine vision inputs."""

    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, batch: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        max_length = max(item["input_ids"].shape[0] for item in batch)

        def pad(tensor: torch.Tensor, value: int) -> torch.Tensor:
            amount = max_length - tensor.shape[0]
            return torch.cat([tensor, torch.full((amount,), value, dtype=tensor.dtype)])

        result = {
            "input_ids": torch.stack(
                [pad(item["input_ids"], self.pad_token_id) for item in batch]
            ),
            "attention_mask": torch.stack(
                [pad(item["attention_mask"], 0) for item in batch]
            ),
            "labels": torch.stack([pad(item["labels"], -100) for item in batch]),
        }
        for key in ("pixel_values", IMAGE_GRID_KEY):
            if key in batch[0]:
                result[key] = torch.cat([item[key] for item in batch], dim=0)
        return result


def copy_processor_files(model_path: str, merged_dir: Path) -> None:
    """Copy local tokenizer assets that save_pretrained may omit."""
    source_dir = Path(model_path)
    if not source_dir.is_dir():
        return
    for name in (
        "vocab.json",
        "merges.txt",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "chat_template.json",
        "preprocessor_config.json",
        "video_preprocessor_config.json",
        "added_tokens.json",
    ):
        source = source_dir / name
        destination = merged_dir / name
        if source.is_file() and not destination.exists():
            shutil.copy2(source, destination)


def main() -> None:
    args = parse_args()
    samples = load_positive_samples(args.data_path, args.max_samples)
    processor = AutoProcessor.from_pretrained(args.model_path)

    model_kwargs: dict[str, Any] = {
        "dtype": torch.bfloat16,
        "device_map": "auto" if args.use_4bit else "cuda:0",
        "trust_remote_code": True,
    }
    if args.use_4bit:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    model = AutoModelForImageTextToText.from_pretrained(args.model_path, **model_kwargs)
    if args.use_4bit:
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False

    model = get_peft_model(
        model,
        LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
            bias="none",
        ),
    )
    model.print_trainable_parameters()

    dataset = MobileForgeLoRADataset(
        samples,
        processor,
        args.image_dir,
        args.max_image_size,
        args.max_length,
    )
    pad_token_id = processor.tokenizer.pad_token_id
    if pad_token_id is None:
        pad_token_id = processor.tokenizer.eos_token_id

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(args.output_dir),
            num_train_epochs=args.num_epochs,
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            learning_rate=args.learning_rate,
            warmup_ratio=0.05,
            logging_steps=10,
            save_steps=200,
            save_total_limit=2,
            bf16=True,
            report_to="none",
            remove_unused_columns=False,
            dataloader_num_workers=0,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
        ),
        train_dataset=dataset,
        data_collator=MobileForgeCollator(pad_token_id),
    )
    trainer.train()

    adapter_dir = args.output_dir / "lora_adapter"
    model.save_pretrained(adapter_dir)
    processor.save_pretrained(adapter_dir)
    if args.use_4bit:
        print(f"Saved adapter to {adapter_dir}; skipped quantized merge")
        return

    merged_dir = args.output_dir / "merged"
    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(merged_dir, safe_serialization=True)
    processor.save_pretrained(merged_dir)
    copy_processor_files(args.model_path, merged_dir)
    print(f"Saved adapter to {adapter_dir} and merged model to {merged_dir}")


if __name__ == "__main__":
    main()
