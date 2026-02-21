# VOICEVOX MCP Server クイックスタート

## MCPサーバーモードで使う（AIエージェントから呼び出し）

### 前提条件
1. VOICEVOXアプリが起動している（`http://localhost:50021`）
2. Ollamaが起動している（口調変換を使う場合）

### 起動方法

#### VS Code + GitHub Copilot で使う

1. **VS Codeでワークスペースを開く**
   ```bash
   cd /path/to/yomiage-svr
   code .
   ```

2. **MCPサーバーが自動起動**  
   `.vscode/mcp.json` の設定により、GitHub Copilot が自動的にMCPサーバーを認識します。

3. **GitHub Copilot から呼び出し**  
   チャットで以下のように依頼：
   ```
   #speech タスクが完了しました、と読み上げて
   ```

#### Claude Desktop で使う

1. **設定ファイルを編集**
   ```bash
   # macOS
   vi ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **設定内容**
   ```json
   {
     "mcpServers": {
       "speech": {
         "command": "/path/to/yomiage-svr/venv/bin/python",
         "args": ["/path/to/yomiage-svr/mcp_server.py"],
         "cwd": "/path/to/yomiage-svr"
       }
     }
   }
   ```

3. **Claude Desktop を再起動**

4. **Claude から呼び出し**
   ```
   「処理が完了しました」をずんだもんの声で読み上げて
   ```

### 利用可能なツール

#### 1. speak - 音声合成＆読み上げ
```
パラメータ:
  text: 読み上げるテキスト
  speaker_name: 話者名（zundamon, tsumugi, metan）
  transform_tone: 口調変換の有無（デフォルト: true）

使用例:
  「実装が完了しました」をずんだもんで読み上げて
  「エラーが発生しています」を春日部つむぎの声で
```

#### 2. list_available_speakers - 話者一覧
```
利用可能なキャラクター一覧を取得

使用例:
  利用可能な話者を教えて
  どんなキャラクターの声が使える？
```

#### 3. transform_character_tone - 口調変換のみ
```
パラメータ:
  text: 変換するテキスト
  speaker_name: 話者名

使用例:
  「こんにちは」をずんだもん口調に変換して
  「タスクが完了しました」を春日部つむぎの口調で
```

### トラブルシューティング

#### ツールが認識されない
- VS Code / Claude Desktop を再起動
- `.vscode/mcp.json` のパスが正しいか確認
- `venv/bin/python` が存在するか確認

#### 音声が再生されない
- VOICEVOXアプリが起動しているか確認
- `http://localhost:50021` にアクセスできるか確認
- ログを確認: `tail -f /tmp/voicevox_mcp.log`（設定している場合）

#### 口調変換が動かない
- Ollamaが起動しているか確認: `ollama list`
- モデルがダウンロードされているか確認
- `vbmcp/config.py` の `OLLAMA_MODEL` 設定を確認

### HTTPサーバーと並行利用

MCPサーバーとHTTPサーバーは同時に起動できます：

```bash
# ターミナル1: HTTPサーバー起動
./start_server.sh

# ターミナル2: MCPサーバーは自動起動（または手動起動）
python mcp_server.py
```

- **HTTPサーバー**: curl/Pythonから呼び出し
- **MCPサーバー**: AIエージェントから呼び出し

どちらも同じ音声合成エンジンを共有するため、機能は同等です。

### 次のステップ

- [README.md](README.md) - 全体のドキュメント
- [QUICKSTART.md](QUICKSTART.md) - HTTPサーバーのクイックスタート
- `.github/agents/voicevox-mcp-developer.agent.md` - 開発用カスタムエージェント
