---
name: speak
description: 音声合成スキル（Ollama口調変換対応）。テキストをキャラクターボイスで読み上げる。
---

# 音声合成スキル

テキストをキャラクターボイスで音声合成。Ollama連携で自動的にキャラクター口調に変換。

**前提**: VoiceBox APIサーバー起動済み（`http://127.0.0.1:8767`）

---

## 使い方

```python
import subprocess

script = ".github/skills/speak/scripts/speak.sh"

# デフォルト（自動選択 + Ollama口調変換）
subprocess.run([script, "タスクが完了しました"])

# 話者指定
subprocess.run([script, "完了", "--speaker", "tsumugi"])

# 口調変換なし
subprocess.run([script, "完了なのだ", "-s", "zundamon", "--no-transform"])
```

---

## 話者

| 話者名 | キャラクター | 特徴 |
|--------|------------|------|
| `zundamon` | ずんだもん | 語尾「のだ」 |
| `tsumugi` | 春日部つむぎ | 丁寧・優しい |
| `metan` | 四国めたん | カジュアル |

**Ollama口調変換例** (デフォルト有効):
- 入力: "タスクが完了しました"
- つむぎ: "タスクが完了しましたよ。お疲れ様でした！"
- ずんだもん: "タスクが完了したのだ！"
- めたん: "できたよ！見てみて！"

**キャラクター詳細**: `references/character_*.md`

---

## 推奨タイミング

- タスク完了時
- ユーザーへの質問前
- エラー・警告検出時
- 進捗報告

---

## リファレンス

- **詳細な使用例**: `references/usage.md`
- **トラブルシューティング**: `references/troubleshooting.md`
- **キャラクター設定**: `references/`
