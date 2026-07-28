# Qwen3-VL-4B LoRA with MobileForge data

This example fine-tunes `Qwen/Qwen3-VL-4B-Instruct` to emit the MobileForge
`mobile_use` protocol supported by Open-AutoGLM's `mobileforge` agent profile.
It uses positive action steps exported in MobileForge GRPO conversation format.

The recipe is an experimental reference, not an official model release or
benchmark result.

## Privacy and artifact policy

This example intentionally contains no model weights, LoRA adapters,
checkpoints, optimizer states, datasets, screenshots, logs, device identifiers,
network addresses, API credentials, or machine-specific paths. Review your
training data and generated model card before publishing any artifact.

Model weights belong in a model registry such as Hugging Face or ModelScope,
subject to the base-model and dataset licenses; they should not be committed to
the Open-AutoGLM source repository.

## Install optional dependencies

Create a separate environment, install Open-AutoGLM, then install:

```bash
pip install -r examples/mobileforge/requirements.txt
```

Install `bitsandbytes` separately if you plan to use `--use-4bit`.
Install `vllm` in the serving environment.

## Prepare data

Download or generate MobileForge training data following the
[MobileForge data documentation](https://github.com/kwai/MobileForge/blob/main/docs/data_release.md).
The JSON file must contain conversation records with an `is_positive` flag, and
image references must be relative to `--image-dir`.

Do not train on or publish screenshots containing personal information unless
you have reviewed and appropriately sanitized them.

## Train

The defaults reproduce a small single-GPU SFT recipe: 2,000 positive samples,
two epochs, LoRA rank 16, and bf16 weights.

```bash
python examples/mobileforge/train_qwen3_vl_4b_lora.py \
  --data-path /path/to/mobileforge_grpo_image_paths.json \
  --image-dir /path/to/mobileforge_images \
  --output-dir /path/to/qwen3-vl-4b-mobileforge-lora
```

On smaller GPUs, add `--use-4bit`. The 4-bit path saves an adapter only because
merging a quantized training model is not reliable. The bf16 path saves both
`lora_adapter/` and a standalone `merged/` model.

## Serve and test

Serve the merged model:

```bash
bash examples/mobileforge/serve_qwen3_vl_4b.sh \
  /path/to/qwen3-vl-4b-mobileforge-lora/merged
```

Check that model responses parse into valid AutoGLM actions:

```bash
python -m examples.mobileforge.smoke_test \
  --model qwen3-vl-4b-mobileforge-sft \
  --data /path/to/mobileforge_grpo_image_paths.json \
  --image-dir /path/to/mobileforge_images
```

Then use it with a connected Android or HarmonyOS device:

```bash
python main.py \
  --device-type hdc \
  --agent-profile mobileforge \
  --base-url http://localhost:8000/v1 \
  --model qwen3-vl-4b-mobileforge-sft \
  "Open Settings and show the current system version"
```
