import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import google.generativeai as genai

# GitHub Secrets 데이터 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

async def main():
    print("뉴스 분석 시작...")
    try:
        # 모델명을 v1beta 경로 없이 단순하게 지정
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "오늘의 주요 뉴스 3가지를 짧게 요약해줘."
        response = model.generate_content(prompt)
        
        # 분석 결과 확인
        report_text = response.text
        print(f"분석 내용: {report_text[:20]}...")

        # 텔레그램 전송
        # StringSession 안에 SESSION_STRING을 넣는 방식 확인
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 메시지 전송 성공!")

    except Exception as e:
        print(f"오류 상세 내용: {e}")

if __name__ == "__main__":
    asyncio.run(main())
