"""メインスクリプト - 入札情報の収集と通知"""

import json
import logging
import os
import sys

from . import mcp_client, kkj_api_client, slack_notifier
from .config import SEARCH_KEYWORDS, SENT_IDS_PATH, LOG_LEVEL


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def load_sent_ids() -> set:
    """送信済みIDを読み込む。"""
    try:
        with open(SENT_IDS_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_sent_ids(sent_ids: set):
    """送信済みIDを保存する。"""
    os.makedirs(os.path.dirname(SENT_IDS_PATH), exist_ok=True)
    with open(SENT_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(sent_ids), f, ensure_ascii=False, indent=2)


def search(keyword: str) -> list[dict]:
    """MCP経由で検索し、失敗時はKKJ APIにフォールバックする。"""
    try:
        return mcp_client.search_bids(keyword)
    except Exception as e:
        logging.getLogger(__name__).warning("MCP検索失敗、フォールバック: %s", e)
        return kkj_api_client.search_bids(keyword)


def format_message(item: dict) -> str:
    """入札情報をSlack投稿用テキストに整形する。"""
    lines = [
        f"📋 *{item['title']}*",
        f"🏢 {item.get('organization', '不明')}",
        f"📍 {item.get('prefecture', '')} {item.get('city', '')}".strip(),
        f"📁 {item.get('category', '不明')}",
        f"📅 公告日: {item.get('cft_issue_date', '不明')}",
        f"🔗 {item.get('url', '')}",
    ]
    return "\n".join(lines)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("入札情報収集を開始します")

    sent_ids = load_sent_ids()
    new_items: list[dict] = []
    seen_ids: set[str] = set()

    # 全キーワードで検索し、重複排除しながら収集
    for keyword in SEARCH_KEYWORDS:
        try:
            results = search(keyword)
        except Exception as e:
            logger.error("検索失敗 keyword=%s: %s", keyword, e)
            continue

        logger.info("keyword=%s: %d件取得", keyword, len(results))

        for item in results:
            item_id = item.get("id")
            if not item_id:
                continue
            if item_id in sent_ids or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            new_items.append(item)

    logger.info("新着案件: %d件（重複排除済み）", len(new_items))

    # Slack通知
    notified = 0
    for item in new_items:
        text = format_message(item)
        try:
            slack_notifier.post_message(text)
            sent_ids.add(item["id"])
            notified += 1
        except Exception as e:
            logger.error("Slack通知失敗 id=%s: %s", item["id"], e)

    save_sent_ids(sent_ids)
    logger.info("完了: %d件の新着通知を送信しました", notified)


if __name__ == "__main__":
    main()
