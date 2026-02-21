#!/bin/bash
# VoiceBox API Server 起動スクリプト（簡素化版）

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source venv/bin/activate

echo "VoiceBox API Server を起動しています..."
echo "（VOICEVOX・Ollamaの確認、ポートチェックはサーバー内で自動実行されます）"
echo "サーバーURL: http://127.0.0.1:8767"
echo "停止するには Ctrl+C を押してください"
echo ""

# サーバー起動（初期化処理は内部で実行される）
python api_server.py
