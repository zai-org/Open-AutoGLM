# Open-AutoGLM

[中文](README.md) | [English](README_en.md)

<div align="center">
<img src=resources/logo.svg width="20%"/>
</div>
<p align="center">
    👋 <a href="resources/WECHAT.md" target="_blank">WeChat</a> または <a href="https://discord.gg/QR7SARHRxK" target="_blank">Discord</a> コミュニティに参加
</p>

## クイックスタート

Claude Code を [GLM Coding Plan](https://z.ai/subscribe) で設定し、以下のプロンプトを入力することで、本プロジェクトを素早くデプロイできます。

```
Access the documentation and install AutoGLM for me
https://raw.githubusercontent.com/zai-org/Open-AutoGLM/refs/heads/main/README_en.md
```

## プロジェクト概要

Phone Agent は AutoGLM をベースに構築されたモバイル向けインテリジェントアシスタントフレームワークです。マルチモーダルな方法でスマートフォンの画面内容を理解し、自動化された操作によってユーザーのタスク完了を支援します。システムは ADB（Android Debug Bridge）を通じてデバイスを制御し、視覚言語モデルで画面を認識し、インテリジェントな計画能力によって操作フローを生成・実行します。ユーザーは「eBay を開いてワイヤレスイヤホンを検索」のように自然言語で要求を伝えるだけで、Phone Agent が意図を自動的に解析し、現在の画面を理解し、次のアクションを計画して、ワークフロー全体を完了します。また、機密操作の確認機構を内蔵しており、ログインや認証コードのシナリオでは手動介入をサポートしています。さらに、リモート ADB デバッグ機能を提供し、WiFi またはネットワーク経由でデバイスに接続して、柔軟なリモート制御と開発を実現できます。

> ⚠️ 本プロジェクトは研究・学習目的のみに使用してください。違法な情報取得、システム妨害、その他の違法行為への使用は固く禁じられています。[利用規約](resources/privacy_policy_en.txt)を注意深くご確認ください。

## モデルダウンロードリンク

| モデル | ダウンロードリンク |
|--------|-------------------|
| AutoGLM-Phone-9B | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B) |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) |

`AutoGLM-Phone-9B` は中国語のモバイルアプリ向けに最適化されたモデルです。`AutoGLM-Phone-9B-Multilingual` は英語シナリオをサポートし、英語やその他の言語コンテンツを含むアプリケーションに適しています。

## 環境準備

### 1. Python 環境

Python 3.10 以上を推奨します。

### 2. ADB（Android Debug Bridge）

1. 公式 ADB [インストールパッケージ](https://developer.android.com/tools/releases/platform-tools)をダウンロードし、任意のパスに解凍
2. 環境変数を設定

- macOS での設定方法：`Terminal` または任意のコマンドラインツールで

  ```bash
  # 解凍先ディレクトリが ~/Downloads/platform-tools の場合。異なる場合はコマンドを調整してください。
  export PATH=${PATH}:~/Downloads/platform-tools
  ```

- Windows での設定方法：[サードパーティのチュートリアル](https://blog.csdn.net/x2584179909/article/details/108319973)を参考に設定してください。

### 3. Android 7.0+ のデバイスまたはエミュレータで「開発者モード」と「USB デバッグ」を有効化

1. 開発者モードの有効化：通常は「設定 → 端末情報 → ビルド番号」を約10回連続でタップすると、「開発者モードが有効になりました」というポップアップが表示されます。端末によって若干異なる場合がありますので、見つからない場合はオンラインで検索してください。
2. USB デバッグの有効化：開発者モードを有効にした後、「設定 → 開発者向けオプション → USB デバッグ」で有効にします。
3. 一部の端末では、開発者オプションを設定後、再起動が必要な場合があります。USB ケーブルでスマートフォンをパソコンに接続し、`adb devices` でデバイス情報が表示されるかテストしてください。表示されない場合は接続に失敗しています。

**関連する権限を必ず確認してください**

![権限](resources/screenshot-20251210-120416.png)

### 4. ADB Keyboard のインストール（テキスト入力用）

[インストールパッケージ](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk)をダウンロードし、対応する Android デバイスにインストールします。
注意：インストール後、「設定 → 入力方法」または「設定 → キーボード一覧」で `ADB Keyboard` を有効にする必要があります（またはコマンド `adb shell ime enable com.android.adbkeyboard/.AdbIME` を使用 [使用方法](https://github.com/senzhk/ADBKeyBoard/blob/master/README.md#how-to-use)）。

## デプロイ準備

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. ADB の設定

**USB ケーブルがデータ転送に対応していること**を確認してください（充電専用ではないこと）。

ADB がインストールされていることを確認し、**USB ケーブル**でデバイスを接続します：

```bash
# 接続されているデバイスを確認
adb devices

# 出力にデバイスが表示されるはずです。例：
# List of devices attached
# emulator-5554   device
```

### 3. モデルサービスの起動

モデルサービスを自分でデプロイするか、サードパーティのモデルサービスプロバイダーを利用できます。

#### オプション A：サードパーティのモデルサービスを利用

モデルを自分でデプロイしたくない場合は、以下の当社モデルをデプロイ済みのサードパーティサービスを利用できます：

**1. z.ai**

- ドキュメント：https://docs.z.ai/api-reference/introduction
- `--base-url`：`https://api.z.ai/api/paas/v4`
- `--model`：`autoglm-phone-multilingual`
- `--apikey`：z.ai プラットフォームで API キーを申請

**2. Novita AI**

- ドキュメント：https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual
- `--base-url`：`https://api.novita.ai/openai`
- `--model`：`zai-org/autoglm-phone-9b-multilingual`
- `--apikey`：Novita AI プラットフォームで API キーを申請

**3. Parasail**

- ドキュメント：https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual
- `--base-url`：`https://api.parasail.io/v1`
- `--model`：`parasail-auto-glm-9b-multilingual`
- `--apikey`：Parasail プラットフォームで API キーを申請

**4. 智谱 BigModel（中国向け）**

- ドキュメント：https://docs.bigmodel.cn/cn/api/introduction
- `--base-url`：`https://open.bigmodel.cn/api/paas/v4`
- `--model`：`autoglm-phone`
- `--apikey`：智谱プラットフォームで API キーを申請

**5. ModelScope（中国向け）**

- ドキュメント：https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B
- `--base-url`：`https://api-inference.modelscope.cn/v1`
- `--model`：`ZhipuAI/AutoGLM-Phone-9B`
- `--apikey`：ModelScope プラットフォームで API キーを申請

サードパーティサービスの使用例：

```bash
# z.ai を使用
python main.py --base-url https://api.z.ai/api/paas/v4 --model "autoglm-phone-multilingual" --apikey "your-z-ai-api-key" "Open Chrome browser"

# Novita AI を使用
python main.py --base-url https://api.novita.ai/openai --model "zai-org/autoglm-phone-9b-multilingual" --apikey "your-novita-api-key" "Open Chrome browser"

# Parasail を使用
python main.py --base-url https://api.parasail.io/v1 --model "parasail-auto-glm-9b-multilingual" --apikey "your-parasail-api-key" "Open Chrome browser"
```

#### オプション B：モデルを自分でデプロイ

ローカルまたは自分のサーバーにモデルをデプロイしたい場合：

1. `requirements.txt` の `For Model Deployment` セクションに従って、推論エンジンフレームワークをインストールしてモデルをダウンロードします。
2. SGlang / vLLM 経由で起動し、OpenAI 形式のサービスを取得します。以下は vLLM のデプロイ方法です。提供する起動パラメータに厳密に従ってください：

- vLLM：

```shell
python3 -m vllm.entrypoints.openai.api_server \
 --served-model-name autoglm-phone-9b-multilingual \
 --allowed-local-media-path /   \
 --mm-encoder-tp-mode data \
 --mm_processor_cache_type shm \
 --mm_processor_kwargs "{\"max_pixels\":5000000}" \
 --max-model-len 25480  \
 --chat-template-content-format string \
 --limit-mm-per-prompt "{\"image\":10}" \
 --model zai-org/AutoGLM-Phone-9B-Multilingual \
 --port 8000
```

- このモデルは `GLM-4.1V-9B-Thinking` と同じアーキテクチャです。モデルデプロイの詳細については、[GLM-V](https://github.com/zai-org/GLM-V) を参照してください。

- 正常に起動すると、`http://localhost:8000/v1` でモデルサービスにアクセスできます。リモートサーバーにモデルをデプロイした場合は、そのサーバーの IP アドレスを使用してアクセスしてください。

### 4. モデルデプロイの確認

モデルサービスを起動した後、以下のコマンドでデプロイを確認できます：

```bash
python scripts/check_deployment_en.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b-multilingual
```

サードパーティのモデルサービスを使用する場合：

```bash
# Novita AI
python scripts/check_deployment_en.py --base-url https://api.novita.ai/openai --model zai-org/autoglm-phone-9b-multilingual --apikey your-novita-api-key

# Parasail
python scripts/check_deployment_en.py --base-url https://api.parasail.io/v1 --model parasail-auto-glm-9b-multilingual --apikey your-parasail-api-key
```

正常に実行されると、スクリプトはモデルの推論結果とトークン統計を表示し、モデルデプロイが正しく動作しているか確認できます。

## AutoGLM の使用方法

### コマンドライン

デプロイしたモデルに応じて `--base-url` と `--model` パラメータを設定します。例：

```bash
# インタラクティブモード
python main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b-multilingual"

# モデルエンドポイントを指定
python main.py --base-url http://localhost:8000/v1 "Open Maps and search for nearby coffee shops"

# API キーで認証
python main.py --apikey sk-xxxxx

# 英語のシステムプロンプトを使用
python main.py --lang en --base-url http://localhost:8000/v1 "Open Chrome browser"

# サポートされているアプリを一覧表示
python main.py --list-apps
```

### Python API

```python
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig

# モデルを設定
model_config = ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b-multilingual",
)

# Agent を作成
agent = PhoneAgent(model_config=model_config)

# タスクを実行
result = agent.run("Open eBay and search for wireless earphones")
print(result)
```

## リモートデバッグ

Phone Agent は WiFi/ネットワーク経由でのリモート ADB デバッグをサポートしており、USB 接続なしでデバイスを制御できます。

### リモートデバッグの設定

#### スマートフォンでワイヤレスデバッグを有効化

スマートフォンとパソコンが同じ WiFi ネットワークに接続されていることを確認してください（下図参照）：

![ワイヤレスデバッグを有効化](resources/screenshot-20251210-120630.png)

#### パソコンで標準 ADB コマンドを使用

```bash
# WiFi 経由で接続（スマートフォンに表示される IP アドレスとポートに置き換えてください）
adb connect 192.168.1.100:5555

# 接続を確認
adb devices
# 表示例：192.168.1.100:5555    device
```

### デバイス管理コマンド

```bash
# 接続されているすべてのデバイスを一覧表示
adb devices

# リモートデバイスに接続
adb connect 192.168.1.100:5555

# 特定のデバイスを切断
adb disconnect 192.168.1.100:5555

# 特定のデバイスでタスクを実行
python main.py --device-id 192.168.1.100:5555 --base-url http://localhost:8000/v1 --model "autoglm-phone-9b-multilingual" "Open TikTok and browse videos"
```

### Python API でのリモート接続

```python
from phone_agent.adb import ADBConnection, list_devices

# 接続マネージャーを作成
conn = ADBConnection()

# リモートデバイスに接続
success, message = conn.connect("192.168.1.100:5555")
print(f"接続状態: {message}")

# 接続されているデバイスを一覧表示
devices = list_devices()
for device in devices:
    print(f"{device.device_id} - {device.connection_type.value}")

# USB デバイスで TCP/IP を有効化
success, message = conn.enable_tcpip(5555)
ip = conn.get_device_ip()
print(f"デバイス IP: {ip}")

# 切断
conn.disconnect("192.168.1.100:5555")
```

### リモート接続のトラブルシューティング

**接続が拒否される：**

- デバイスとパソコンが同じネットワークにあることを確認
- ファイアウォールがポート 5555 をブロックしていないか確認
- TCP/IP モードが有効になっていることを確認：`adb tcpip 5555`

**接続が切断される：**

- WiFi が切断されている可能性があります。`--connect` で再接続してください
- 一部のデバイスは再起動後に TCP/IP が無効になります。USB 経由で再度有効にしてください

**複数のデバイス：**

- `--device-id` を使用して使用するデバイスを指定
- または `--list-devices` を使用して接続されているすべてのデバイスを表示

## 設定

### カスタム SYSTEM PROMPT

システムは中国語と英語の両方のプロンプトを提供しており、`--lang` パラメータで切り替えられます：

- `--lang cn` - 中国語プロンプト（デフォルト）、設定ファイル：`phone_agent/config/prompts_zh.py`
- `--lang en` - 英語プロンプト、設定ファイル：`phone_agent/config/prompts_en.py`

対応する設定ファイルを直接編集して、特定の領域でのモデル能力を強化したり、アプリ名を注入して特定のアプリを無効にしたりできます。

### 環境変数

| 変数 | 説明 | デフォルト値 |
|------|------|-------------|
| `PHONE_AGENT_BASE_URL` | モデル API の URL | `http://localhost:8000/v1` |
| `PHONE_AGENT_MODEL` | モデル名 | `autoglm-phone-9b` |
| `PHONE_AGENT_API_KEY` | 認証用 API キー | `EMPTY` |
| `PHONE_AGENT_MAX_STEPS` | タスクあたりの最大ステップ数 | `100` |
| `PHONE_AGENT_DEVICE_ID` | ADB デバイス ID | （自動検出） |
| `PHONE_AGENT_LANG` | 言語（`cn` または `en`） | `en` |

### モデル設定

```python
from phone_agent.model import ModelConfig

config = ModelConfig(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",  # API キー（必要な場合）
    model_name="autoglm-phone-9b-multilingual",  # モデル名
    max_tokens=3000,  # 最大出力トークン数
    temperature=0.1,  # サンプリング温度
    frequency_penalty=0.2,  # 頻度ペナルティ
)
```

### Agent 設定

```python
from phone_agent.agent import AgentConfig

config = AgentConfig(
    max_steps=100,  # タスクあたりの最大ステップ数
    device_id=None,  # ADB デバイス ID（None で自動検出）
    lang="en",  # 言語：cn（中国語）または en（英語）
    verbose=True,  # デバッグ情報を出力（思考プロセスとアクションを含む）
)
```

### Verbose モード出力

`verbose=True` の場合、Agent は各ステップで詳細な情報を出力します：

```
==================================================
💭 思考プロセス:
--------------------------------------------------
現在システムデスクトップにいます。まず eBay アプリを起動する必要があります
--------------------------------------------------
🎯 実行アクション:
{
  "_metadata": "do",
  "action": "Launch",
  "app": "eBay"
}
==================================================

...（アクション実行後、次のステップに続く）

==================================================
💭 思考プロセス:
--------------------------------------------------
eBay が開きました。検索ボックスをタップする必要があります
--------------------------------------------------
🎯 実行アクション:
{
  "_metadata": "do",
  "action": "Tap",
  "element": [499, 182]
}
==================================================

🎉 ================================================
✅ タスク完了: eBay を開いて 'wireless earphones' を検索しました
==================================================
```

これにより、AI の推論プロセスと各ステップの具体的な操作を明確に確認できます。

## サポートされているアプリ

Phone Agent は 50 以上の主要なアプリケーションをサポートしています：

| カテゴリ | アプリ |
|---------|--------|
| ソーシャル＆メッセージング | X, TikTok, WhatsApp, Telegram, Facebook Messenger, Google Chat, Quora, Reddit, Instagram |
| 生産性＆オフィス | Gmail, Google Calendar, Google Drive, Google Docs, Google Tasks, Joplin |
| ライフ・ショッピング＆金融 | Amazon Shopping, Temu, Bluecoins, Duolingo, Google Fit, eBay |
| ユーティリティ＆メディア | Google Clock, Chrome, Google Play Store, Google Play Books, Files by Google |
| 旅行＆ナビゲーション | Google Maps, Booking.com, Trip.com, Expedia, OpenTracks |

`python main.py --list-apps` を実行して完全なリストを確認できます。

## 利用可能なアクション

Agent は以下のアクションを実行できます：

| アクション | 説明 |
|------------|------|
| `Launch` | アプリを起動 |
| `Tap` | 指定座標をタップ |
| `Type` | テキストを入力 |
| `Swipe` | 画面をスワイプ |
| `Back` | 前のページに戻る |
| `Home` | ホーム画面に戻る |
| `Long Press` | 長押し |
| `Double Tap` | ダブルタップ |
| `Wait` | ページの読み込みを待機 |
| `Take_over` | 手動介入をリクエスト（ログイン/認証コードなど） |

## カスタムコールバック

機密操作の確認と手動介入を処理：

```python
def my_confirmation(message: str) -> bool:
    """機密操作確認コールバック"""
    return input(f"{message} を実行しますか？(y/n): ").lower() == "y"


def my_takeover(message: str) -> None:
    """手動介入コールバック"""
    print(f"手動で完了してください: {message}")
    input("完了後、Enter を押してください...")


agent = PhoneAgent(
    confirmation_callback=my_confirmation,
    takeover_callback=my_takeover,
)
```

## サンプル

`examples/` ディレクトリでその他の使用例を確認できます：

- `basic_usage.py` - 基本的なタスク実行
- シングルステップデバッグモード
- バッチタスク実行
- カスタムコールバック

## 開発

### 開発環境のセットアップ

開発には dev 依存関係が必要です：

```bash
pip install -e ".[dev]"
```

### テストの実行

```bash
pytest tests/
```

### 完全なプロジェクト構造

```
phone_agent/
├── __init__.py          # パッケージエクスポート
├── agent.py             # PhoneAgent メインクラス
├── adb/                 # ADB ユーティリティ
│   ├── connection.py    # リモート/ローカル接続管理
│   ├── screenshot.py    # スクリーンキャプチャ
│   ├── input.py         # テキスト入力（ADB Keyboard）
│   └── device.py        # デバイス制御（タップ、スワイプなど）
├── actions/             # アクション処理
│   └── handler.py       # アクション実行器
├── config/              # 設定
│   ├── apps.py          # サポートされているアプリのマッピング
│   ├── prompts_zh.py    # 中国語システムプロンプト
│   └── prompts_en.py    # 英語システムプロンプト
└── model/               # AI モデルクライアント
    └── client.py        # OpenAI 互換クライアント
```

## FAQ

よくある問題とその解決策：

### デバイスが見つからない

ADB サービスを再起動してみてください：

```bash
adb kill-server
adb start-server
adb devices
```

それでもデバイスが認識されない場合は、以下を確認してください：
1. USB デバッグが有効になっているか
2. USB ケーブルがデータ転送に対応しているか（充電専用のケーブルもあります）
3. スマートフォンの認証ポップアップで「許可」をタップしたか
4. 別の USB ポートまたはケーブルを試す

### アプリは開けるがタップできない

一部のデバイスでは、以下の両方のデバッグオプションを有効にする必要があります：
- **USB デバッグ**
- **USB デバッグ（セキュリティ設定）**

「設定 → 開発者向けオプション」で両方のオプションが有効になっていることを確認してください。

### テキスト入力が機能しない

1. デバイスに ADB Keyboard がインストールされていることを確認
2. 設定 > システム > 言語と入力 > 仮想キーボードで有効にする
3. Agent は入力が必要な時に自動的に ADB Keyboard に切り替えます

### スクリーンショットが失敗する（黒い画面）

これは通常、アプリが機密ページ（支払い、パスワード、銀行アプリ）を表示していることを意味します。Agent は自動的にこれを検出し、手動介入をリクエストします。

### Windows でのエンコーディング問題

`UnicodeEncodeError gbk code` のようなエラーメッセージ

解決策：コードを実行する前に環境変数を追加：`PYTHONIOENCODING=utf-8`

### 非 TTY 環境でインタラクティブモードが動作しない

`EOF when reading a line` のようなエラー

解決策：非インタラクティブモードでタスクを直接指定するか、TTY モードのターミナルアプリケーションに切り替えてください。

### 引用

私たちの研究が役立った場合は、以下の論文を引用してください：

```bibtex
@article{liu2024autoglm,
  title={Autoglm: Autonomous foundation agents for guis},
  author={Liu, Xiao and Qin, Bo and Liang, Dongzhu and Dong, Guang and Lai, Hanyu and Zhang, Hanchen and Zhao, Hanlin and Iong, Iat Long and Sun, Jiadai and Wang, Jiaqi and others},
  journal={arXiv preprint arXiv:2411.00820},
  year={2024}
}
@article{xu2025mobilerl,
  title={MobileRL: Online Agentic Reinforcement Learning for Mobile GUI Agents},
  author={Xu, Yifan and Liu, Xiao and Liu, Xinghan and Fu, Jiaqi and Zhang, Hanchen and Jing, Bohao and Zhang, Shudan and Wang, Yuting and Zhao, Wenyi and Dong, Yuxiao},
  journal={arXiv preprint arXiv:2509.18119},
  year={2025}
}
```

---

## 自動デプロイガイド（AI アシスタント向け）

> **このセクションは、Open-AutoGLM の自動デプロイを行う AI アシスタント（Claude Code など）向けに設計されています。**
>
> 人間の読者の場合は、このセクションをスキップして上記のドキュメントに従ってください。

---

### プロジェクト概要

Open-AutoGLM はフォン Agent フレームワークです：
- **入力**：ユーザーの自然言語による指示（例：「WhatsApp を開いて John にメッセージを送って」）
- **出力**：ユーザーの Android スマートフォンを自動操作してタスクを完了
- **メカニズム**：スクリーンショット → 視覚モデルが画面を理解 → タップ座標を出力 → ADB がアクションを実行 → ループ

アーキテクチャは 2 つの部分で構成：
1. **Agent コード**（このリポジトリ）：ユーザーのパソコンで実行、モデル呼び出し、アクション解析、スマートフォン制御を担当
2. **視覚モデルサービス**：リモート API またはローカルデプロイ

---

### デプロイ前チェックリスト

デプロイを開始する前に、ユーザーに以下の項目を確認してください：

#### ハードウェア要件
- [ ] ユーザーが Android スマートフォン（Android 7.0+）を持っている
- [ ] ユーザーがデータ転送に対応した USB ケーブル（充電専用ではない）を持っている
- [ ] スマートフォンとパソコンが USB ケーブルで接続可能

#### スマートフォンの設定
- [ ] 開発者モードが有効（設定 → 端末情報 → ビルド番号を 7 回タップ）
- [ ] USB デバッグが有効（設定 → 開発者向けオプション → USB デバッグ）
- [ ] 一部のモデルでは「USB デバッグ（セキュリティ設定）」も有効にする必要あり
- [ ] ADB Keyboard アプリがインストールされている（ダウンロード：https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk）
- [ ] ADB Keyboard がシステム設定で有効（設定 → 言語と入力 → ADB Keyboard を有効化）

#### モデルサービスの確認（いずれかを選択）

**ユーザーに明確に確認：AutoGLM モデルサービスへのアクセスは既にありますか？**

- **オプション A：デプロイ済みモデルサービスを使用（推奨）**
  - ユーザーがモデルサービスの URL を提供（例：`http://xxx.xxx.xxx.xxx:8000/v1`）
  - ローカル GPU 不要、モデルダウンロード不要
  - この URL を `--base-url` パラメータとして直接使用

- **オプション B：モデルをローカルにデプロイ（高スペック要件）**
  - NVIDIA GPU が必要（24GB+ VRAM 推奨）
  - vLLM または SGLang のインストールが必要
  - 約 20GB のモデルファイルのダウンロードが必要
  - **ユーザーが初心者または不明な場合は、オプション A を強く推奨**

---

### デプロイ手順

#### フェーズ 1：環境セットアップ

```bash
# 1. ADB ツールをインストール
# macOS：
brew install android-platform-tools
# または手動でダウンロード：https://developer.android.com/tools/releases/platform-tools

# Windows：ダウンロードして解凍し、PATH 環境変数に追加

# 2. ADB のインストールを確認
adb version
# バージョン情報が出力されるはず

# 3. スマートフォンを接続して確認
# USB ケーブルでスマートフォンを接続し、スマートフォンで「USB デバッグを許可」をタップ
adb devices
# デバイスリストが出力されるはず。例：
# List of devices attached
# XXXXXXXX    device
```

**`adb devices` で空リストまたは unauthorized が表示される場合：**
1. スマートフォンに認証ポップアップが表示されているか確認し、「許可」をタップ
2. USB デバッグが有効か確認
3. 別のケーブルまたは USB ポートを試す
4. `adb kill-server && adb start-server` を実行して再試行

#### フェーズ 2：Agent をインストール

```bash
# 1. リポジトリをクローン（まだの場合）
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM

# 2. 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係をインストール
pip install -r requirements.txt
pip install -e .
```

**注意：モデルリポジトリをクローンする必要はありません。モデルは API 経由で呼び出されます。**

#### フェーズ 3：モデルサービスを設定

**ユーザーがオプション A（デプロイ済みモデルを使用）を選択した場合：**

以下のサードパーティモデルサービスを利用できます：

1. **z.ai**
   - ドキュメント：https://docs.z.ai/api-reference/introduction
   - `--base-url`：`https://api.z.ai/api/paas/v4`
   - `--model`：`autoglm-phone-multilingual`
   - `--apikey`：z.ai プラットフォームで API キーを申請

2. **Novita AI**
   - ドキュメント：https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual
   - `--base-url`：`https://api.novita.ai/openai`
   - `--model`：`zai-org/autoglm-phone-9b-multilingual`
   - `--apikey`：Novita AI プラットフォームで API キーを申請

3. **Parasail**
   - ドキュメント：https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual
   - `--base-url`：`https://api.parasail.io/v1`
   - `--model`：`parasail-auto-glm-9b-multilingual`
   - `--apikey`：Parasail プラットフォームで API キーを申請

使用例：

```bash
# z.ai を使用
python main.py --base-url https://api.z.ai/api/paas/v4 --model "autoglm-phone-multilingual" --apikey "your-z-ai-api-key" "Open Chrome browser"

# Novita AI を使用
python main.py --base-url https://api.novita.ai/openai --model "zai-org/autoglm-phone-9b-multilingual" --apikey "your-novita-api-key" "Open Chrome browser"

# Parasail を使用
python main.py --base-url https://api.parasail.io/v1 --model "parasail-auto-glm-9b-multilingual" --apikey "your-parasail-api-key" "Open Chrome browser"
```

または、ユーザーが提供する URL を直接使用し、ローカルモデルデプロイの手順をスキップしてください。

**ユーザーがオプション B（モデルをローカルにデプロイ）を選択した場合：**

```bash
# 1. vLLM をインストール
pip install vllm

# 2. モデルサービスを起動（モデルを自動ダウンロード、約 20GB）
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b-multilingual \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs "{\"max_pixels\":5000000}" \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt "{\"image\":10}" \
  --model zai-org/AutoGLM-Phone-9B-Multilingual \
  --port 8000

# モデルサービス URL：http://localhost:8000/v1
```

#### フェーズ 4：デプロイを確認

```bash
# Open-AutoGLM ディレクトリで実行
# {MODEL_URL} を実際のモデルサービスアドレスに置き換え

python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual" "Open Gmail and send an email to File Transfer Assistant: Deployment successful"
```

**期待される結果：**
- スマートフォンが自動的に Gmail を開く
- 自動的に受信者を検索
- 「Deployment successful」というメッセージを自動的に送信

---

### トラブルシューティング

| エラー症状 | 考えられる原因 | 解決策 |
|-----------|---------------|--------|
| `adb devices` で何も表示されない | USB デバッグが有効でないかケーブルの問題 | 開発者オプションを確認、ケーブルを交換 |
| `adb devices` で unauthorized と表示 | スマートフォンが認証されていない | スマートフォンで「USB デバッグを許可」をタップ |
| アプリは開けるがタップできない | セキュリティデバッグ権限が不足 | 「USB デバッグ（セキュリティ設定）」を有効化 |
| テキスト入力が文字化けまたは入力されない | ADB Keyboard が有効でない | システム設定で ADB Keyboard を有効化 |
| スクリーンショットが黒い画面 | 機密ページ（支払い/銀行） | 正常な動作、システムが自動的に処理 |
| モデルサービスに接続できない | URL が間違っているかサービスが実行されていない | URL を確認、サービスが実行中か確認 |
| `ModuleNotFoundError` | 依存関係がインストールされていない | `pip install -r requirements.txt` を実行 |

---

### デプロイのポイント

1. **スマートフォンの接続を最優先で確認**：コードをインストールする前に、`adb devices` でデバイスが表示されることを確認
2. **ADB Keyboard をスキップしない**：これがないとテキスト入力が失敗します
3. **モデルサービスは外部依存**：Agent コードにはモデルが含まれていません。別途モデルサービスが必要です
4. **権限の問題はまずスマートフォンの設定を確認**：ほとんどの問題はスマートフォン側の設定が不完全なことが原因
5. **デプロイ後は簡単なタスクでテスト**：「Gmail を開いてファイル転送アシスタントにメッセージを送信」を受け入れ基準として推奨

---

### コマンドクイックリファレンス

```bash
# ADB 接続を確認
adb devices

# ADB サービスを再起動
adb kill-server && adb start-server

# 依存関係をインストール
pip install -r requirements.txt && pip install -e .

# Agent を実行（インタラクティブモード）
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual"

# Agent を実行（単一タスク）
python main.py --base-url {MODEL_URL} --model "autoglm-phone-9b-multilingual" "your task description"

# サポートされているアプリリストを表示
python main.py --list-apps
```

---

**デプロイ成功の指標：スマートフォンがユーザーの自然言語による指示を自動的に実行できる。**
