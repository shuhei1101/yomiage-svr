#!/usr/bin/env python3
"""
Ollama口調変換 精度テスト

APIサーバーを介さず、Ollamaサーバーに直接リクエストして
各キャラクターの口調変換の精度を評価します。

config.pyのSPEAKERS定義とOllamaServiceを使用します。

使い方:
    # 全キャラクターをテスト
    python test/ollama_test.py

    # 結果をファイルに保存
    python test/ollama_test.py --save

    # 特定のキャラクターのみテスト
    python test/ollama_test.py --character zundamon
"""

import argparse
import os
import sys
import time
from typing import Dict, List

# vbmcp モジュールから設定とサービスをインポート
from vbmcp.config import SPEAKERS
from vbmcp.services.ollama_service import OllamaService

# ==================== 設定 ====================

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma2:2b"
TIMEOUT = 15  # 秒

# テストケース（入力テキスト）
TEST_CASES = [
    "タスクが完了しました",
    "エラーが発生しています",
    "これで問題ありません",
    "確認してください",
    "お疲れ様です",
    "どうしたらいいですか",
    "プログラミングは楽しいです",
    "ファイルの作成が完了しました",
    "接続に失敗しました",
    "テストを実行します",
]

# キャラクター別の期待出力と評価基準
CHARACTER_EVALUATION_RULES = {
    "tsumugi": {
        "expected_outputs": [
            "タスクが完了しました！あーし、嬉しいです！",
            "エラーが発生してるみたいです！あーしが一緒に確認します！",
            "これで大丈夫です！完璧じゃないですか！",
            "確認してもらえますか？",
            "お疲れ様です！あーしが何でもお手伝いします！",
            "どうしたらいいですか？あーしが一緒に考えます！",
            "プログラミングは楽しいです！あーしも大好きです！",
            "ファイルの作成が完了しました！よかったです！",
            "接続に失敗しちゃいました。でもあーしが原因を調べます！",
            "テストを実行しても大丈夫ですか？",
        ],
        "required_patterns": ["です", "ます", "ですか"],  # 敬語表現（「ですよ」「ますね」は禁止）
        "forbidden_patterns": ["のだ", "なのだ", "わね", "わよ", "ですよ", "ますよ", "ますね", "ですね", "よ！", "ね！", "よ。", "ね。"],  # 他キャラの語尾 + 禁止語尾
        "pronoun_check": {
            "expected": "あーし",
            "forbidden": ["ボク", "僕", "わたくし", "俺"]
        },
        "tone_keywords": ["優しい", "丁寧", "柔らかい"],
    },
    "zundamon": {
        "expected_outputs": [
            "タスクが完了したのだ！",
            "エラーが発生してる！確認してほしいのだ！",
            "これで問題ないのだ！",
            "確認してほしいのだ！",
            "お疲れ様なのだ！",
            "どうしたらいいか教えてほしいのだ！",
            "プログラミングは楽しいのだ！",
            "ファイルの作成が完了したのだ！",
            "接続に失敗したのだ！",
            "テストを実行するのだ！",
        ],
        "required_patterns": ["のだ", "なのだ"],
        "forbidden_patterns": ["です", "ます"],
        "pronoun_check": {
            "expected": "ボク",
            "forbidden": ["私", "わたくし", "俺"]
        },
        "tone_keywords": ["明るい", "元気", "フレンドリー"],
    },
    "metan": {
        "expected_outputs": [
            "できたわ。見てちょうだい。",
            "ちょっと待って。エラーが出てるわ。",
            "これで、問題ないわ。",
            "確認してもらえるかしら。",
            "お疲れ様。",  # シンプルな挨拶（語尾チェックスキップ）
            "どうしたらいいかしら。",
            "プログラミングは楽しいわ。",
            "ファイルができたわ。",
            "接続に失敗したわ。",
            "テストを実行するわ。",
        ],
        "required_patterns": ["わ", "かしら", "でしょ"],  # めたんの語尾（「わ」が基本）
        "forbidden_patterns": ["のだ", "なのだ", "です", "ます", "わね", "わよ", "よ。"],  # 他キャラの語尾 + 禁止語尾
        "skip_pattern_check_indexes": [4],  # インデックス（テストケース5="お疲れ様です"）でパターンチェックをスキップ
        "pronoun_check": {
            "expected": "わたし",  # または省略
            "forbidden": ["ボク", "僕", "あーし"]
        },
        "tone_keywords": ["カジュアル", "フレンドリー", "親しみやすい"],
    },
}


# ==================== ヘルパー関数 ====================

def check_ollama_server(ollama_service: OllamaService) -> bool:
    """Ollamaサーバーの起動確認"""
    import requests
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        print("✅ Ollamaサーバー: 起動中")
        print(f"   利用可能なモデル: {', '.join(model_names)}")
        
        if OLLAMA_MODEL not in model_names:
            print(f"⚠️  モデル {OLLAMA_MODEL} が見つかりません")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Ollamaサーバー: 起動していません - {e}")
        return False


def check_patterns(text: str, required: List[str], forbidden: List[str]) -> Dict:
    """パターンチェックを実行"""
    # required: いずれか1つ以上含まれていればOK
    matched_required = [p for p in required if p in text]
    has_required = len(matched_required) > 0
    
    # forbidden: すべて含まれていなければOK
    found_forbidden = [p for p in forbidden if p in text]
    
    return {
        "has_required": has_required,
        "matched_required": matched_required,
        "found_forbidden": found_forbidden,
    }


def check_pronoun(text: str, expected: str, forbidden: List[str]) -> Dict:
    """一人称チェックを実行"""
    has_expected = expected in text
    found_forbidden = [p for p in forbidden if p in text]
    return {
        "has_expected": has_expected,
        "found_forbidden": found_forbidden,
    }


def evaluate_result(
    actual: str,
    input_text: str,
    expected: str,
    rules: Dict,
    original_text: str,
    test_index: int = -1
) -> Dict:
    """1件の変換結果を評価する
    
    Args:
        test_index: テストケースのインデックス（0始まり）、skip_pattern_check_indexesと比較
    """
    result = {
        "input": input_text,
        "expected": expected,
        "original": original_text,
        "actual": actual,
        "exact_match": actual.strip() == expected.strip(),
        "issues": [],
        "score": 0.0,
        "processing_time": 0.0,
    }

    # パターンチェックをスキップするか確認
    skip_pattern_check = test_index in rules.get("skip_pattern_check_indexes", [])
    
    # パターンチェック
    if not skip_pattern_check:
        pattern_result = check_patterns(
            actual,
            rules["required_patterns"],
            rules["forbidden_patterns"],
        )
        
        if not pattern_result["has_required"]:
            result["issues"].append(
                f"必須パターン不足: {rules['required_patterns']} のいずれも含まれていない"
            )
        if pattern_result["found_forbidden"]:
            result["issues"].append(
                f"禁止パターン検出: {pattern_result['found_forbidden']}"
            )
    else:
        # パターンチェックスキップ時はダミー結果
        pattern_result = {
            "has_required": True,
            "matched_required": [],
            "found_forbidden": [],
        }

    # 一人称チェック（一人称が含まれるケースのみ）
    if "pronoun_check" in rules:
        pronoun_config = rules["pronoun_check"]
        if any(p in original_text for p in ["私", "僕", "俺", "ボク"]):
            pronoun_result = check_pronoun(
                actual, pronoun_config["expected"], pronoun_config["forbidden"]
            )
            if not pronoun_result["has_expected"] and pronoun_config["expected"] != "":
                result["issues"].append(
                    f"一人称未変換: 「{pronoun_config['expected']}」が見つからない"
                )
            if pronoun_result["found_forbidden"]:
                result["issues"].append(
                    f"禁止一人称検出: {pronoun_result['found_forbidden']}"
                )

    # スコア計算
    if result["exact_match"]:
        # 完全一致なら満点
        score = 1.0
    else:
        # 部分的な評価
        score = 1.0
        
        # パターンチェック結果でスコアを調整
        if not pattern_result["has_required"]:
            score -= 0.3
        if pattern_result["found_forbidden"]:
            score -= 0.2 * len(pattern_result["found_forbidden"])
        
        # 一人称チェック
        if "pronoun_check" in rules and any(p in original_text for p in ["私", "僕", "俺", "ボク"]):
            pronoun_result = check_pronoun(
                actual, rules["pronoun_check"]["expected"], rules["pronoun_check"]["forbidden"]
            )
            if not pronoun_result["has_expected"]:
                score -= 0.1
            if pronoun_result["found_forbidden"]:
                score -= 0.1 * len(pronoun_result["found_forbidden"])
        
        score = max(0.0, min(1.0, score))
    
    result["score"] = score
    
    return result


def print_separator(char="=", length=70):
    """区切り線を表示"""
    print(char * length)


# ==================== メインテスト ====================

def run_character_test(
    char_id: str,
    speaker,
    ollama_service: OllamaService,
    rules: Dict
) -> List[Dict]:
    """特定のキャラクターのテストを実行"""
    char_name = speaker.name
    tone_prompt = speaker.tone_prompt
    expected_outputs = rules.get("expected_outputs", [])
    
    print_separator("=")
    print(f"🎭 {char_name} ({char_id})")
    print(f"   スタイル: {speaker.style}")
    print(f"   話者ID: {speaker.id}")
    print(f"   評価基準: 必須パターン={rules['required_patterns']}, 禁止パターン={rules['forbidden_patterns']}")
    print_separator("=")
    print()
    
    results = []
    
    for i, test_text in enumerate(TEST_CASES, 1):
        expected = expected_outputs[i-1] if i-1 < len(expected_outputs) else ""
        
        print(f"テストケース {i}/{len(TEST_CASES)}")
        print("-" * 70)
        print(f"📝 入力: {test_text}")
        if expected:
            print(f"💭 期待: {expected}")
        
        # 時間計測開始
        start_time = time.time()
        
        # OllamaServiceで変換実行
        transformed = ollama_service.transform_text(test_text, tone_prompt)
        
        # 処理時間
        elapsed = time.time() - start_time
        
        print(f"🗣️  結果: {transformed}")
        print(f"⏱️  処理時間: {elapsed:.2f}秒")
        
        # 結果評価
        eval_result = evaluate_result(transformed, test_text, expected, rules, test_text, test_index=i-1)
        eval_result["processing_time"] = elapsed
        results.append(eval_result)
        
        # 結果表示
        if eval_result["exact_match"]:
            print(f"✅ 完全一致！")
        elif eval_result["score"] >= 0.9:
            print(f"✅ 優秀 (スコア: {eval_result['score']:.1%})")
        elif eval_result["score"] >= 0.7:
            print(f"⚠️  良好 (スコア: {eval_result['score']:.1%})")
        else:
            print(f"❌ 要改善 (スコア: {eval_result['score']:.1%})")
        
        if eval_result["issues"]:
            for issue in eval_result["issues"]:
                print(f"   ⚠️  {issue}")
        
        print()
    
    return results


def print_summary(char_name: str, results: List[Dict]):
    """結果サマリーを表示"""
    print_separator("=")
    print(f"📊 {char_name} - テスト結果サマリー")
    print_separator("=")
    
    total = len(results)
    exact_match_count = sum(1 for r in results if r["exact_match"])
    excellent_count = sum(1 for r in results if r["score"] >= 0.9)
    good_count = sum(1 for r in results if r["score"] >= 0.7)
    issue_free_count = sum(1 for r in results if not r["issues"])
    avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
    avg_time = sum(r["processing_time"] for r in results) / total if total > 0 else 0
    
    print(f"総テスト数:     {total}")
    print(f"完全一致:       {exact_match_count} ({exact_match_count/total*100:.1f}%)")
    print(f"優秀 (≥90%):    {excellent_count} ({excellent_count/total*100:.1f}%)")
    print(f"良好 (≥70%):    {good_count} ({good_count/total*100:.1f}%)")
    print(f"問題なし:       {issue_free_count} ({issue_free_count/total*100:.1f}%)")
    print(f"平均スコア:     {avg_score:.1%}")
    print(f"平均処理時間:   {avg_time:.2f}秒")
    print()
    
    # 問題があったケースの詳細
    problem_results = [r for r in results if r["issues"]]
    if problem_results:
        print_separator("-")
        print("⚠️  問題があったケース:")
        print_separator("-")
        for i, r in enumerate(problem_results, 1):
            print(f"\n{i}. 入力: {r['input']}")
            if r.get("expected"):
                print(f"   期待: {r['expected']}")
            print(f"   結果: {r['actual']}")
            print(f"   スコア: {r['score']:.1%}")
            for issue in r["issues"]:
                print(f"   問題: {issue}")
    else:
        print("🎉 全テストケースで問題なし！")
    
    print()


def save_results_to_file(char_id: str, char_name: str, results: List[Dict], output_dir: str = "test"):
    """結果をファイルに保存"""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"ollama_test_result_{char_id}.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Ollama口調変換 精度テスト結果 - {char_name} ({char_id})\n")
        f.write(f"モデル: {OLLAMA_MODEL}\n")
        f.write(f"日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        total = len(results)
        exact_match_count = sum(1 for r in results if r["exact_match"])
        excellent_count = sum(1 for r in results if r["score"] >= 0.9)
        good_count = sum(1 for r in results if r["score"] >= 0.7)
        issue_free_count = sum(1 for r in results if not r["issues"])
        avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
        avg_time = sum(r["processing_time"] for r in results) / total if total > 0 else 0
        
        f.write(f"総テスト数: {total}\n")
        f.write(f"完全一致: {exact_match_count} ({exact_match_count/total*100:.1f}%)\n")
        f.write(f"優秀 (≥90%): {excellent_count} ({excellent_count/total*100:.1f}%)\n")
        f.write(f"良好 (≥70%): {good_count} ({good_count/total*100:.1f}%)\n")
        f.write(f"問題なし: {issue_free_count} ({issue_free_count/total*100:.1f}%)\n")
        f.write(f"平均スコア: {avg_score:.1%}\n")
        f.write(f"平均処理時間: {avg_time:.2f}秒\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("詳細結果\n")
        f.write("=" * 70 + "\n\n")
        
        for i, r in enumerate(results, 1):
            status = "✅" if r["exact_match"] else ("🌟" if r["score"] >= 0.9 else ("⚠️" if r["score"] >= 0.7 else "❌"))
            f.write(f"テスト {i}: {status}\n")
            f.write(f"  入力: {r['input']}\n")
            if r.get("expected"):
                f.write(f"  期待: {r['expected']}\n")
            f.write(f"  結果: {r['actual']}\n")
            f.write(f"  スコア: {r['score']:.1%}\n")
            if r["exact_match"]:
                f.write(f"  完全一致: はい\n")
            f.write(f"  処理時間: {r['processing_time']:.2f}秒\n")
            if r["issues"]:
                for issue in r["issues"]:
                    f.write(f"  問題: {issue}\n")
            f.write("\n")
    
    print(f"✅ 結果を保存しました: {output_file}")


def main():
    """メインテスト実行"""
    parser = argparse.ArgumentParser(
        description="Ollama口調変換の精度テストを実行"
    )
    parser.add_argument(
        "--character", "-c",
        default=None,
        help="テスト対象のキャラクターID (例: zundamon, tsumugi, metan)"
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="結果をファイルに保存する"
    )
    args = parser.parse_args()
    
    print_separator()
    print("🎤 Ollama口調変換 精度テスト")
    print(f"   モデル: {OLLAMA_MODEL}")
    print_separator()
    print()
    
    # OllamaServiceを初期化
    ollama_service = OllamaService(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    
    # 事前確認
    print("📋 事前確認")
    print("-" * 70)
    if not check_ollama_server(ollama_service):
        print("\n❌ Ollamaサーバーが起動していません。終了します。")
        sys.exit(1)
    print(f"✅ OllamaService初期化完了")
    print()
    
    # テスト対象のキャラクターを決定
    if args.character:
        if args.character not in SPEAKERS:
            print(f"❌ キャラクター '{args.character}' が見つかりません")
            print(f"   利用可能: {', '.join(SPEAKERS.keys())}")
            sys.exit(1)
        test_characters = [args.character]
    else:
        test_characters = list(SPEAKERS.keys())
    
    # 各キャラクターでテスト実行
    all_results = {}
    
    for char_id in test_characters:
        if char_id not in CHARACTER_EVALUATION_RULES:
            print(f"⚠️  {char_id} の評価ルールが未定義 - スキップします")
            continue
        
        speaker = SPEAKERS[char_id]
        rules = CHARACTER_EVALUATION_RULES[char_id]
        
        results = run_character_test(char_id, speaker, ollama_service, rules)
        all_results[char_id] = results
        
        print_summary(speaker.name, results)
        
        if args.save:
            save_results_to_file(char_id, speaker.name, results)
        
        print()
    
    # 総合結果
    if len(test_characters) > 1:
        print_separator("=")
        print("🏆 総合結果")
        print_separator("=")
        
        for char_id in test_characters:
            if char_id not in all_results:
                continue
            results = all_results[char_id]
            exact_match = sum(1 for r in results if r["exact_match"])
            avg_score = sum(r["score"] for r in results) / len(results)
            issue_free = sum(1 for r in results if not r["issues"])
            
            print(f"{SPEAKERS[char_id].name:12s}: 完全一致 {exact_match}/{len(results)}, 平均スコア {avg_score:.1%}, 問題なし {issue_free}/{len(results)}")
        
        print_separator("=")


if __name__ == "__main__":
    main()
