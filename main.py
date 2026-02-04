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

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def main():
    try:
        prompt = "오늘의 주요 뉴스 3가지를 요약해줘."
        response = model.generate_content(prompt)
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            await client.send_message(CHAT_ID, response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
