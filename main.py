import os
import asyncio
import requests
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

# Secrets 정보 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def main():
    print("뉴스 데이터 수집 및 분석 시작 (Gemini 2.5 Flash)...")
    
    # 1. AI에게 뉴스 요약 요청 (모델명을 gemini-2.5-flash로 변경)
    # 목록에 있던 정확한 모델명을 사용합니다.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "오늘의 전 세계 주요 경제 및 기술 뉴스 3가지를 한국어로 핵심만 간략하게 요약해줘. 이모지를 사용해서 보기 좋게 만들어줘."}]
        }]
    }

    try:
        # AI 서버로 요청 전송
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            # 답변 추출
            try:
                report_text = result['candidates'][0]['content']['parts'][0]['text']
                print("✅ AI 분석 완료")
            except:
                report_text = "AI 답변을 가져왔지만 형식이 달라 읽지 못했습니다."
        else:
            report_text = f"⚠️ AI 연결 실패 (코드 {response.status_code}): {response.text}"
            print(report_text)

        # 2. 텔레그램으로 결과 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 메시지 전송 완료!")

    except Exception as e:
        print(f"시스템 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
