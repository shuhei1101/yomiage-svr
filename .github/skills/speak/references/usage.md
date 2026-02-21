# 音声合成スキル - 詳細使用例

## HTTP API直接呼び出し

```python
import requests

# 自動選択 + 口調変換
requests.post("http://127.0.0.1:8767/speech", json={"text": "タスクが完了しました"})

# 話者指定 + 口調変換
requests.post("http://127.0.0.1:8767/speech", json={"text": "完了", "speaker_name": "tsumugi"})

# 口調変換なし
requests.post("http://127.0.0.1:8767/speech", json={"text": "完了なのだ", "speaker_name": "zundamon", "transform_tone": False})
```

## Python内から実行

```python
import subprocess
import sys

script = ".github/skills/speak/scripts/speak.py"

# 基本
subprocess.run([sys.executable, script, "処理完了"])

# 話者指定
subprocess.run([sys.executable, script, "処理完了", "-s", "tsumugi"])

# 口調変換なし
subprocess.run([sys.executable, script, "完了なのだ", "-s", "zundamon", "--no-transform"])
```

## 複数回に分けて通知

```python
import subprocess
import time

script = ".github/skills/speak/scripts/speak.py"

subprocess.run(["python", script, "セリフ生成が完了しました"])
time.sleep(1)
subprocess.run(["python", script, "チェックに進んでも大丈夫ですか？"])
```
