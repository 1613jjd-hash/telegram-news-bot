import os
import asyncio
import requests # 직접 요청을 보내는 도구
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

# Secrets 데이터 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def main():
    print("뉴스 분석 시작 (Direct API 방식)...")
    
    # 1. AI에게 질문하기 (라이브러리 없이 직접 주소로 요청)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "오늘의 주요 뉴스 3가지를 한국어로 간단히 요약해줘."}]
        }]
    }

    try:
        # 우편 보내듯 데이터 전송
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            # 성공하면 답장 뜯어보기
            result = response.json()
            report_text = result['candidates'][0]['content']['parts'][0]['text']
            print("AI 답변 도착 완료!")
        else:
            # 실패하면 에러 내용 확인
            report_text = f"AI 연결 실패 (코드 {response.status_code}): {response.text}"
            print(report_text)

        # 2. 텔레그램 전송 (이건 이미 성공했음!)
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 전송 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
