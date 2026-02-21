"""
Startup Service - サーバー起動時の前処理を管理
"""
import asyncio
import logging
import subprocess
import sys
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class StartupService:
    """サーバー起動時の前処理を管理するサービス"""
    
    def __init__(self):
        self.ollama_pid: Optional[int] = None
        
    async def initialize_all_services(self, target_port: Optional[int] = 8767, skip_port_check: bool = False) -> None:
        """
        全サービスの初期化を実行
        
        Args:
            target_port: 対象ポート番号（デフォルト: 8767、MCPサーバーの場合はNone）
            skip_port_check: ポートチェックをスキップするか（MCPサーバー用）
        """
        logger.info("サーバー起動前の初期化を開始します...")
        
        # 1. VOICEVOXの起動確認
        await self.check_voicevox_server()
        
        # 2. Ollamaの起動確認・自動起動
        await self.ensure_ollama_server()
        
        # 3. 対象ポートの既存プロセス終了（HTTPサーバーの場合のみ）
        if not skip_port_check and target_port is not None:
            await self.kill_existing_processes(target_port)
        elif skip_port_check:
            logger.info("MCPサーバー起動: ポートチェックをスキップします")
        
        logger.info("✅ 初期化完了 - サーバーを起動します...")
    
    async def check_voicevox_server(self) -> None:
        """VOICEVOXサーバーの起動確認"""
        logger.info("VOICEVOXサーバーを確認しています...")
        
        try:
            response = requests.get("http://localhost:50021/version", timeout=3)
            if response.status_code == 200:
                logger.info("✅ VOICEVOX確認完了")
                return
        except requests.RequestException:
            pass
        
        # VOICEVOXが起動していない場合
        logger.error("❌ VOICEVOXサーバーが起動していません")
        logger.error("VOICEVOXアプリを起動してから再度実行してください")
        sys.exit(1)
    
    async def ensure_ollama_server(self) -> None:
        """Ollamaサーバーの確認・自動起動
        
        注意: Ollamaは複数のMCPサーバーインスタンスで共有される
        複数のワークスペースから同時起動されても、同じOllamaインスタンスを使用する
        """
        logger.info("Ollamaサーバーを確認しています...")
        
        # 既に起動しているかチェック
        if await self._is_ollama_running():
            logger.info("✅ Ollama既に起動済み（複数ワークスペースで共有）")
            return
        
        # Ollamaを起動
        logger.info("Ollamaサーバーを起動しています...")
        try:
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.ollama_pid = process.pid
            
            # 起動を待機（最大15秒）
            logger.info("Ollamaの起動を待機中...")
            for i in range(15):
                if await self._is_ollama_running():
                    logger.info("✅ Ollama起動完了")
                    return
                await asyncio.sleep(1)
            
            # 起動に失敗した場合
            logger.error("❌ Ollamaの起動に失敗しました")
            self.cleanup_ollama()
            sys.exit(1)
            
        except FileNotFoundError:
            logger.error("❌ Ollamaコマンドが見つかりません")
            logger.error("Ollamaをインストールしてから再度実行してください")
            sys.exit(1)
    
    async def _is_ollama_running(self) -> bool:
        """Ollamaが起動しているかチェック"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    async def kill_existing_processes(self, port: int) -> None:
        """指定ポートの既存プロセスを終了"""
        logger.info(f"ポート{port}の既存プロセスを確認しています...")
        
        try:
            # lsofコマンドでポートを使用しているプロセスIDを取得
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                logger.info(f"ポート{port}で動作中のプロセスを終了します...")
                
                # kill -9 でプロセスを強制終了
                subprocess.run(
                    ["kill", "-9"] + pids,
                    capture_output=True,
                    timeout=5
                )
                
                await asyncio.sleep(1)  # 少し待機
                logger.info("✅ 既存プロセス終了完了")
            else:
                logger.info(f"✅ ポート{port}は使用可能")
        
        except subprocess.TimeoutExpired:
            logger.warning(f"ポート{port}チェックでタイムアウト")
        except FileNotFoundError:
            logger.warning("lsofコマンドが見つかりません（Windowsの場合は正常）")
        except Exception as e:
            logger.warning(f"ポートチェック中にエラー: {e}")
    
    def cleanup_ollama(self) -> None:
        """Ollamaプロセスのクリーンアップ"""
        if self.ollama_pid:
            try:
                subprocess.run(
                    ["kill", str(self.ollama_pid)],
                    capture_output=True,
                    timeout=3
                )
                logger.info("Ollamaサーバーを終了しました")
            except subprocess.TimeoutExpired:
                logger.warning("Ollama終了処理でタイムアウト")
            except Exception as e:
                logger.warning(f"Ollama終了時にエラー: {e}")
            finally:
                self.ollama_pid = None


# グローバルインスタンス
startup_service = StartupService()


# 終了時クリーンアップ用
def cleanup_on_exit():
    """プロセス終了時のクリーンアップ処理"""
    startup_service.cleanup_ollama()


# シグナルハンドラー設定
import signal
signal.signal(signal.SIGTERM, lambda signum, frame: cleanup_on_exit())
signal.signal(signal.SIGINT, lambda signum, frame: cleanup_on_exit())
