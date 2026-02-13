"""メインスクリプト - 入札情報の収集と通知"""

import json
import logging
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
            return set(json.load(f).keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_sent_ids(sent_ids: set):
    """送信済みIDを保存する。"""
    data = {id_: True for id_ in sent_ids}
    with open(SENT_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def search(keyword: str) -> list[dict]:
    """MCP経由で検索し、失敗時はKKJ APIにフォールバックする。"""
    try:
        return mcp_client.search_bids(keyword)
    except Exception as e:
        logging.getLogger(__name__).warning("MCP検索失敗、フォールバック: %s", e)
        return kkj_api_client.search_bids(keyword)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("入札情報収集を開始します")

    sent_ids = load_sent_ids()
    new_count = 0

    for keyword in SEARCH_KEYWORDS:
        try:
            results = search(keyword)
        except Exception as e:
            logger.error("検索失敗 keyword=%s: %s", keyword, e)
            continue

        for item in results:
            item_id = item.get("id")
            if not item_id or item_id in sent_ids:
                continue

            # TODO: メッセージフォーマットを整える
            text = f"【新着入札】{item.get('title', '不明')}\n{item.get('url', '')}"
            try:
                slack_notifier.post_message(text)
                sent_ids.add(item_id)
                new_count += 1
            except Exception as e:
                logger.error("Slack通知失敗 id=%s: %s", item_id, e)

    save_sent_ids(sent_ids)
    logger.info("完了: %d件の新着通知を送信しました", new_count)


if __name__ == "__main__":
    main()
