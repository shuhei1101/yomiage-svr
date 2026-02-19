# NotifyAgentActMCP - Python版 要件定義書

## 1. プロジェクト概要

### 1.1 目的
AIエージェント（GitHub Copilot、Claude Desktop等）から音声合成を実行できるMCPサーバーをPythonで実装する。ずんだもんなどのキャラクターボイスでテキストを読み上げることで、AIとのインタラクションをより豊かにする。

### 1.2 背景
- C#版が存在するが、.NET SDKのインストールやVOICEVOX Coreのセットアップが複雑
- Pythonでの実装により、環境構築を簡素化し、保守性を向上させる
- VOICEVOX Python SDKを活用することで、より簡潔な実装を実現

## 2. 機能要件

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

## 3. 非機能要件

### 3.1 パフォーマンス
- 音声合成処理は非同期で実行
- クライアントのリクエストは即座に応答（ブロッキングしない）
- 音声再生はバックグラウンドで実行

### 3.2 互換性
- **対応OS**: macOS (優先)、Linux、Windows
- **Python**: 3.9以上
- **VOICEVOX**: voicevox-core Python SDK

### 3.3 保守性
- 設定は環境変数で管理
- ログ出力は標準エラー出力に統一（MCPプロトコル準拠）
- モジュール化した構成

## 4. 技術スタック

### 4.1 主要ライブラリ
- **mcp**: MCPサーバー実装
- **voicevox-core**: 音声合成エンジン
- **pyaudio** / **sounddevice**: 音声再生（macOS対応）

### 4.2 開発ツール
- **uv** / **pip**: パッケージ管理
- **python-dotenv**: 環境変数管理（開発用）

## 5. プロジェクト構成

```
NotifyAgentActMCP/
├── server.py                 # MCPサーバー本体
├── services/
│   ├── __init__.py
│   ├── voicevox_service.py  # VOICEVOX音声合成サービス
│   └── audio_service.py     # 音声再生サービス
├── tools/
│   ├── __init__.py
│   └── speech_tool.py       # Speechツール実装
├── requirements.txt         # 依存パッケージ
├── .vscode/
│   └── mcp.json            # MCP設定ファイル
└── README.md               # 使い方ドキュメント
```

## 6. 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `VOICEVOX_STYLE_ID` | 音声スタイルID | 1 | No |
| `VOICEVOX_DICT_DIR` | Open JTalk辞書パス | (自動検出) | No |

## 7. セットアップ手順

### 7.1 依存パッケージインストール
```bash
pip install -r requirements.txt
```

### 7.2 VOICEVOX Coreのインストール
```bash
pip install voicevox-core
# または
voicevox-core install
```

### 7.3 MCP設定
`.vscode/mcp.json` に以下を追加:
```json
{
  "servers": {
    "NotifyAgentAct": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "VOICEVOX_STYLE_ID": "1"
      }
    }
  }
}
```

## 8. 使用例

### 8.1 GitHub Copilot / Claude Desktopからの呼び出し
```
このプロジェクトの概要を #Speech で教えてください
```

### 8.2 期待される動作
1. AIがテキストを生成
2. Speechツールが呼び出される
3. ずんだもんの音声で読み上げが開始
4. クライアントには即座に応答が返る

## 9. 制約事項

### 9.1 ライセンス
- VOICEVOX利用規約への準拠が必要
- 音声利用時は「VOICEVOX:ずんだもん」等のクレジット表記必須

### 9.2 技術的制約
- 音声合成はローカルで実行（ネットワーク不要）
- 初回実行時はモデルダウンロードに時間がかかる可能性
- 音声再生はシステムのオーディオデバイスに依存

## 10. 今後の拡張案

### 10.1 機能拡張
- 複数キャラクターの選択機能
- 音声パラメータ調整（速度、音量、音程）
- 音声ファイルの保存機能

### 10.2 技術的改善
- キャッシュ機構の実装
- 音声合成の並列処理
- WebSocket経由のリアルタイム再生

## 11. 成功基準

- [ ] MCPサーバーとして正常に起動できる
- [ ] GitHub Copilot / Claude Desktopから呼び出せる
- [ ] テキストを音声合成して再生できる
- [ ] エラー時も適切にハンドリングできる
- [ ] 環境変数で音声スタイルを変更できる
- [ ] macOS環境で問題なく動作する
