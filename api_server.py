"""
VoiceBox API Server
FastAPIベースの音声合成HTTPサーバー
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from vbmcp.tools.speech_tool import SpeechTool
from vbmcp.config import list_speakers, get_speaker, SPEAKERS
from vbmcp.services.ollama_service import OllamaService
from vbmcp.services.character_selector import CharacterSelector
from vbmcp.services.startup_service import startup_service

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# リクエストモデル
class SpeechRequest(BaseModel):
    text: str = Field(..., description="読み上げるテキスト", min_length=1)
    speaker_name: str | None = Field(None, description="話者名（省略時は自動選択）")
    transform_tone: bool = Field(True, description="口調変換の有無（True: Ollamaで変換, False: 元のまま）")


class TransformRequest(BaseModel):
    text: str = Field(..., description="変換するテキスト", min_length=1)
    speaker_name: str = Field(..., description="話者名（tsumugi, zundamon, metan）")


# レスポンスモデル
class SpeechResponse(BaseModel):
    status: str
    message: str
    speaker_name: str
    original_text: str
    transformed_text: str | None = None


class TransformResponse(BaseModel):
    speaker_name: str
    speaker_display_name: str
    original_text: str
    transformed_text: str
    success: bool


class SpeakerInfo(BaseModel):
    name: str
    display_name: str
    style: str
    speed_scale: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル"""
    logger.info("VoiceBox API Server starting...")
    
    # 起動前の初期化処理
    await startup_service.initialize_all_services(target_port=8767)
    
    yield
    
    # 終了時のクリーンアップ
    logger.info("VoiceBox API Server shutting down...")
    startup_service.cleanup_ollama()


# FastAPIアプリケーション
app = FastAPI(
    title="VoiceBox API",
    description="VOICEVOX音声合成APIサーバー",
    version="1.0.0",
    lifespan=lifespan
)

# サービスインスタンス
speech_tool = SpeechTool()
ollama_service = OllamaService()
character_selector = CharacterSelector(list_speakers())


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "service": "VoiceBox API",
        "version": "1.0.0",
        "endpoints": {
            "POST /speech": "音声合成リクエスト",
            "POST /transform": "口調変換のみ（音声再生なし）",
            "GET /speakers": "利用可能な話者一覧",
            "GET /health": "ヘルスチェック"
        }
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.get("/speakers", response_model=dict[str, SpeakerInfo])
async def get_speakers():
    """利用可能な話者一覧を取得"""
    speakers_info = {}
    for name, speaker in SPEAKERS.items():
        speakers_info[name] = SpeakerInfo(
            name=name,
            display_name=str(speaker),
            style=speaker.style,
            speed_scale=speaker.speed_scale
        )
    return speakers_info


@app.post("/transform", response_model=TransformResponse)
async def transform_tone(request: TransformRequest):
    """
    口調変換のみ（音声再生なし）
    
    テキストをキャラクターの口調に変換します。
    音声合成・再生は行わず、変換結果のみを返します。
    
    テスト・検証用途に最適です。
    """
    try:
        # 話者取得
        speaker = get_speaker(request.speaker_name)
        
        # Ollamaで口調変換
        transformed_text = ollama_service.transform_text(
            request.text,
            speaker.tone_prompt
        )
        
        logger.info(f"口調変換成功: {request.speaker_name} - {request.text[:30]}... -> {transformed_text[:30]}...")
        
        return TransformResponse(
            speaker_name=request.speaker_name,
            speaker_display_name=str(speaker),
            original_text=request.text,
            transformed_text=transformed_text,
            success=True
        )
        
    except ValueError as e:
        # 無効な話者名
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # その他のエラー（Ollama接続エラーなど）
        logger.error(f"口調変換エラー: {e}", exc_info=True)
        
        # エラー時は元のテキストを返す
        return TransformResponse(
            speaker_name=request.speaker_name,
            speaker_display_name=str(get_speaker(request.speaker_name)),
            original_text=request.text,
            transformed_text=request.text,  # フォールバック
            success=False
        )


async def _perform_speech(text: str, speaker_name: str | None):
    """音声合成をバックグラウンドで実行"""
    try:
        await speech_tool.speak(text, speaker_name)
    except Exception as e:
        logger.error(f"音声合成エラー: {e}", exc_info=True)


@app.post("/speech", response_model=SpeechResponse)
async def create_speech(
    request: SpeechRequest,
    background_tasks: BackgroundTasks
):
    """
    音声合成リクエスト
    
    テキストを音声合成して読み上げます。
    - speaker_name省略時: 自動選択
    - transform_tone=True: Ollamaで口調変換
    - transform_tone=False: 元のテキストのまま
    
    処理はバックグラウンドで実行されるため、即座にレスポンスが返ります。
    """
    original_text = request.text
    transformed_text = None
    
    # 話者名の決定
    if request.speaker_name is None:
        # 自動選択
        speaker_name = character_selector.select(request.text, strategy="random")
        logger.info(f"話者自動選択: {speaker_name}")
    else:
        # 手動指定
        speaker_name = request.speaker_name
        try:
            get_speaker(speaker_name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # 口調変換
    if request.transform_tone:
        try:
            speaker = get_speaker(speaker_name)
            transformed_text = ollama_service.transform_text(
                request.text,
                speaker.tone_prompt
            )
            final_text = transformed_text
            logger.info(f"口調変換: {original_text[:30]}... -> {transformed_text[:30]}...")
        except Exception as e:
            logger.error(f"口調変換エラー: {e} - 元のテキストを使用")
            final_text = original_text
            transformed_text = None
    else:
        final_text = original_text
        logger.info("口調変換スキップ")
    
    # バックグラウンドタスクとして音声合成を実行
    background_tasks.add_task(_perform_speech, final_text, speaker_name)
    
    message = f"音声合成を開始しました (話者: {speaker_name}): {final_text[:50]}{'...' if len(final_text) > 50 else ''}"
    
    return SpeechResponse(
        status="accepted",
        message=message,
        speaker_name=speaker_name,
        original_text=original_text,
        transformed_text=transformed_text
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8767,  # ポート変更（8767が使用中のため）
        reload=False,  # reload無効化
        log_level="info"
    )
