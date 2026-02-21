"""
VoiceSpeaker統合モジュール

全キャラクターの設定を統合的に管理し、動的な取得機能を提供します。
新しいキャラクターを追加する際は、このモジュールに登録するだけで自動的に利用可能になります。
"""

from typing import Dict, List
from ..base import VoiceSpeaker
from .zundamon import get_zundamon_speaker
from .tsumugi import get_tsumugi_speaker
from .metan import get_metan_speaker


def get_all_speakers() -> Dict[str, VoiceSpeaker]:
    """
    全てのキャラクター設定を取得
    
    Returns:
        Dict[str, VoiceSpeaker]: キャラクター名をキーとした設定辞書
    """
    return {
        "zundamon": get_zundamon_speaker(),
        "tsumugi": get_tsumugi_speaker(),
        "metan": get_metan_speaker(),
    }


def get_speaker_names() -> List[str]:
    """
    利用可能なキャラクター名の一覧を取得
    
    Returns:
        List[str]: キャラクター名のリスト
    """
    return list(get_all_speakers().keys())


def get_speaker_by_name(name: str) -> VoiceSpeaker:
    """
    指定されたキャラクター名の設定を取得
    
    Args:
        name: キャラクター名
        
    Returns:
        VoiceSpeaker: キャラクター設定
        
    Raises:
        ValueError: 存在しないキャラクター名が指定された場合
    """
    speakers = get_all_speakers()
    if name not in speakers:
        available = ", ".join(speakers.keys())
        raise ValueError(f"キャラクター '{name}' が見つかりません。利用可能なキャラクター: {available}")
    
    return speakers[name]


def display_speaker_info(name: str) -> str:
    """
    キャラクター情報を表示用文字列で取得
    
    Args:
        name: キャラクター名
        
    Returns:
        str: 表示用のキャラクター情報
    """
    try:
        speaker = get_speaker_by_name(name)
        return f"🎤 {speaker.name} ({speaker.style}) - ID:{speaker.id}, 速度:{speaker.speed_scale}"
    except ValueError as e:
        return f"❌ エラー: {e}"


# モジュール読み込み時の確認用
if __name__ == "__main__":
    print("📋 利用可能なキャラクター:")
    for name in get_speaker_names():
        print(f"  - {display_speaker_info(name)}")
