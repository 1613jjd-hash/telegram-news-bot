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
    print(f"총 {len(SOURCE_CHANNEL_IDS)}개의 방 분석 시작 (Model: Gemini 2.0 Flash)...")
    
    full_report_data = []

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        time_limit = datetime.now(timezone.utc) - timedelta(hours=24)

        for room_id in SOURCE_CHANNEL_IDS:
            try:
                # 방 정보 가져오기 시도
                try:
                    entity = await client.get_entity(room_id)
                    room_name = entity.title if hasattr(entity, 'title') else "알 수 없는 방"
                except:
                    # 방 정보를 못 찾으면(Entity Error) 그냥 ID로 표시하고 계속 진행
                    room_name = f"방 ID {room_id}"
                    print(f"⚠️ 방 정보를 찾을 수 없어 ID로 대체합니다: {room_id}")

                print(f"📥 수집 중: {room_name}")

                room_messages = []
                # 안전하게 방당 50개까지만 수집 (Flash 모델이라도 양 조절 필요)
                async for message in client.iter_messages(room_id, limit=50):
                    if message.date < time_limit:
                        break
                    
                    if message.text and len(message.text) > 20: # 너무 짧은 말은 제외
                        msg_time = message.date.strftime("%H:%M")
                        # 텍스트 길이 제한 (너무 긴 뉴스 하나가 토큰 다 잡아먹지 않게)
                        clean_text = message.text[:500] 
                        room_messages.append(f"[{room_name} | {msg_time}] {clean_text}")
                
                room_messages.reverse()
                
                if room_messages:
                    full_report_data.append(f"\n=== 🏠 {room_name} ===\n" + "\n".join(room_messages))
                else:
                    print(f"  -> {room_name}: 수집할 내용 없음")

            except Exception as e:
                print(f"🛑 {room_id} 접근 불가: {e}")
                continue

    final_text = "\n".join(full_report_data)
    
    if not final_text:
        print("수집된 내용이 없습니다. 봇이 방에 들어가 있는지 확인해주세요.")
        return

    print(f"데이터 수집 완료 ({len(final_text)}자). AI 요약 요청 중...")

    # ✅ 모델 변경: gemini-2.5-pro -> gemini-2.0-flash
    # (2.0 Flash는 무료 한도가 훨씬 높고 성능도 매우 좋습니다)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    너는 최고의 주식/경제 뉴스 큐레이터야.
    아래는 여러 주식 정보 채널에서 수집한 지난 24시간의 대화와 뉴스들이야.
    내용이 많으니 중복된 내용은 하나로 합치고, 가장 영양가 있는 정보만 골라서 브리핑해줘.

    [보고서 작성 양식]
    # ⚡️ 오늘의 핵심 주식/경제 브리핑 (Gemini 2.0)
    
    ## 1. 🔥 시장을 뜨겁게 달군 3가지 이슈
    * (가장 많이 언급되거나 중요한 이슈 3개 선정)

    ## 2. 📈 채널별 주요 정보 요약
    * **{full_report_data[0].split('===')[1].strip() if full_report_data else '방'} 등**: (각 채널에서만 나온 알짜 정보 요약)

    ## 3. 🧐 주목할만한 섹터/종목
    * (언급된 종목과 그 이유)

    ---
    [수집된 데이터]
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
                    if len(report_text) > 4000:
                        await client.send_message(CHAT_ID, report_text[:4000])
                        await client.send_message(CHAT_ID, report_text[4000:])
                    else:
                        await client.send_message(CHAT_ID, report_text)
                    print("★ 통합 요약 전송 완료!")
            except:
                print("AI 답변 형식 오류")
        else:
            print(f"AI 요청 실패: {response.text}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
