"""
VoiceBox基本クラス定義

音声合成システムで使用する基本的なデータクラスを定義します。
循環インポートを回避するため、このファイルは他のモジュールから独立しています。
"""

from dataclasses import dataclass


@dataclass
class VoiceSpeaker:
    """話者設定クラス"""
    id: int           # 話者ID（VOICEVOXのスタイルID）
    name: str         # 話者名（表示用）
    style: str        # 話し方（ノーマル、ツンツン、など）
    speed_scale: float = 1.15  # 話す速度（0.5〜2.0）
    tone_prompt: str = ""  # Ollama用の口調変換プロンプト

    def __str__(self) -> str:
        return f"{self.name}（{self.style}）"
