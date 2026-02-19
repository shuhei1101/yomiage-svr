"""
NotifyAgentActMCP - MCPサーバー本体
VOICEVOX音声合成を提供するMCPサーバー
"""

import asyncio
import logging
import sys

from dotenv import load_dotenv
load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from vbmcp.tools.speech_tool import SpeechTool
from vbmcp.config import list_speakers, SPEAKERS

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Server("NotifyAgentAct")
speech_tool = SpeechTool()


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """利用可能なツールのリストを返す"""
    # 利用可能な話者リストを生成
    speaker_list = []
    for name, speaker in SPEAKERS.items():
        speaker_list.append(f"{name}: {speaker}")
    speakers_desc = "\n".join(speaker_list)
    
    return [
        types.Tool(
            name="Speech",
            description="テキストをVOICEVOXで音声合成して読み上げます。ずんだもんなどのキャラクターボイスでテキストを読み上げます。",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "読み上げるテキスト",
                    },
                    "speaker_name": {
                        "type": "string",
                        "description": f"話者名（省略時はデフォルト話者を使用）。利用可能な話者:\n{speakers_desc}",
                        "enum": list_speakers(),
                    },
                },
                "required": ["text"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """ツール呼び出しを処理する"""
    if name == "Speech":
        text = arguments.get("text", "")
        if not text:
            return [types.TextContent(type="text", text="エラー: テキストが指定されていません")]

        # 話者名を取得（オプショナル）
        speaker_name = arguments.get("speaker_name")

        # バックグラウンドで音声合成・再生を実行（ブロッキングしない）
        asyncio.create_task(speech_tool.speak(text, speaker_name))
        
        # レスポンスメッセージ
        speaker_info = f" (話者: {speaker_name})" if speaker_name else ""
        
        return [types.TextContent(type="text", text=f"音声合成を開始しました{speaker_info}: {text[:50]}{'...' if len(text) > 50 else ''}")]
    else:
        return [types.TextContent(type="text", text=f"エラー: 未知のツール '{name}'")]


async def main():
    logger.info("NotifyAgentActMCP サーバーを起動しています...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
