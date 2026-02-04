import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import google.generativeai as genai

# GitHub Secrets에서 정보 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
# 모델명을 'gemini-1.5-flash'로 명확히 지정
model = genai.GenerativeModel('gemini-1.5-flash')

async def main():
    print("뉴스 수집 및 AI 분석 시작...")
    
    try:
        # 테스트용 프롬프트 (나중에 뉴스 수집 코드가 있다면 여기에 넣으세요)
        prompt = "오늘의 주요 경제 뉴스 3가지를 요약해서 알려줘."
        
        # AI 분석 요청
        response = model.generate_content(prompt)
        report_text = response.text
        
        # 텔레그램 메시지 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, report_text)
            print("텔레그램 메시지 전송 성공!")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
