---
name: yomiage-overview
description: VoiceBox APIサーバー（yomiage-svr）プロジェクトの包括的な概要。VOICEVOX音声合成、Ollama口調変換、FastAPI HTTPサーバーを組み合わせたキャラクターボイス読み上げシステムの全体構成、技術スタック、セットアップ手順を提供します。
license: MIT
---

# VoiceBox APIサーバー プロジェクト概要

## プロジェクト概要

### 1.1 目的
AIエージェント（GitHub Copilot、Claude Desktop等）から音声合成を実行できるMCPサーバーをPythonで実装する。ずんだもん、春日部つむぎ、四国めたんなどのキャラクターボイスでテキストを読み上げることで、AIとのインタラクションをより豊かにする。

### 1.2 背景
- C#版が存在するが、.NET SDKのインストールやVOICEVOX Coreのセットアップが複雑
- Pythonでの実装により、環境構築を簡素化し、保守性を向上させる
- VOICEVOXローカルサーバーのHTTP APIを利用することで、`requests` のみで簡潔に実装

## 機能要件

### 2.1 MCPサーバー機能
- **MCP (Model Context Protocol) サーバー**として動作
- **stdio**による通信をサポート
- GitHub Copilot / Claude Desktopからツールとして呼び出し可能

### 2.2 音声合成機能（Speechツール）
#### 2.2.1 基本機能
- ツール名: `Speech`
- 入力: テキスト（文字列）
- 出力: 音声再生（バックグラウンド実行）

#### 2.2.2 処理フロー
1. クライアントから音声合成リクエストを受信
2. VOICEVOXエンジンでテキストを音声合成（WAVファイル生成）
3. 一時ファイルに保存
4. 音声を再生
5. 再生完了後、一時ファイルを削除

#### 2.2.3 エラーハンドリング
- 音声合成エラー時はMCP通知で通知
- 音声再生エラー時も同様に通知
- エラー発生時も一時ファイルは確実に削除

### 2.3 音声設定
- **音声スタイルID**: 環境変数で設定可能
  - デフォルト: 1（ずんだもん ノーマル）
  - その他: 2（あまあま）、3（ツンツン）など
- **キャラクター**: VOICEVOXの全キャラクターに対応

## 非機能要件

### 3.1 パフォーマンス
- 音声合成処理は非同期で実行
- クライアントのリクエストは即座に応答（ブロッキングしない）
- 音声再生はバックグラウンドで実行

### 3.2 互換性
- **対応OS**: macOS (優先)、Linux、Windows
- **Python**: 3.9以上
- **VOICEVOX**: ローカルアプリ版（デフォルト `http://localhost:50021` でAPIサーバーが起動）

### 3.3 保守性
- 設定は環境変数で管理
- ログ出力は標準エラー出力に統一（MCPプロトコル準拠）
- モジュール化した構成

## 技術スタック

### 4.1 主要ライブラリ
- **mcp**: MCPサーバー実装
- **requests**: VOICEVOXローカルサーバーへのHTTPリクエスト
- **sounddevice** / **soundfile**: 音声再生（macOS対応）
- **python-dotenv**: 環境変数管理（開発用）

### 4.2 開発ツール
- **uv** / **pip**: パッケージ管理
- **python-dotenv**: 環境変数管理（開発用）

## プロジェクト構成

```
yomiage-svr/
├── api_server.py                 # FastAPI HTTPサーバー（メイン）
├── mcp_server.py                # MCPサーバー本体（MCPクライアント用）
├── start_server.sh              # 自動起動スクリプト
├── vbmcp/                       # メインパッケージ
│   ├── __init__.py
│   ├── config.py                # 話者設定・Ollama設定
│   ├── services/
│   │   ├── __init__.py
│   │   ├── voicevox_service.py  # VOICEVOX HTTP API音声合成サービス
│   │   ├── ollama_service.py    # Ollama口調変換サービス
│   │   ├── audio_service.py     # 音声再生サービス
│   │   └── character_selector.py # キャラクター自動選択
│   └── tools/
│       ├── __init__.py
│       └── speech_tool.py       # Speechツール実装
├── requirements.txt             # 依存パッケージ  
├── .vscode/
│   └── mcp.json               # MCP設定ファイル
└── README.md                  # 使い方ドキュメント
```

## 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `VOICEVOX_STYLE_ID` | 音声スタイルID（話者ID） | 1 | No |
| `VOICEVOX_BASE_URL` | VOICEVOXサーバーURL | http://localhost:50021 | No |
| `VOICEVOX_SPEED_SCALE` | 話す速度（0.5〜2.0） | 1.0 | No |
| `OLLAMA_BASE_URL` | OllamaサーバーURL | http://localhost:11434 | No |
| `OLLAMA_MODEL` | 使用モデル | gemma2:2b | No |

## セットアップ手順

### 7.1 VOICEVOXアプリの起動
VOICEVOX公式サイトからアプリをダウンロード・インストールし、起動しておく。
デフォルトで `http://localhost:50021` にAPIサーバーが立ち上がる。

### 7.2 Ollamaのインストールと起動
```bash
# Ollamaをインストール（macOS）
brew install ollama

# 軽量モデルをダウンロード
ollama pull gemma2:2b
```

### 7.3 依存パッケージインストール
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7.4 サーバー起動（推奨）
```bash
# 全自動セットアップ（VOICEVOX・Ollama・APIサーバー）
./start_server.sh
```

### 7.5 MCP設定
`.vscode/mcp.json` に以下を追加:
```json
{
  "servers": {
    "yomiage": {
      "type": "stdio", 
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "VOICEVOX_STYLE_ID": "1"
      }
    }
  }
}
```

## 使用例

### HTTP API（直接呼び出し）
```bash
# つむぎの口調変換＋音声合成
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "お疲れ様です", "speaker_name": "tsumugi"}'

# 口調変換のみ（音声再生なし）
curl -X POST http://127.0.0.1:8767/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "おつかれ", "speaker_name": "metan"}'
```

### MCP経由（GitHub Copilot）
```markdown
#yomiage タスクが完了しました
```

### 期待される動作
1. AIがテキストを生成
2. Speechツール/MCPツールが呼び出される
3. Ollama で口調変換（「お疲れ様です」→「お疲れ様です！あーし、嬉しいです！」）
4. VOICEVOX で音声合成
5. つむぎの音声で読み上げが開始
6. クライアントには即座に応答が返る

## 主要キャラクター設定

### ずんだもん
- 語尾: 「〜なのだ」「〜のだ」
- 一人称: 「ボク」
- 特徴: 明るく元気、フレンドリー

### 春日部つむぎ
- 語尾: 「〜です！」「〜ます！」（「ね」「よ」は使用禁止）
- 一人称: 「あーし」
- 特徴: 丁寧で優しい、相手を気遣う

### 四国めたん
- 語尾: 「〜わ」「〜かしら」「〜でしょ」
- 一人称: 「わたし」または省略
- 特徴: 冷静で落ち着いた、お姉さん的

## 制約事項

### 9.1 ライセンス
- VOICEVOX利用規約への準拠が必要
- 音声利用時は「VOICEVOX:ずんだもん」等のクレジット表記必須

### 9.2 技術的制約
- VOICEVOXアプリをローカルで事前起動しておく必要がある
- 音声合成はVOICEVOX HTTP API経由（`localhost:50021`）で実行
- 音声再生はシステムのオーディオデバイスに依存
- Ollama（口調変換）も事前起動が必要（`localhost:11434`）

## トラブルシューティング

### よくある問題
1. **Ollama未起動**: 口調変換が元のテキストのままの場合
   - 解決: `ollama serve` で起動するか `./start_server.sh` 使用
2. **ポート競合**: 8767ポートが使用中
   - 解決: `lsof -ti:8767 | xargs kill -9` でプロセス終了
3. **VOICEVOX未起動**: 音声合成エラー
   - 解決: VOICEVOXアプリを起動

## 今後の拡張案

### 10.1 機能拡張
- 複数キャラクターの選択機能
- 音声パラメータ調整（速度、音量、音程）
- 音声ファイルの保存機能

### 10.2 技術的改善
- キャッシュ機構の実装
- 音声合成の並列処理
- WebSocket経由のリアルタイム再生

## 成功基準

- [x] FastAPI HTTPサーバーとして正常に起動できる
- [x] MCPサーバーとして正常に起動できる
- [x] GitHub Copilot / Claude Desktopから呼び出せる
- [x] テキストを音声合成して再生できる
- [x] Ollama口調変換が正常動作する
- [x] エラー時も適切にハンドリングできる
- [x] 環境変数で音声スタイルを変更できる
- [x] macOS環境で問題なく動作する
- [x] 自動起動スクリプトが全サービスを統合管理する
