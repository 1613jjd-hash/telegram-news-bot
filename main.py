name: Daily Crypto Briefing

on:
  schedule:
    - cron: '0 0 * * *'  # 매일 아침 9시(한국시간) 자동 실행
  workflow_dispatch:      # 수동 실행 버튼 활성화

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install telethon google-generativeai

      - name: Run script
        env:
          API_ID: ${{ secrets.API_ID }}
          API_HASH: ${{ secrets.API_HASH }}
          SESSION_STRING: ${{ secrets.SESSION_STRING }}
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python main.py
