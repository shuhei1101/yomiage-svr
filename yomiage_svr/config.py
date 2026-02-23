"""
VOICEVOX 話者設定

このファイルでは音声合成に使用する話者（キャラクター）の設定を管理します。
キャラクター固有の設定は charactor/ フォルダの個別ファイルに分割されています。
"""

import os

# 基本クラスのインポート
from .base import VoiceSpeaker

# キャラクター固有設定のインポート
from .charactor.zundamon import get_zundamon_speaker
from .charactor.tsumugi import get_tsumugi_speaker  
from .charactor.metan import get_metan_speaker


# 話者設定の動的読み込み
def _load_speakers() -> dict[str, VoiceSpeaker]:
    """
    各キャラクターファイルから設定を読み込んで辞書を作成
    
    Returns:
        dict[str, VoiceSpeaker]: 話者名をキーとした設定辞書
    """
    return {
        "zundamon": get_zundamon_speaker(),
        "tsumugi": get_tsumugi_speaker(),
        "metan": get_metan_speaker(),
    }


# 話者設定辞書
SPEAKERS = _load_speakers()

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


# ==================== Ollama設定 ====================

# Ollamaサーバー設定
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:2b")

# Ollama生成パラメータ（バリエーション重視設定）
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))  # 適度な温度でバリエーション確保
OLLAMA_TOP_P = float(os.getenv("OLLAMA_TOP_P", "0.9"))              # nucleus sampling
OLLAMA_TOP_K = int(os.getenv("OLLAMA_TOP_K", "30"))                 # トップ30候補
OLLAMA_REPEAT_PENALTY = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.1"))  # 繰り返し防止
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "200"))    # 最大トークン数
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "15"))             # タイムアウト（秒）
