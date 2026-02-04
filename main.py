import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from google import genai

# Secrets 데이터 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 클라이언트 설정
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

async def main():
    print("뉴스 분석 시작 (호환성 모드)...")
    try:
        # 모델명을 'models/gemini-1.5-flash' 전체 경로로 입력해봅니다.
        response = client_gemini.models.generate_content(
            model='gemini-1.5-flash', 
            contents="오늘의 뉴스 요약을 한국어로 짧게 부탁해."
        )
        
        report_text = response.text
        print(f"AI 분석 완료!")

        # 텔레그램 전송
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client_tg:
            await client_tg.send_message(CHAT_ID, report_text)
            print("★ 텔레그램 메시지 전송 성공!")

    except Exception as e:
        # 에러가 나면 텔레그램으로 에러 내용이라도 보내서 연결 확인
        print(f"에러 발생: {e}")
        try:
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client_tg:
                await client_tg.send_message(CHAT_ID, f"AI 분석 중 에러가 발생했어요: {e}")
                print("에러 메시지를 텔레그램으로 보냈습니다.")
        except:
            print("텔레그램 전송마저 실패했습니다. 세션이나 ID를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
