"""
VOICEVOX 話者設定

このファイルでは音声合成に使用する話者（キャラクター）の設定を管理します。
"""

from dataclasses import dataclass
import os


@dataclass
class VoiceSpeaker:
    """話者設定クラス"""
    id: int           # 話者ID（VOICEVOXのスタイルID）
    name: str         # 話者名（表示用）
    style: str        # 話し方（ノーマル、ツンツン、など）
    speed_scale: float = 1.2  # 話す速度（0.5〜2.0）

    def __str__(self) -> str:
        return f"{self.name}（{self.style}）"


# デフォルト話者設定
SPEAKERS = {
    "zundamon": VoiceSpeaker(
        id=1,
        name="ずんだもん",
        style="ノーマル",
        speed_scale=1.2,
    ),
    "tsumugi": VoiceSpeaker(
        id=8,
        name="春日部つむぎ",
        style="ノーマル",
        speed_scale=1.2,
    ),
    "metan": VoiceSpeaker(
        id=2,
        name="四国めたん",
        style="ノーマル",
        speed_scale=1.2,
    ),
}

# デフォルト話者（環境変数で上書き可能）
DEFAULT_SPEAKER_NAME = os.getenv("DEFAULT_SPEAKER", "zundamon")

# VOICEVOX サーバー設定（環境変数のみから取得）
VOICEVOX_BASE_URL = os.getenv("VOICEVOX_BASE_URL", "http://localhost:50021")


def get_speaker(name: str | None = None) -> VoiceSpeaker:
    """話者設定を取得する
    
    Args:
        name: 話者名（省略時はデフォルト話者）
    
    Returns:
        VoiceSpeaker: 話者設定
    
    Raises:
        ValueError: 存在しない話者名が指定された場合
    """
    if name is None:
        name = DEFAULT_SPEAKER_NAME
    
    if name not in SPEAKERS:
        available = ", ".join(SPEAKERS.keys())
        raise ValueError(f"話者 '{name}' が見つかりません。利用可能な話者: {available}")
    
    return SPEAKERS[name]


def list_speakers() -> list[str]:
    """利用可能な話者名のリストを返す"""
    return list(SPEAKERS.keys())
