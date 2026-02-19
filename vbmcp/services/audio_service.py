"""
音声再生サービス
WAVファイルを再生する（macOS/Linux/Windows対応）
"""

import asyncio
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioService:
    """音声再生サービス"""

    def __init__(self) -> None:
        self._system = platform.system()
        logger.info(f"OS: {self._system}")

    async def play(self, wav_path: str) -> None:
        """WAVファイルを非同期で再生する"""
        logger.info(f"音声再生開始: {wav_path}")
        try:
            await self._play_with_best_method(wav_path)
            logger.info(f"音声再生完了: {wav_path}")
        except Exception as e:
            logger.error(f"音声再生エラー: {e}")
            raise

    async def _play_with_best_method(self, wav_path: str) -> None:
        """OSに適した再生方法を選択する"""
        # まずsounddevice + soundfileを試みる
        try:
            await self._play_with_sounddevice(wav_path)
            return
        except ImportError:
            logger.debug("sounddeviceが利用不可。コマンドラインツールにフォールバック")
        except Exception as e:
            logger.warning(f"sounddeviceでの再生に失敗: {e}。コマンドラインツールにフォールバック")

        # コマンドラインツールを使用
        await self._play_with_command(wav_path)

    async def _play_with_sounddevice(self, wav_path: str) -> None:
        """sounddevice + soundfileで再生する"""
        import sounddevice as sd  # pyright: ignore[reportMissingModuleSource]
        import soundfile as sf  # pyright: ignore[reportMissingModuleSource]

        loop = asyncio.get_event_loop()

        def _blocking_play():
            data, samplerate = sf.read(wav_path, dtype="float32")
            sd.play(data, samplerate)
            sd.wait()

        await loop.run_in_executor(None, _blocking_play)

    async def _play_with_command(self, wav_path: str) -> None:
        """OSのコマンドラインツールで再生する"""
        if self._system == "Darwin":
            cmd = ["afplay", wav_path]
        elif self._system == "Linux":
            # aplay -> paplay -> ffplay の順で試みる
            cmd = self._find_linux_player(wav_path)
        elif self._system == "Windows":
            cmd = ["powershell", "-c", f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync()']
        else:
            raise RuntimeError(f"サポートされていないOS: {self._system}")

        logger.debug(f"コマンド実行: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace").strip() if stderr else "不明なエラー"
            raise RuntimeError(f"音声再生コマンドが失敗しました (終了コード {proc.returncode}): {err_msg}")

    def _find_linux_player(self, wav_path: str) -> list[str]:
        """Linuxで利用可能な再生コマンドを探す"""
        players = [
            ["aplay", wav_path],
            ["paplay", wav_path],
            ["ffplay", "-nodisp", "-autoexit", wav_path],
            ["cvlc", "--play-and-exit", wav_path],
        ]
        for player_cmd in players:
            executable = player_cmd[0]
            result = subprocess.run(["which", executable], capture_output=True)
            if result.returncode == 0:
                return player_cmd

        raise RuntimeError(
            "Linuxで音声再生ツールが見つかりません。"
            "aplay、paplay、ffplay のいずれかをインストールしてください。"
        )
