"""
VOICEVOX MCP Server
FastMCPベースの音声合成MCPサーバー

GitHub Copilot / Claude Desktop からキャラクターボイスを呼び出せます。
"""

import asyncio
import logging
import random
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from yomiage-svr.tools.speech_tool import SpeechTool
from yomiage-svr.config import list_speakers, get_speaker, SPEAKERS
from yomiage-svr.services.ollama_service import OllamaService
from yomiage-svr.services.startup_service import startup_service

# ログ設定（MCPサーバーではstderrに出力）
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# FastMCP サーバー初期化
mcp = FastMCP("VOICEVOX Speech Server")

# サービスインスタンス（グローバル）
speech_tool = SpeechTool()
ollama_service = OllamaService()


# レスポンスモデル
class SpeakerInfo(BaseModel):
    """話者情報"""
    name: str = Field(description="話者名（内部ID）")
    display_name: str = Field(description="表示名")
    style: str = Field(description="話し方スタイル")
    speed_scale: float = Field(description="話速（倍率）")


class SpeakersResponse(BaseModel):
    """話者一覧レスポンス"""
    speakers: list[SpeakerInfo] = Field(description="利用可能な話者一覧")
    default_speaker: str = Field(description="デフォルト話者名")


class TransformResult(BaseModel):
    """口調変換結果"""
    original_text: str = Field(description="元のテキスト")
    transformed_text: str = Field(description="変換後のテキスト")
    speaker_name: str = Field(description="使用した話者名")


@mcp.tool()
def list_available_speakers() -> SpeakersResponse:
    """利用可能な話者（キャラクター）の一覧を取得
    
    Returns:
        話者情報のリスト（ずんだもん、春日部つむぎ、四国めたんなど）
    """
    logger.info("話者一覧取得リクエスト")
    
    speakers_list = []
    for key, speaker in SPEAKERS.items():
        speakers_list.append(SpeakerInfo(
            name=key,
            display_name=speaker.name,
            style=speaker.style,
            speed_scale=speaker.speed_scale
        ))
    
    return SpeakersResponse(
        speakers=speakers_list,
        default_speaker=list(SPEAKERS.keys())[0]
    )


@mcp.tool()
async def speak(
    text: str = Field(description="読み上げるテキスト"),
    speaker_name: Optional[str] = Field(
        None, 
        description="話者名（zundamon, tsumugi, metan）。省略時は自動選択"
    ),
    transform_tone: bool = Field(
        True, 
        description="Ollamaで口調変換するか（True: 変換する, False: そのまま読む）"
    )
) -> str:
    """テキストを音声合成してキャラクターボイスで読み上げる
    
    Args:
        text: 読み上げるテキスト
        speaker_name: 話者名（zundamon, tsumugi, metan）。省略時は自動選択
        transform_tone: 口調変換の有無
        
    Returns:
        実行結果メッセージ
    """
    logger.info(f"音声合成リクエスト: text='{text[:50]}...', speaker={speaker_name}, transform={transform_tone}")
    
    try:
        # 話者が指定されていない場合はランダム選択
        if not speaker_name:
            speaker_name = random.choice(list(SPEAKERS.keys()))
            logger.info(f"話者をランダム選択: {speaker_name}")
        
        # 話者の存在確認
        speaker = get_speaker(speaker_name)
        if not speaker:
            available = ", ".join(SPEAKERS.keys())
            error_msg = f"話者 '{speaker_name}' が見つかりません。利用可能: {available}"
            logger.error(error_msg)
            return f"❌ エラー: {error_msg}"
        
        # 口調変換
        transformed_text = text
        if transform_tone and speaker.tone_prompt:
            logger.info("Ollamaで口調変換を実行中...")
            try:
                transformed_text = ollama_service.transform_text(text, speaker.tone_prompt)
                logger.info(f"口調変換完了: '{transformed_text[:50]}...'")
            except Exception as e:
                logger.warning(f"口調変換失敗（元のテキストを使用）: {e}")
                transformed_text = text
        
        # 音声合成＆再生（バックグラウンド実行）
        asyncio.create_task(speech_tool.speak(transformed_text, speaker_name))
        
        result_msg = f"✅ 音声合成を開始しました\n話者: {speaker.name}\n元テキスト: {text}\n"
        if transform_tone and transformed_text != text:
            result_msg += f"変換後: {transformed_text}"
        else:
            result_msg += f"読み上げ: {transformed_text}"
            
        return result_msg
        
    except Exception as e:
        error_msg = f"音声合成エラー: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"❌ {error_msg}"


@mcp.tool()
def transform_character_tone(
    text: str = Field(description="変換するテキスト"),
    speaker_name: str = Field(description="話者名（zundamon, tsumugi, metan）")
) -> TransformResult:
    """テキストをキャラクターの口調に変換（音声合成なし、文字列のみ）
    
    Args:
        text: 変換元のテキスト
        speaker_name: 話者名
        
    Returns:
        変換結果（元テキストと変換後テキスト）
    """
    logger.info(f"口調変換リクエスト: text='{text[:50]}...', speaker={speaker_name}")
    
    try:
        # 話者の存在確認
        speaker = get_speaker(speaker_name)
        if not speaker:
            available = ", ".join(SPEAKERS.keys())
            raise ValueError(f"話者 '{speaker_name}' が見つかりません。利用可能: {available}")
        
        # 口調変換
        if speaker.tone_prompt:
            transformed_text = ollama_service.transform_text(text, speaker.tone_prompt)
            logger.info(f"変換完了: '{transformed_text[:50]}...'")
        else:
            transformed_text = text
            logger.info("この話者には口調プロンプトがありません（変換スキップ）")
        
        return TransformResult(
            original_text=text,
            transformed_text=transformed_text,
            speaker_name=speaker_name
        )
        
    except Exception as e:
        error_msg = f"口調変換エラー: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("VOICEVOX MCP Server を起動します...")
    
    # 起動前の初期化処理を実行（MCPサーバーはポートチェック不要）
    try:
        asyncio.run(startup_service.initialize_all_services(target_port=None, skip_port_check=True))
    except SystemExit:
        # 初期化処理で sys.exit() が呼ばれた場合（エラー時）
        logger.error("初期化処理が失敗しました。プロセスを終了します。")
        sys.exit(1)
    
    logger.info(f"登録済み話者: {', '.join(SPEAKERS.keys())}")
    
    # 終了時のクリーンアップハンドラー設定
    import signal
    def cleanup_handler(signum, frame):
        logger.info("MCPサーバーを終了しています...")
        startup_service.cleanup_ollama()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    
    # stdio transport でMCPサーバーを起動
    try:
        mcp.run()
    finally:
        # 通常終了時もクリーンアップを実行
        startup_service.cleanup_ollama()
