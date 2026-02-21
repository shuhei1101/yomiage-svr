"""
VOICEVOX音声合成サービス
VOICEVOXローカルサーバーのHTTP APIを使用してテキストを音声合成する

事前にVOICEVOXアプリを起動しておく必要があります。
デフォルトでは http://localhost:50021 でAPIサーバーが動作します。
"""

import asyncio
import logging
import os
import tempfile

import requests

from ..config import VOICEVOX_BASE_URL, get_speaker, VoiceSpeaker

logger = logging.getLogger(__name__)


class VoicevoxService:
    """VOICEVOX HTTP API を使った音声合成サービス"""

    def __init__(self) -> None:
        self._base_url: str = VOICEVOX_BASE_URL
        self._default_speaker: VoiceSpeaker = get_speaker()  # デフォルト話者を取得

    def _audio_query(self, text: str, speaker_id: int, speed_scale: float) -> dict:
        """テキストから音声合成クエリを作成する"""
        resp = requests.post(
            f"{self._base_url}/audio_query",
            params={"text": text, "speaker": speaker_id},
        )
        resp.raise_for_status()
        query = resp.json()
        query["speedScale"] = speed_scale
        return query

    def _synthesis(self, query: dict, speaker_id: int) -> bytes:
        """クエリから音声データ（WAVバイト列）を生成する"""
        resp = requests.post(
            f"{self._base_url}/synthesis",
            params={"speaker": speaker_id},
            json=query,
        )
        resp.raise_for_status()
        return resp.content

    async def synthesize(self, text: str, speaker_name: str | None = None) -> bytes:
        """テキストを音声合成してWAVバイト列を返す
        
        Args:
            text: 音声合成するテキスト
            speaker_name: 話者名（config.pyのSPEAKERSに定義されている名前）
                         省略時はデフォルト話者を使用
        
        Returns:
            WAVバイト列
        """
        # 話者設定を取得
        speaker = get_speaker(speaker_name) if speaker_name else self._default_speaker
        
        logger.info(f"音声合成中 ({speaker}, speed={speaker.speed_scale}): '{text[:30]}{'...' if len(text) > 30 else ''}'")

        loop = asyncio.get_event_loop()
        query = await loop.run_in_executor(None, self._audio_query, text, speaker.id, speaker.speed_scale)
        wav_bytes = await loop.run_in_executor(None, self._synthesis, query, speaker.id)

        logger.info(f"音声合成完了 ({len(wav_bytes)} bytes)")
        return wav_bytes

    async def synthesize_to_file(self, text: str, speaker_name: str | None = None) -> str:
        """テキストを音声合成して一時WAVファイルのパスを返す
        
        Args:
            text: 音声合成するテキスト
            speaker_name: 話者名（config.pyのSPEAKERSに定義されている名前）
                         省略時はデフォルト話者を使用
        
        Returns:
            一時WAVファイルのパス
        """
        wav_bytes = await self.synthesize(text, speaker_name)

        fd, tmp_path = tempfile.mkstemp(suffix=".wav", prefix="voicevox_")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(wav_bytes)
            logger.info(f"一時ファイルに保存: {tmp_path}")
            return tmp_path
        except Exception:
            os.close(fd)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
