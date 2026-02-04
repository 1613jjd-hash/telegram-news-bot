import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from google import genai  # 최신 라이브러리 사용

# GitHub Secrets 데이터 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 최신 Gemini 클라이언트 설정
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

async def main():
    print("뉴스 분석 시작 (최신 방식)...")
    try:
        # AI 분석 요청 (경로 문제 해결)
        response = client_gemini.models.generate_content(
            model='gemini-1.5-flash', 
            contents="오늘의 주요 뉴스 3가지를 아주 짧게 요약해줘."
        )
        
        report_text = response.text
        print(f"분석 성공: {report_text[:15]}...")

        # 텔레그램 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client_tg:
            await client_tg.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 메시지 전송 성공!")

    except Exception as e:
        print(f"최종 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
