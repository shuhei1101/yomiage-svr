# VoiceBox API Server

VOICEVOX音声合成を提供するFastAPI HTTPサーバー。  
ずんだもん、春日部つむぎ、四国めたんなどのキャラクターボイスでテキストを読み上げます。

**🚀 すぐに始めたい方は [QUICKSTART.md](QUICKSTART.md) をご覧ください**

## 特徴

- **FastAPI ベース**: 高速で軽量なHTTPサーバー
- **どこからでも呼び出し可能**: curl、Python、任意のHTTPクライアントから利用可能
- **1つのサーバーで複数プロジェクト対応**: 常駐型サーバーで効率的
- **バックグラウンド実行**: リクエストは即座にレスポンスを返す
- **複数の話者をサポート**: キャラクターごとに速度設定可能
- **macOS / Linux / Windows 対応**

## セットアップ

### 1. VOICEVOXアプリの起動

VOICEVOX公式サイトからアプリをダウンロード・インストールし、起動しておく。  
デフォルトで `http://localhost:50021` にAPIサーバーが立ち上がる。

### 2. 依存パッケージのインストール

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. サーバー起動

```bash
./start_server.sh
```

または直接起動：

```bash
python api_server.py
```

サーバーが起動すると `http://127.0.0.1:8767` でアクセス可能になります。

## 設定

### 環境変数（オプション）

`.env` ファイルを作成して以下を設定できます：

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `VOICEVOX_BASE_URL` | VOICEVOXサーバーURL | `http://localhost:50021` |
| `DEFAULT_SPEAKER` | デフォルト話者名 | `zundamon` |

### 話者設定

`yomiage-svr/config.py` で話者（キャラクター）を設定できます。

**利用可能な話者:**

| 話者名 | キャラクター | スタイル | 速度 |
|--------|------------|---------|-----|
| `zundamon` | ずんだもん | ノーマル | 1.2 |
| `tsumugi` | 春日部つむぎ | ノーマル | 1.2 |
| `metan` | 四国めたん | ノーマル | 1.2 |

話者を追加・変更するには、`yomiage-svr/config.py` の `SPEAKERS` 辞書を編集してください。

## API仕様

### エンドポイント

#### `POST /speech`
テキストを音声合成して読み上げ

**リクエストボディ:**
```json
{
  "text": "読み上げるテキスト",
  "speaker_name": "zundamon"  // 省略可
}
```

**レスポンス:**
```json
{
  "status": "accepted",
  "message": "音声合成を開始しました: ...",
  "speaker_name": "zundamon"
}
```

#### `GET /speakers`
利用可能な話者一覧を取得

**レスポンス:**
```json
{
  "zundamon": {
    "name": "zundamon",
    "display_name": "ずんだもん（ノーマル）",
    "style": "ノーマル",
    "speed_scale": 1.2
  },
  ...
}
```

#### `GET /health`
ヘルスチェック

**レスポンス:**
```json
{
  "status": "ok"
}
```

## 使い方

### curlコマンドで呼び出し

```bash
# デフォルト話者で読み上げ
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは、音声合成のテストです"}'

# 話者を指定して読み上げ
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "春日部つむぎです", "speaker_name": "tsumugi"}'

# 利用可能な話者一覧を取得
curl http://127.0.0.1:8767/speakers
```

### Pythonから呼び出し

`client_example.py` を参照：

```python
import requests

# 音声合成リクエスト
response = requests.post(
    "http://127.0.0.1:8767/speech",
    json={"text": "こんにちは", "speaker_name": "zundamon"}
)
print(response.json())
```

詳細な使用例：

```bash
python client_example.py
```

### 他のプロジェクトから呼び出し

任意のプロジェクトから、HTTPリクエストでVoiceBox APIを呼び出せます：

```python
# あなたのプロジェクトのコード
import requests

def speak(text: str, speaker: str = "zundamon"):
    requests.post(
        "http://127.0.0.1:8767/speech",
        json={"text": text, "speaker_name": speaker}
    )

# 使用例
speak("処理が完了しました")
speak("エラーが発生しました", speaker="metan")
```

### 直接実行

```bash
python server.py
```

## プロジェクト構成

```
VoiceBox-API/
├── api_server.py               # FastAPIサーバー本体
├── server.py                   # MCPサーバー（旧版・オプション）
├── start_server.sh             # サーバー起動スクリプト
├── client_example.py           # クライアント使用例
├── yomiage-svr/
│   ├── __init__.py
│   ├── config.py               # 話者設定
│   ├── services/
│   │   ├── __init__.py
│   │   ├── voicevox_service.py # VOICEVOX HTTP API音声合成サービス
│   │   └── audio_service.py    # 音声再生サービス
│   └── tools/
│       ├── __init__.py
│       └── speech_tool.py      # Speechツール実装
├── requirements.txt            # 依存パッケージ
├── .env.example               # 環境変数サンプル
└── README.md                  # このファイル
```

## MCPサーバー版（GitHub Copilot / Claude Desktop から呼び出し）

### MCPとは？

**MCP (Model Context Protocol)** は、AIエージェント（GitHub Copilot、Claude Desktopなど）がツールを呼び出すための標準プロトコルです。MCPサーバーとして起動することで、AIエージェントから直接音声合成を実行できます。

### セットアップ

#### 1. MCP設定ファイルの配置

`.vscode/mcp.json` が既に配置されています：

```json
{
  "mcpServers": {
    "yomiage": {
      "command": "${workspaceFolder}/venv/bin/python",
      "args": ["mcp_server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

#### 2. Claude Desktop での設定（オプション）

Claude Desktopから利用する場合は、`~/Library/Application Support/Claude/claude_desktop_config.json` に追加：

```json
{
  "mcpServers": {
    "voicevox-speech": {
      "command": "python",
      "args": ["/path/to/yomiage-svr/mcp_server.py"],
      "cwd": "/path/to/yomiage-svr"
    }
  }
}
```

### MCPサーバーとして起動

```bash
# stdio transport（標準入出力での通信）
python mcp_server.py
```

### 提供されるツール

#### 1. `speak` - 音声合成＆読み上げ
```
テキストを音声合成してキャラクターボイスで読み上げ
引数:
  - text: 読み上げるテキスト
  - speaker_name: 話者名（zundamon, tsumugi, metan）。省略時は自動選択
  - transform_tone: 口調変換の有無（デフォルト: true）
```

#### 2. `list_available_speakers` - 話者一覧取得
```
利用可能な話者（キャラクター）の一覧を取得
戻り値: 話者情報のリスト（名前、スタイル、速度など）
```

#### 3. `transform_character_tone` - 口調変換のみ
```
テキストをキャラクターの口調に変換（音声合成なし、文字列のみ）
引数:
  - text: 変換するテキスト
  - speaker_name: 話者名
戻り値: 元テキストと変換後テキスト
```

### GitHub Copilot / Claude Desktop からの使用例

**GitHub Copilot:**
```
#yomiage タスクが完了しました、と読み上げて
```

**Claude Desktop:**
```
「処理が完了しました」をずんだもんの声で読み上げて
```

AIエージェントが自動的に適切なツールを呼び出し、音声で通知してくれます。

### HTTPサーバーとMCPサーバーの使い分け

| 用途 | 推奨サーバー | 起動方法 |
|------|------------|---------|
| curl / Python から呼び出し | FastAPI HTTPサーバー | `./start_server.sh` |
| GitHub Copilot / Claude Desktop から呼び出し | MCPサーバー | `.vscode/mcp.json` で自動起動 |
| 常駐サーバーとして複数プロジェクトから利用 | FastAPI HTTPサーバー | `./start_server.sh` |

**両方同時に起動することも可能です**（ポートが異なるため競合しません）。

## ライセンス・クレジット

VOICEVOX利用時は「VOICEVOX:ずんだもん」等のクレジット表記が必要です。  
詳細は [VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/) をご確認ください。
