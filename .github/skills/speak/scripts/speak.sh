#!/bin/bash
##
## VoiceBox API 音声合成スクリプト
##
## VoiceBox APIサーバーに音声合成リクエストを送信します。
## Copilotスキルから実行される想定のスクリプトです。
##

set -e

VOICEBOX_API_URL="http://127.0.0.1:8767"

# ヘルプ表示
show_help() {
    cat << EOF
VoiceBox API 音声合成スクリプト

使い方:
    $0 "読み上げるテキスト" [オプション]

オプション:
    -s, --speaker NAME      話者名（zundamon, tsumugi, metan）
    --no-transform          口調変換を無効化（元のテキストのまま読み上げ）
    --list-speakers         利用可能な話者一覧を表示
    -h, --help              このヘルプを表示

例:
    $0 "タスクが完了しました"
    $0 "完了" -s tsumugi
    $0 "完了なのだ" -s zundamon --no-transform
    $0 --list-speakers
EOF
}

# 話者一覧を取得
list_speakers() {
    response=$(curl -s -f "${VOICEBOX_API_URL}/speakers" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "⚠️  VoiceBox APIサーバーに接続できません" >&2
        echo "   サーバーが起動しているか確認してください: ./start_server.sh" >&2
        return 1
    fi
    
    echo "利用可能な話者:"
    echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for name, info in data.items():
    print(f\"  - {name}: {info['display_name']} (速度: {info['speed_scale']})\")
"
}

# 音声合成を実行
speak() {
    local text="$1"
    local speaker="$2"
    local transform_tone="$3"
    
    # JSONペイロード作成
    local payload="{\"text\": \"$text\", \"transform_tone\": $transform_tone"
    
    if [ -n "$speaker" ]; then
        payload="$payload, \"speaker_name\": \"$speaker\""
    fi
    
    payload="$payload}"
    
    # APIリクエスト送信
    response=$(curl -s -f -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "${VOICEBOX_API_URL}/speech" 2>&1)
    
    if [ $? -ne 0 ]; then
        if echo "$response" | grep -q "Connection refused"; then
            echo "⚠️  VoiceBox APIサーバーに接続できません" >&2
            echo "   サーバーが起動しているか確認してください: ./start_server.sh" >&2
        elif echo "$response" | grep -q "timed out"; then
            echo "⚠️  リクエストがタイムアウトしました" >&2
        else
            echo "⚠️  リクエストエラー: $response" >&2
        fi
        return 1
    fi
    
    # レスポンスからメッセージを抽出
    message=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'OK'))" 2>/dev/null || echo "OK")
    echo "✓ 音声合成リクエスト送信: $message"
    return 0
}

# ==================== メイン処理 ====================

text=""
speaker=""
transform_tone="true"
list_mode=false

# 引数パース
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --list-speakers)
            list_mode=true
            shift
            ;;
        -s|--speaker)
            speaker="$2"
            shift 2
            ;;
        --no-transform)
            transform_tone="false"
            shift
            ;;
        -*)
            echo "不明なオプション: $1" >&2
            show_help >&2
            exit 1
            ;;
        *)
            text="$1"
            shift
            ;;
    esac
done

# 話者一覧表示モード
if [ "$list_mode" = true ]; then
    list_speakers
    exit $?
fi

# テキストが指定されていない場合
if [ -z "$text" ]; then
    show_help
    exit 1
fi

# 音声合成実行
speak "$text" "$speaker" "$transform_tone"
exit $?
