# NotifyAgentActMCP

AIエージェント（GitHub Copilot、Claude Desktop等）から音声合成を実行できるMCPサーバー。  
ずんだもんなどのVOICEVOXキャラクターボイスでテキストを読み上げます。

## 機能

- **Speech ツール**: テキストをVOICEVOXで音声合成して読み上げ
- バックグラウンド実行（クライアントをブロッキングしない）
- macOS / Linux / Windows 対応
- 複数の話者（キャラクター）をサポート
- 話者ごとに速度設定可能

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

### 3. MCP設定

**VS Code の場合:**  
`.vscode/mcp.json` が既に設定されています。

**Claude Desktop の場合:**  
[README_MCP_SETUP.md](README_MCP_SETUP.md) を参照してください。

## 設定

### 環境変数（オプション）

`.env` ファイルを作成して以下を設定できます：

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `VOICEVOX_BASE_URL` | VOICEVOXサーバーURL | `http://localhost:50021` |
| `DEFAULT_SPEAKER` | デフォルト話者名 | `zundamon` |

### 話者設定

`vbmcp/config.py` で話者（キャラクター）を設定できます。

**利用可能な話者:**

| 話者名 | キャラクター | スタイル | 速度 |
|--------|------------|---------|-----|
| `zundamon` | ずんだもん | ノーマル | 1.0 |
| `zundamon_sweet` | ずんだもん | あまあま | 1.0 |
| `zundamon_tsun` | ずんだもん | ツンツン | 1.0 |
| `tsumugi` | 春日部つむぎ | ノーマル | 1.3 |
| `hau` | 雨晴はう | ノーマル | 1.0 |
| `metan` | 四国めたん | ノーマル | 1.0 |
| `metan_sweet` | 四国めたん | あまあま | 1.0 |

## 使い方

### 基本的な使い方

```
このプロジェクトの概要を #Speech で教えてください
```

```
「テスト完了しました。問題はありません。」と Speech で読み上げてください
```

### 話者を指定して使用

```
「こんにちは」を zundamon_tsun で #Speech して
```

```
「おはようございます」を tsumugi（春日部つむぎ）で #Speech して
```

### 直接実行

```bash
python server.py
```

## プロジェクト構成

```
NotifyAgentActMCP/
├── server.py                    # MCPサーバー本体（エントリーポイント）
├── vbmcp/
│   ├── __init__.py
│   ├── config.py               # 話者設定
│   ├── services/
│   │   ├── __init__.py
│   │   ├── voicevox_service.py  # VOICEVOX HTTP API音声合成サービス
│   │   └── audio_service.py     # 音声再生サービス
│   └── tools/
│       ├── __init__.py
│       └── speech_tool.py       # Speechツール実装
├── requirements.txt             # 依存パッケージ
├── .env.example                # 環境変数サンプル
├── .vscode/
│   └── mcp.json                # MCP設定ファイル
├── README.md                   # このファイル
└── README_MCP_SETUP.md         # MCP設定ガイド
```

## ライセンス・クレジット

VOICEVOX利用時は「VOICEVOX:ずんだもん」等のクレジット表記が必要です。  
詳細は [VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/) をご確認ください。
