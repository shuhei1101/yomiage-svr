# VoiceBox API Server - クイックスタートガイド

## 🚀 5分で始める

### 1. VOICEVOXアプリを起動

[VOICEVOX公式サイト](https://voicevox.hiroshiba.jp/)からアプリをダウンロードして起動

### 2. サーバーを起動

```bash
cd /Users/nishikawashuhei/nishikawa/30_repos/voicebox-mcp
./start_server.sh
```

起動メッセージが表示されたら成功です：
```
INFO:     Uvicorn running on http://127.0.0.1:8767
```

### 3. 動作確認

別のターミナルを開いて：

```bash
# ヘルスチェック
curl http://127.0.0.1:8767/health

# 音声合成テスト
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは、音声合成のテストです"}'
```

音声が再生されれば成功です！🎉

## 📝 他のプロジェクトから使う

### Python

```python
import requests

def speak(text: str):
    requests.post(
        "http://127.0.0.1:8767/speech",
        json={"text": text}
    )

speak("処理が完了しました")
```

### JavaScript/Node.js

```javascript
async function speak(text) {
    await fetch('http://127.0.0.1:8767/speech', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
    });
}

speak('処理が完了しました');
```

### Bash/Shell

```bash
function speak() {
    curl -s -X POST http://127.0.0.1:8767/speech \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$1\"}"
}

speak "ビルドが完了しました"
```

## 🎭 話者を変更する

```bash
# ずんだもん
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちはなのだ", "speaker_name": "zundamon"}'

# 春日部つむぎ
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "speaker_name": "tsumugi"}'

# 四国めたん
curl -X POST http://127.0.0.1:8767/speech \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "speaker_name": "metan"}'
```

## 🛠️ トラブルシューティング

### 音声が再生されない

1. VOICEVOXアプリが起動しているか確認
   ```bash
   curl http://localhost:50021/version
   ```

2. オーディオデバイスが正しく設定されているか確認

### サーバーが起動しない

1. ポート8767が使用中でないか確認
   ```bash
   lsof -i :8767
   ```

2. Python仮想環境がアクティブか確認
   ```bash
   which python
   # → .../voicebox-mcp/venv/bin/python である必要がある
   ```

## 📚 詳細ドキュメント

- [README.md](README.md) - 完全なドキュメント
- [client_example.py](client_example.py) - Pythonクライアント例
- API仕様: `http://127.0.0.1:8767/docs` (サーバー起動後にブラウザでアクセス)
