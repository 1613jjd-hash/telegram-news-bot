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
    print(f"🔥 실전 데이트레이딩 분석 시작 (Model: Gemini 3.0 Flash Preview)...")
    
    full_report_data = []

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        # [필수] 내 대화 목록 갱신 (ID 매칭을 위해 필수)
        print("🔍 채널 접속 권한 갱신 중...")
        await client.get_dialogs(limit=None) 

        # 데이트레이딩은 최신성이 생명이므로 지난 12시간 데이터만 집중 분석 (시간 단축 및 정확도 향상)
        time_limit = datetime.now(timezone.utc) - timedelta(hours=12)

        for room_id in SOURCE_CHANNEL_IDS:
            try:
                entity = await client.get_entity(room_id)
                room_name = entity.title if hasattr(entity, 'title') else "알 수 없는 방"
                print(f"📥 수집 중: {room_name}")

                room_messages = []
                # 최근 12시간 내의 핵심 메시지 50개만 수집
                async for message in client.iter_messages(room_id, limit=50):
                    if message.date < time_limit:
                        break
                    
                    # 너무 짧은 잡담은 제외, 뉴스나 정보성 텍스트만
                    if message.text and len(message.text) > 30: 
                        msg_time = message.date.strftime("%H:%M")
                        # 텍스트 전처리 (너무 긴 공시 내용은 앞부분만)
                        clean_text = message.text[:600] 
                        room_messages.append(f"[{room_name} | {msg_time}] {clean_text}")
                
                room_messages.reverse()
                
                if room_messages:
                    full_report_data.append(f"\n=== 📡 {room_name} 수집 데이터 ===\n" + "\n".join(room_messages))
                else:
                    print(f"  -> {room_name}: 최근 12시간 내 중요 데이터 없음")

            except Exception as e:
                print(f"⚠️ {room_id} 접근 실패: {e}")
                continue

    final_text = "\n".join(full_report_data)
    
    if not final_text:
        print("수집된 내용이 없습니다.")
        return

    print(f"📊 데이터 확보 완료 ({len(final_text)}자). 트레이딩 전략 수립 중...")

    # ✅ 모델: Gemini 3.0 Flash Preview (최신 성능)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"
    
    # 🔥 [전문가 프롬프트] 데이트레이더의 시각을 주입
    prompt = f"""
    당신은 월스트리트 헤지펀드 출신의 수석 데이트레이더이자 시장 심리 분석가입니다.
    당신의 목표는 수집된 텔레그램 찌라시와 뉴스들 속에서 '내일 당장 주가를 움직일 강력한 재료(Catalyst)'를 찾아내는 것입니다.
    
    단순한 요약은 필요 없습니다. 트레이더가 매매에 참고할 수 있는 '돈이 되는 정보'만 걸러내세요.
    잡담, 의미 없는 인사, 이미 반영된 낡은 뉴스는 과감히 무시하세요.

    [분석 요구사항]
    1. **공격적이고 직관적인 어조**로 작성하세요.
    2. 모든 종목명이나 섹터명은 **볼드체**로 강조하세요. (예: **삼성전자**, **2차전지**)
    3. 찌라시의 신뢰도를 스스로 판단하여, 단순 루머인지 팩트인지 구분하세요.

    ---
    [작성 양식]

    # 🚨 MARKET ALPHA REPORT (Date: {datetime.now().strftime('%m/%d')})

    ## 1. 💎 오늘/내일의 주도 섹터 및 테마 (Strongest Momentum)
    * **(섹터명)**: (상승 이유와 관련 대장주 나열. 예: **에코프로** 실적 발표 기대감으로 수급 쏠림)
    * **(섹터명)**: (관련 뉴스 요약)

    ## 2. 🔥 당장 주목해야 할 개별 종목 (Hot Tickers)
    * 🎯 **종목명**: (핵심 재료 한 줄 요약) - *예상 파급력: 상/중/하*
    * 🎯 **종목명**: (핵심 재료 한 줄 요약) - *예상 파급력: 상/중/하*
    * 🎯 **종목명**: (핵심 재료 한 줄 요약) - *예상 파급력: 상/중/하*

    ## 3. 💬 시장의 찐 바닥 민심 (Sentiment Check)
    * (채널 참여자들의 대화 분위기를 통해 현재 시장이 탐욕 구간인지, 공포 구간인지 분석. 예: "폭락장에 다들 패닉 상태", "특정 테마에만 광적으로 집착 중")

    ## 4. ⚠️ 주의/악재 뉴스 (Risk Alert)
    * (유상증자, 블록딜, CEO 리스크 등 피해야 할 종목이나 악재)

    ---
    [Raw Data Source]
    {final_text}
    """

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        # 쿼터 제한 방지를 위한 대기
        time.sleep(2)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            try:
                report_text = result['candidates'][0]['content']['parts'][0]['text']
                
                async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                    # 메시지 길이 처리
                    if len(report_text) > 4000:
                        await client.send_message(CHAT_ID, report_text[:4000])
                        await client.send_message(CHAT_ID, report_text[4000:])
                    else:
                        await client.send_message(CHAT_ID, report_text)
                    print("★ 트레이딩 리포트 전송 완료!")
            except:
                print("AI 응답 형식 에러")
        else:
            print(f"AI 요청 실패: {response.text}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
