#!/usr/bin/env python3
"""
VoiceBox API 音声合成スクリプト

VoiceBox APIサーバーに音声合成リクエストを送信します。
Copilotスキルから実行される想定のスクリプトです。
"""

import sys
import requests
from typing import Optional


VOICEBOX_API_URL = "http://127.0.0.1:8767"


def speak(text: str, speaker_name: Optional[str] = None, transform_tone: bool = True) -> bool:
    """
    テキストを音声合成して読み上げる
    
    Args:
        text: 読み上げるテキスト
        speaker_name: 話者名（省略時は自動選択）
        transform_tone: 口調変換の有無（True: Ollamaで変換, False: 元のまま）
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        url = f"{VOICEBOX_API_URL}/speech"
        payload = {
            "text": text,
            "transform_tone": transform_tone
        }
        
        if speaker_name:
            payload["speaker_name"] = speaker_name
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        print(f"✓ 音声合成リクエスト送信: {result.get('message', 'OK')}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️  VoiceBox APIサーバーに接続できません", file=sys.stderr)
        print("   サーバーが起動しているか確認してください: ./start_server.sh", file=sys.stderr)
        return False
        
    except requests.exceptions.Timeout:
        print("⚠️  リクエストがタイムアウトしました", file=sys.stderr)
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  リクエストエラー: {e}", file=sys.stderr)
        return False


def get_speakers() -> Optional[dict]:
    """
    利用可能な話者一覧を取得
    
    Returns:
        dict: 話者情報、失敗時None
    """
    try:
        url = f"{VOICEBOX_API_URL}/speakers"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  話者一覧の取得に失敗: {e}", file=sys.stderr)
        return None


def main():
    """コマンドライン実行用のメイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VoiceBox API 音声合成スクリプト"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="読み上げるテキスト"
    )
    parser.add_argument(
        "-s", "--speaker",
        help="話者名（zundamon, tsumugi, metan）"
    )
    parser.add_argument(
        "--no-transform",
        action="store_true",
        help="口調変換を無効化（元のテキストのまま読み上げ）"
    )
    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="利用可能な話者一覧を表示"
    )
    
    args = parser.parse_args()
    
    # 話者一覧表示
    if args.list_speakers:
        speakers = get_speakers()
        if speakers:
            print("利用可能な話者:")
            for name, info in speakers.items():
                print(f"  - {name}: {info['display_name']} (速度: {info['speed_scale']})")
        return
    
    # テキストが指定されていない場合はヘルプを表示
    if not args.text:
        parser.print_help()
        return
    
    # 音声合成実行
    transform_tone = not args.no_transform  # --no-transformがあればFalse
    success = speak(args.text, args.speaker, transform_tone)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
