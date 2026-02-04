import os
import asyncio
import requests
import json
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession

# GitHub Secrets 정보 가져오기
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 콤마로 구분된 여러 개의 방 ID를 리스트로 변환
source_ids_raw = os.environ.get("SOURCE_CHANNEL_ID", "")
SOURCE_CHANNEL_IDS = [int(x.strip()) for x in source_ids_raw.split(',') if x.strip()]

async def main():
    print(f"총 {len(SOURCE_CHANNEL_IDS)}개의 방 분석 시작 (Model: Gemini 2.5 Pro)...")
    
    full_report_data = []

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        time_limit = datetime.now(timezone.utc) - timedelta(hours=24)

        for room_id in SOURCE_CHANNEL_IDS:
            try:
                entity = await client.get_entity(room_id)
                room_name = entity.title if hasattr(entity, 'title') else "알 수 없는 방"
                print(f"📥 수집 중: {room_name}")

                room_messages = []
                # Pro 모델은 똑똑하지만 한 번에 처리하는 양이 정해져 있으니 방당 80개 정도로 조절
                async for message in client.iter_messages(room_id, limit=80):
                    if message.date < time_limit:
                        break
                    
                    if message.text and len(message.text) > 10:
                        msg_time = message.date.strftime("%H:%M")
                        room_messages.append(f"[{room_name} | {msg_time}] {message.text}")
                
                room_messages.reverse()
                
                if room_messages:
                    full_report_data.append(f"\n=== 🏠 {room_name} 대화 내용 ===\n" + "\n".join(room_messages))

            except Exception as e:
                print(f"⚠️ {room_id} 수집 건너뜀: {e}")
                continue

    final_text = "\n".join(full_report_data)
    
    if not final_text:
        print("수집된 내용 없음.")
        return

    print(f"수집 완료. AI 요약 요청 중... (Pro 모델이라 시간이 조금 더 걸릴 수 있습니다)")

    # ✅ 여기가 변경되었습니다: gemini-2.5-flash -> gemini-2.5-pro
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    너는 최고의 금융/투자 분석가야. 아래는 주식/정보방들의 지난 24시간 대화 내용이야.
    이 내용을 깊이 있게 분석해서 보고서를 작성해줘. 단순 나열하지 말고 '통찰(Insight)'을 담아줘.

    [작성 양식]
    # 🧐 일일 투자 인사이트 리포트 (Gemini Pro)
    
    ## 1. 🌪️ 시장을 관통하는 핵심 키워드
    * (대화 전체를 관통하는 가장 중요한 주제나 분위기 분석)

    ## 2. 💬 커뮤니티 여론 및 반응
    * **{full_report_data[0].split('===')[1].strip() if full_report_data else '방'} 등**: (각 방별 참여자들의 심리 상태나 주요 관심사 분석)

    ## 3. 🚀 주목할 종목/섹터 Top Picks
    * (단순 언급이 아닌, 왜 주목받는지 이유 포함)

    ---
    [데이터]
    {final_text}
    """

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            try:
                report_text = result['candidates'][0]['content']['parts'][0]['text']
                
                async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                    # 내용이 길어질 수 있어 안전하게 나누기
                    if len(report_text) > 4000:
                        await client.send_message(CHAT_ID, report_text[:4000])
                        await client.send_message(CHAT_ID, report_text[4000:])
                    else:
                        await client.send_message(CHAT_ID, report_text)
                    print("★ Pro 모델 분석 결과 전송 완료!")
            except:
                print("AI 답변 형식 오류")
        else:
            print(f"AI 요청 실패: {response.text}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
