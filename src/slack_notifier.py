"""Slack投稿ロジック"""

import logging
import requests

from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

logger = logging.getLogger(__name__)

SLACK_POST_URL = "https://slack.com/api/chat.postMessage"


def post_message(text: str, channel: str = SLACK_CHANNEL_ID) -> dict:
    """Slackチャンネルにメッセージを投稿する。

    Args:
        text: 投稿するメッセージ本文
        channel: 投稿先チャンネルID

    Returns:
        Slack APIのレスポンス
    """
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "channel": channel,
        "text": text,
    }
    resp = requests.post(SLACK_POST_URL, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        logger.error("Slack投稿失敗: %s", data.get("error"))
    return data
