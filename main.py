import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import google.generativeai as genai
import requests

# GitHub Secrets에서 정보 가져오기
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']
gemini_key = os.environ['GEMINI_API_KEY']
bot_token = os.environ['BOT_TOKEN']
chat_id = os.environ['CHAT_ID']

# Gemini 설정
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 분석할 채널 리스트 (원하는 채널 ID나 @주소로 변경하세요)
TARGET_CHANNELS = ['@coindeskkorea', '@BlockMedia', '@bloomingbit'] 

async def main():
    # 텔레그램 접속
    client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
    await client.start()
    
    news_data = ""
    print("뉴스 수집 중...")
    
    # 각 채널에서 최근 메시지 10개씩만 가져오기 (너무 많으면 AI가 힘들어함)
    for channel in TARGET_CHANNELS:
        try:
            async for message in client.iter_messages(channel, limit=10):
                if message.text:
                    # 날짜와 내용 수집
                    date_str = message.date.strftime("%Y-%m-%d %H:%M")
                    news_data += f"[{channel} | {date_str}] {message.text[:200]}\n" # 너무 길면 자름
        except Exception as e:
            print(f"Error fetching {channel}: {e}")
            
    if not news_data:
        print("새로운 뉴스가 없습니다.")
        return

    print("AI 분석 요청 중...")
    
    # 프롬프트 작성
    prompt = f"""
    너는 월스트리트의 유능한 투자 분석가야. 아래 텔레그램 뉴스들을 읽고 한국어로 브리핑해줘.
    
    [뉴스 데이터]
    {news_data}
    
    [작성 양식]
    📊 **[오늘의 시장 브리핑]**
    
    1. **핵심 이슈 요약 (3가지)**
       - (이슈 1)
       - (이슈 2)
       - (이슈 3)
       
    2. **시장 분위기 (심리 지수)**
       - 점수: O/100 (0:공포 ~ 100:탐욕)
       - 판단: (강세장/약세장/보합세 중 택1)
       - 이유: (분위기 점수를 준 이유 1줄 설명)
       
    3. **투자자 대응 전략**
       - (한 줄 조언)
    """
    
    # Gemini에게 요청
    response = model.generate_content(prompt)
    summary = response.text
    
    # 결과 텔레그램 봇으로 전송
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(send_url, data={'chat_id': chat_id, 'text': summary, 'parse_mode': 'Markdown'})
    print("전송 완료!")

if __name__ == '__main__':
    asyncio.run(main())
