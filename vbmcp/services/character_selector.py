"""キャラクター選択ロジック"""

import random
import logging
from typing import List

logger = logging.getLogger(__name__)


class CharacterSelector:
    """テキストの内容に応じてキャラクターを選択"""
    
    def __init__(self, speakers: List[str]):
        """
        Args:
            speakers: 利用可能な話者名のリスト
        """
        self.speakers = speakers
    
    def select(self, text: str, strategy: str = "random") -> str:
        """
        テキストに応じてキャラクターを選択
        
        Args:
            text: 入力テキスト
            strategy: 選択戦略（"random" | "rule_based"）
        
        Returns:
            選択された話者名
        """
        if strategy == "rule_based":
            return self._select_by_rule(text)
        else:
            return self._select_random()
    
    def _select_random(self) -> str:
        """ランダムにキャラクターを選択"""
        speaker = random.choice(self.speakers)
        logger.info(f"キャラクター選択（ランダム）: {speaker}")
        return speaker
    
    def _select_by_rule(self, text: str) -> str:
        """
        テキストの内容からキャラクターを選択
        
        ルール:
        - エラー・警告系 → めたん（緊張感）
        - 完了・成功系 → ずんだもん（元気）
        - その他 → つむぎ（丁寧）
        """
        text_lower = text.lower()
        
        # エラー・警告系
        error_keywords = ["エラー", "error", "問題", "警告", "失敗", "できません", "できない"]
        if any(keyword in text_lower for keyword in error_keywords):
            logger.info(f"キャラクター選択（ルール: エラー系）: metan")
            return "metan"
        
        # 完了・成功系
        success_keywords = ["完了", "成功", "できました", "finished", "success", "done"]
        if any(keyword in text_lower for keyword in success_keywords):
            logger.info(f"キャラクター選択（ルール: 成功系）: zundamon")
            return "zundamon"
        
        # デフォルト（丁寧な対応）
        logger.info(f"キャラクター選択（ルール: デフォルト）: tsumugi")
        return "tsumugi"


class RoundRobinSelector:
    """ラウンドロビン方式でキャラクターを順番に選択"""
    
    def __init__(self, speakers: List[str]):
        """
        Args:
            speakers: 利用可能な話者名のリスト
        """
        self.speakers = speakers
        self.index = 0
    
    def select(self, text: str = "") -> str:
        """
        順番にキャラクターを選択
        
        Args:
            text: 入力テキスト（未使用）
        
        Returns:
            選択された話者名
        """
        speaker = self.speakers[self.index]
        self.index = (self.index + 1) % len(self.speakers)
        logger.info(f"キャラクター選択（ラウンドロビン）: {speaker}")
        return speaker
