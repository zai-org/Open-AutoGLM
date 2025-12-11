import argparse
import json
import os

from openai import OpenAI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="检查模型部署是否成功的工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/check_deployment_cn.py --base-url http://localhost:8000/v1 --apikey your-key --model autoglm-phone-9b
  python scripts/check_deployment_cn.py --base-url http://localhost:8000/v1 --apikey your-key --model autoglm-phone-9b --messages-file custom.json
        """,
    )

    parser.add_argument(
        "--base-url",
        type=str,
        required=True,
        help="API 服务的 base URL，例如: http://localhost:8000/v1",
    )

    parser.add_argument(
        "--apikey", type=str, default="EMPTY", help="API 密钥 (默认: EMPTY)"
    )

    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="要测试的模型名称，例如: autoglm-phone-9b",
    )

    parser.add_argument(
        "--messages-file",
        type=str,
        default="scripts/sample_messages.json",
        help="包含测试消息的 JSON 文件路径 (默认: scripts/sample_messages.json)",
    )

    parser.add_argument(
        "--max-tokens", type=int, default=3000, help="最大生成 token 数 (默认: 3000)"
    )

    parser.add_argument(
        "--temperature", type=float, default=0.0, help="采样温度 (默认: 0.0)"
    )

    parser.add_argument(
        "--top_p", type=float, default=0.85, help="nucleus sampling 参数 (默认: 0.85)"
    )

    parser.add_argument(
        "--frequency_penalty", type=float, default=0.2, help="频率惩罚参数 (默认: 0.2)"
    )

    args = parser.parse_args()

    # 读取测试消息
    if not os.path.exists(args.messages_file):
        print(f"错误: 消息文件 {args.messages_file} 不存在")
        exit(1)

    with open(args.messages_file) as f:
        messages = json.load(f)

    base_url = args.base_url
    api_key = args.apikey
    model = args.model

    print(f"开始测试模型推理...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Messages file: {args.messages_file}")
    print("=" * 80)

    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        response = client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            frequency_penalty=args.frequency_penalty,
            stream=False,
        )

        print("\n模型推理结果:")
        print("=" * 80)
        print(response.choices[0].message.content)
        print("=" * 80)

        if response.usage:
            print(f"\n统计信息:")
            print(f"  - Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  - Completion tokens: {response.usage.completion_tokens}")
            print(f"  - Total tokens: {response.usage.total_tokens}")

        print(f"\n请根据上述推理结果判断模型部署是否符合预期。")

    except Exception as e:
        print(f"\n调用 API 时发生错误:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(
            "\n提示: 请检查 base_url、api_key 和 model 参数是否正确，以及服务是否正在运行。"
        )
        exit(1)
