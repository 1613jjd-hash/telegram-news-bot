import os
import asyncio
import requests
import json
import time
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
    print(f"총 {len(SOURCE_CHANNEL_IDS)}개의 방 분석 시작 (Model: Gemini 3.0 Flash Preview)...")
    
    full_report_data = []

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        # ✅ [필수] 내 대화 목록 갱신 (이걸 해야 ID만으로 방을 찾을 수 있음)
        print("내 대화 목록 갱신 중... (Access Hash 확보)")
        await client.get_dialogs(limit=None) 

        time_limit = datetime.now(timezone.utc) - timedelta(hours=24)

        for room_id in SOURCE_CHANNEL_IDS:
            try:
                # 방 정보 가져오기
                entity = await client.get_entity(room_id)
                room_name = entity.title if hasattr(entity, 'title') else "알 수 없는 방"
                print(f"📥 수집 중: {room_name}")

                room_messages = []
                # Flash 모델은 처리 속도가 빠르므로 60개까지 수집
                async for message in client.iter_messages(room_id, limit=60):
                    if message.date < time_limit:
                        break
                    
                    if message.text and len(message.text) > 20: 
                        msg_time = message.date.strftime("%H:%M")
                        # 텍스트 길이 제한 
                        clean_text = message.text[:800] 
                        room_messages.append(f"[{room_name} | {msg_time}] {clean_text}")
                
                room_messages.reverse()
                
                if room_messages:
                    full_report_data.append(f"\n=== 🏠 {room_name} ===\n" + "\n".join(room_messages))
                else:
                    print(f"  -> {room_name}: 수집할 내용 없음")

            except Exception as e:
                print(f"⚠️ {room_id} 접근 불가: {e} (ID 확인 필요)")
                continue

    final_text = "\n".join(full_report_data)
    
    if not final_text:
        print("수집된 내용이 없습니다.")
        return

    print(f"데이터 수집 완료 ({len(final_text)}자). AI 요약 요청 중...")

    # ✅ [핵심 변경] 모델을 'gemini-3-flash-preview'로 설정
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    너는 금융/투자 분석 전문가야.
    아래는 여러 주식 정보 채널에서 수집한 지난 24시간의 대화와 뉴스들이야.
    내용이 방대하니 중복된 내용은 합치고, 투자자에게 가장 가치 있는 인사이트 위주로 브리핑해줘.

    [보고서 작성 양식]
    # ⚡️ 오늘의 핵심 주식/경제 브리핑 (Gemini 3.0)
    
    ## 1. 🔥 시장을 움직이는 핵심 테마 3
    * (단순 뉴스 나열보다, 시장에 미치는 영향 위주로 분석)

    ## 2. 📊 채널별 주요 정보 요약
    * **채널별 특징**: (각 방에서만 언급된 찌라시나 알짜 정보)

    ## 3. 🚀 주목할만한 섹터/종목
    * (종목명 - 선정 이유 간단히)

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
        # 요청 전 잠시 대기
        time.sleep(2)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            try:
                report_text = result['candidates'][0]['content']['parts'][0]['text']
                
                async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                    # 긴 메시지 분할 전송
                    if len(report_text) > 4000:
                        await client.send_message(CHAT_ID, report_text[:4000])
                        await client.send_message(CHAT_ID, report_text[4000:])
                    else:
                        await client.send_message(CHAT_ID, report_text)
                    print("★ 통합 요약 전송 완료!")
            except:
                print("AI 답변 파싱 실패 (응답 형식이 예상과 다름)")
                print(result) # 디버깅용 출력
        else:
            print(f"AI 요청 실패: {response.text}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
