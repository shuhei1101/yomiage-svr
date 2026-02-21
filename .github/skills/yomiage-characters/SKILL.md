---
name: yukkuri-characters
description: 合成音声キャラクター（ずんだもん・四国めたん・春日部つむぎ）の設定を提供するスキル。セリフ生成・台本制作・キャラクター設定が必要な場合に使用する。
---

# Yukkuri Characters

## Overview

合成音声キャラクター（ずんだもん・四国めたん・春日部つむぎ）の包括的なキャラクター設定を提供する。

このスキルは、**汎用的なコア設定**と**プロジェクト固有設定**を分離して管理する。

## When to Use This Skill

以下の場合に参照する：
- 合成音声キャラクターのセリフを生成する
- 台本・脚本を作成する
- キャラクターの口調・性格を確認する
- 掛け合いパターンを参照する
- 新規プロジェクトでキャラクター設定を再利用する

## Usage

### 基本的な使い方

1. **汎用的な設定のみ必要な場合**（他プロジェクト）
   - `references/core/` 配下のファイルのみを参照する
   - `zundamon_core.md`, `metan_core.md`, `tsumugi_core.md`

2. **プロジェクト固有設定が必要な場合**（このプロジェクト）
   - `references/core/` と `references/project_specific/` 両方を参照する
   - `common.md`（キャラ関係性・バランス）も併せて参照

### 参照が必要なファイル選択ガイド

| タスク | 参照ファイル |
|--------|------------|
| ずんだもんの基本設定確認 | `references/core/zundamon_core.md` |
| ずんだもんのプロジェクト固有設定確認 | `references/project_specific/zundamon_narration.md` |
| キャラ間の掛け合いバランス | `references/project_specific/common.md` |
| 3キャラ全員の基本設定 | `references/core/` 配下全ファイル |
| プロジェクト固有の台本生成 | `references/core/` + `references/project_specific/` 全ファイル |

## Character Overview

| キャラ名 | コア設定ファイル | プロジェクト固有設定ファイル | 特徴 |
|---------|----------------|-------------------|------|
| ずんだもん | `core/zundamon_core.md` | `project_specific/zundamon_narration.md` | 語尾「〜のだ」、素直で感情的、メイン実況 |
| 四国めたん | `core/metan_core.md` | `project_specific/metan_narration.md` | 冷静お姉さん、ツッコミ・解説役 |
| 春日部つむぎ | `core/tsumugi_core.md` | `project_specific/tsumugi_narration.md` | 敬語で明るい、ポジティブ、賑やかし役 |

## References Structure

### `references/core/`
各キャラクターの**汎用的な設定**（他プロジェクトでも再利用可能）

- **含む内容**: 基本情報、口調・話し方、性格、感情表現、基本的な掛け合いパターン
- **含まない内容**: ゲーム実況固有の設定、プロジェクト固有の背景

### `references/project_specific/`
**プロジェクト固有の設定**（例: ゲーム実況プロジェクト）

- **含む内容**: プロジェクト特有の役割、背景設定、文化、掛け合いサンプル、キャラ関係性、シーン別推奨組み合わせ
- **依存**: `core/` の設定をベースにした拡張設定
- **カスタマイズ**: プロジェクトに応じて自由に作成・変更可能

## Best Practices

### セリフ生成時の注意点

1. **必ず該当キャラのコア設定を読み込む**
2. **プロジェクト固有設定がある場合、project_specific/ も読み込む**
3. **common.md でキャラ間バランスを確認する**
4. **例文の使い回し禁止**：サンプルはパターン例であり、毎回新しい表現を考える

### 複数キャラ登場時

- `common.md` の「複数キャラ登場時のバランス指針」「シーン別推奨組み合わせ」を参照
- 役割分担を守る（ずんだもん=主軸、めたん=締め役、つむぎ=賑やかし）

### 他プロジェクトでの再利用

- `references/core/` のみをコピーして使用
- プロジェクト固有設定は新たに作成（`project_specific/` をテンプレートとして参考可）
