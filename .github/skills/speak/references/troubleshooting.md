# トラブルシューティング

## 音声が再生されない

### VoiceBox APIサーバー確認
```bash
curl http://127.0.0.1:8767/health
```

### VOICEVOXアプリ確認
```bash
curl http://localhost:50021/version
```

## スクリプトがエラーになる

### requests インストール確認
```bash
pip install requests
```

### Pythonバージョン確認（3.9以上推奨）
```bash
python --version
```

## Ollama口調変換が動かない

### Ollamaサーバー確認
```bash
curl http://localhost:11434/api/tags
```

### gemma2:2b モデル確認
```bash
ollama list | grep gemma2:2b
```

モデルがない場合：
```bash
ollama pull gemma2:2b
```
