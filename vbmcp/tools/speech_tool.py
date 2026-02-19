"""
Speechツール
テキストを音声合成して読み上げるMCPツール
"""

import asyncio
import logging
import os

from ..services.voicevox_service import VoicevoxService
from ..services.audio_service import AudioService

logger = logging.getLogger(__name__)


class SpeechTool:
    """音声読み上げツール"""

    def __init__(self) -> None:
        self._voicevox = VoicevoxService()
        self._audio = AudioService()

    async def speak(self, text: str, speaker_name: str | None = None) -> None:
        """テキストを音声合成して再生する（バックグラウンド実行）
        
        Args:
            text: 読み上げるテキスト
            speaker_name: 話者名（config.pyのSPEAKERSに定義されている名前）
                         省略時はデフォルト話者を使用
        """
        tmp_path: str | None = None
        try:
            logger.info(f"音声合成開始: '{text[:50]}{'...' if len(text) > 50 else ''}' (speaker_name={speaker_name})")

            # 音声合成して一時ファイルに保存
            tmp_path = await self._voicevox.synthesize_to_file(text, speaker_name)

            # 音声を再生
            await self._audio.play(tmp_path)

        except Exception as e:
            logger.error(f"音声読み上げエラー: {e}", exc_info=True)
        finally:
            # 一時ファイルを確実に削除
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    logger.debug(f"一時ファイルを削除しました: {tmp_path}")
                except Exception as e:
                    logger.warning(f"一時ファイルの削除に失敗しました: {tmp_path}: {e}")
