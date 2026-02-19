# MCP設定ガイド

このMCPサーバーを使用するための設定方法を説明します。

## 前提条件

- VOICEVOXアプリがインストールされ、起動していること（デフォルト: `http://localhost:50021`）
- このプロジェクトが `/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/` にインストールされていること

## 設定方法

### 方法1: Claude Desktop（グローバル設定）**推奨**

すべてのClaude Desktop会話で音声合成を使えるようにします。

#### 設定ファイルの場所
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### 設定内容
以下を追加してください：

```json
{
  "servers": {
    "NotifyAgentAct": {
      "command": "/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/venv/bin/python",
      "args": ["/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/server.py"],
      "env": {
        "VOICEVOX_BASE_URL": "http://localhost:50021"
      }
    }
  }
}
```

#### 設定後
1. Claude Desktopを再起動
2. 新しい会話で「こんにちは」と #Speech して」と入力
3. ずんだもんの声で読み上げが開始されます

---

### 方法2: VS Code（プロジェクトごと）

特定のプロジェクトでのみ使用する場合。

#### 設定ファイルの場所
プロジェクトルートに `.vscode/mcp.json` を作成

#### 設定内容
```json
{
  "servers": {
    "NotifyAgentAct": {
      "type": "stdio",
      "command": "/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/venv/bin/python",
      "args": ["/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/server.py"],
      "cwd": "/Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp",
      "env": {
        "VOICEVOX_BASE_URL": "http://localhost:50021"
      }
    }
  }
}
```

---

### 方法3: 別の場所にインストールした場合

インストール先が異なる場合は、上記のパスを適宜変更してください。

例: `~/mcp-servers/voicebox-mcp/` にインストールした場合

```json
{
  "servers": {
    "NotifyAgentAct": {
      "command": "/Users/あなたのユーザー名/mcp-servers/voicebox-mcp/venv/bin/python",
      "args": ["/Users/あなたのユーザー名/mcp-servers/voicebox-mcp/server.py"],
      "env": {
        "VOICEVOX_BASE_URL": "http://localhost:50021"
      }
    }
  }
}
```

---

## 使用方法

### 基本的な使い方

```
「こんにちは」と #Speech で言って
```

### 話者を指定

```
「こんにちは」を zundamon_tsun で #Speech して
```

### 利用可能な話者

- `zundamon` - ずんだもん（ノーマル）
- `zundamon_sweet` - ずんだもん（あまあま）
- `zundamon_tsun` - ずんだもん（ツンツン）
- `tsumugi` - 春日部つむぎ（速度1.3倍）
- `hau` - 雨晴はう
- `metan` - 四国めたん（ノーマル）
- `metan_sweet` - 四国めたん（あまあま）

---

## カスタマイズ

### 話者の設定を変更

`vbmcp/config.py` の `SPEAKERS` 辞書で話者の速度などを変更できます。

```python
"zundamon": VoiceSpeaker(
    id=1,
    name="ずんだもん",
    style="ノーマル",
    speed_scale=1.2,  # ← 速度を変更
),
```

### デフォルト話者を変更

`.env` ファイルを作成：

```bash
DEFAULT_SPEAKER=tsumugi
```

---

## トラブルシューティング

### 音声が再生されない

1. VOICEVOXアプリが起動しているか確認
2. `http://localhost:50021` にアクセスして接続確認
3. オーディオデバイスが正しく設定されているか確認

### MCPサーバーが認識されない

1. Claude Desktop / VS Codeを再起動
2. 設定ファイルのパスが正しいか確認
3. JSON構文エラーがないか確認

### パーミッションエラー

```bash
chmod +x /Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp/venv/bin/python
```

---

## ライセンスとクレジット

音声合成時は「VOICEVOX:ずんだもん」等のクレジット表記が必要です。
詳細はVOICEVOX利用規約を参照してください。
