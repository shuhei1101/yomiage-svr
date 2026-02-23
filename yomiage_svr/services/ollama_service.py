"""Ollama連携サービス - テキストをキャラクターの口調に変換"""

import requests
import logging
from typing import Optional
from yomiage_svr import config

logger = logging.getLogger(__name__)


class OllamaService:
    """Ollama APIを使ってテキストをキャラクターの口調に変換するサービス"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None,
        num_predict: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        """
        Args:
            base_url: OllamaサーバーのベースURL（省略時はconfig.OLLAMA_BASE_URL）
            model: 使用するモデル名（省略時はconfig.OLLAMA_MODEL）
            temperature: 生成温度（省略時はconfig.OLLAMA_TEMPERATURE）
            top_p: nucleus sampling（省略時はconfig.OLLAMA_TOP_P）
            top_k: トップK候補（省略時はconfig.OLLAMA_TOP_K）
            repeat_penalty: 繰り返しペナルティ（省略時はconfig.OLLAMA_REPEAT_PENALTY）
            num_predict: 最大トークン数（省略時はconfig.OLLAMA_NUM_PREDICT）
            timeout: タイムアウト秒数（省略時はconfig.OLLAMA_TIMEOUT）
        """
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL
        self.temperature = temperature if temperature is not None else config.OLLAMA_TEMPERATURE
        self.top_p = top_p if top_p is not None else config.OLLAMA_TOP_P
        self.top_k = top_k if top_k is not None else config.OLLAMA_TOP_K
        self.repeat_penalty = repeat_penalty if repeat_penalty is not None else config.OLLAMA_REPEAT_PENALTY
        self.num_predict = num_predict if num_predict is not None else config.OLLAMA_NUM_PREDICT
        self.timeout = timeout if timeout is not None else config.OLLAMA_TIMEOUT
    
    def transform_text(self, text: str, character_prompt: str) -> str:
        """
        テキストをキャラクターの口調に変換
        
        Args:
            text: 変換元のテキスト
            character_prompt: キャラクター別の口調プロンプト
        
        Returns:
            変換後のテキスト（失敗時は元のテキストを返す）
        """
        try:
            # プロンプト構築
            full_prompt = f"{character_prompt}\n\n{text}"
            
            # Ollama APIリクエスト
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,  # ストリーミングなし
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                    "repeat_penalty": self.repeat_penalty,
                    "num_predict": self.num_predict,
                }
            }
            
            logger.info(f"Ollama変換リクエスト: model={self.model}, text_length={len(text)}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # レスポンスパース
            result = response.json()
            transformed_text = result.get("response", "").strip()
            
            if not transformed_text:
                logger.warning("Ollamaレスポンスが空 - 元のテキストを使用")
                return text
            
            logger.info(f"Ollama変換成功: {text[:30]}... -> {transformed_text[:30]}...")
            return transformed_text
            
        except requests.exceptions.Timeout:
            logger.error(f"Ollama変換タイムアウト（{self.timeout}秒） - 元のテキストを使用")
            return text
            
        except requests.exceptions.ConnectionError:
            logger.error("Ollamaサーバーに接続できません - 元のテキストを使用")
            return text
            
        except Exception as e:
            logger.error(f"Ollama変換エラー: {e} - 元のテキストを使用")
            return text
    
    def health_check(self) -> bool:
        """
        Ollamaサーバーの死活確認
        
        Returns:
            接続成功時True、失敗時False
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            logger.info("Ollamaサーバー接続OK")
            return True
        except Exception as e:
            logger.warning(f"Ollamaサーバー接続失敗: {e}")
            return False
