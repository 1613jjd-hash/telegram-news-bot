import os
import asyncio
import requests
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

# GitHub Secrets 정보 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def main():
    print("뉴스 브리핑 시작 (Gemini Pro)...")
    
    # 모델 이름을 'gemini-pro'로 변경 (가장 안정적인 버전)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "오늘의 주요 뉴스 3가지를 한국어로 요약해줘."}]
        }]
    }

    try:
        # AI에게 요청 보내기
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            # 성공 시 답변 내용 추출
            result = response.json()
            # 답변 구조가 조금 다를 수 있어 안전하게 추출
            try:
                report_text = result['candidates'][0]['content']['parts'][0]['text']
            except:
                report_text = "AI 답변을 해석하는 데 실패했습니다. 다시 시도해주세요."
                
            print("AI 답변 도착!")
        else:
            # 실패 시 에러 코드 출력
            report_text = f"AI 오류 (코드 {response.status_code}): {response.text}"
            print(report_text)

        # 텔레그램으로 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 전송 완료!")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
