"""
VoiceBox API クライアント例

他のプロジェクトからVoiceBox APIサーバーを呼び出すサンプルコード
"""

import requests
from typing import Optional


class VoiceBoxClient:
    """VoiceBox API クライアント"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8767"):
        self.base_url = base_url
    
    def speak(self, text: str, speaker_name: Optional[str] = None) -> dict:
        """
        テキストを音声合成して読み上げる
        
        Args:
            text: 読み上げるテキスト
            speaker_name: 話者名（省略時はデフォルト）
        
        Returns:
            APIレスポンス
        """
        url = f"{self.base_url}/speech"
        payload = {"text": text}
        
        if speaker_name:
            payload["speaker_name"] = speaker_name
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_speakers(self) -> dict:
        """利用可能な話者一覧を取得"""
        url = f"{self.base_url}/speakers"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> dict:
        """ヘルスチェック"""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


# 使用例
if __name__ == "__main__":
    client = VoiceBoxClient()
    
    # ヘルスチェック
    print("ヘルスチェック:", client.health_check())
    
    # 話者一覧取得
    print("\n利用可能な話者:")
    speakers = client.get_speakers()
    for name, info in speakers.items():
        print(f"  - {name}: {info['display_name']} (速度: {info['speed_scale']})")
    
    # 音声合成（デフォルト話者）
    print("\n音声合成リクエスト（デフォルト話者）:")
    result = client.speak("こんにちは！音声合成のテストです。")
    print(result)
    
    # 音声合成（話者指定）
    print("\n音声合成リクエスト（つむぎ）:")
    result = client.speak("春日部つむぎです。よろしくお願いします。", speaker_name="tsumugi")
    print(result)
    
    # curlコマンド例も表示
    print("\n" + "="*60)
    print("curlコマンド例:")
    print("="*60)
    print("\n# デフォルト話者で読み上げ")
    print('curl -X POST http://127.0.0.1:8767/speech \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"text": "こんにちは"}\'')
    
    print("\n# 話者を指定して読み上げ")
    print('curl -X POST http://127.0.0.1:8767/speech \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"text": "こんにちは", "speaker_name": "tsumugi"}\'')
    
    print("\n# 話者一覧取得")
    print('curl http://127.0.0.1:8767/speakers')
