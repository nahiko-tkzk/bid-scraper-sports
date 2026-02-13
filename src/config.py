"""設定・キーワード定義"""

import os
from dotenv import load_dotenv

load_dotenv()

# Slack設定
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C0AF5TBN89X")

# 検索設定
SEARCH_DAYS_BACK = int(os.getenv("SEARCH_DAYS_BACK", "7"))
MAX_RESULTS_PER_QUERY = int(os.getenv("MAX_RESULTS_PER_QUERY", "200"))

# MCP設定
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://mcp.n-3.ai/mcp?tools=kkj-search")

# ログレベル
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 検索キーワード
SEARCH_KEYWORDS = [
    "スポーツ",
    "アーバンスポーツ",
    "スケートボード",
    "BMX",
    "クライミング",
    "サーフィン",
    "ブレイキン",
    "体育館",
    "スポーツ施設",
    "運動公園",
]

# 送信済みID保存パス
SENT_IDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sent_ids.json")
