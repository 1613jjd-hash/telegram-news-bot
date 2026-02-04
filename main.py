import os
import asyncio
import requests
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

# Secrets 정보
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def main():
    print("사용 가능한 모델 목록 조회 중...")
    
    # 1. 구글에게 "사용 가능한 모델 다 내놔"라고 요청 (List Models)
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # 'generateContent' 기능이 있는 모델만 골라내기
            available_models = []
            if 'models' in data:
                for m in data['models']:
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        available_models.append(m['name']) # 예: models/gemini-pro
            
            if available_models:
                # 모델 목록을 줄바꿈으로 연결
                msg_text = "✅ 사용 가능한 모델 목록:\n" + "\n".join(available_models)
            else:
                msg_text = "❌ API 키는 맞는데, 사용할 수 있는 모델이 하나도 없습니다. (권한 문제 가능성)"
                
        else:
            msg_text = f"❌ 모델 목록 조회 실패 (코드 {response.status_code}): {response.text}"

        print(msg_text)

        # 2. 결과 텔레그램 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, msg_text)
            print("★ 진단 결과 텔레그램 전송 완료!")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
