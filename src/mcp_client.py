"""MCP接続・ツール呼び出し"""

import logging
import requests

from .config import MCP_SERVER_URL

logger = logging.getLogger(__name__)


def search_bids(keyword: str, **params) -> list[dict]:
    """MCPサーバー経由でKKJ検索を実行する。

    Args:
        keyword: 検索キーワード
        **params: 追加の検索パラメータ

    Returns:
        検索結果のリスト
    """
    # TODO: MCPプロトコルに沿ったリクエスト実装
    logger.info("MCP検索: keyword=%s", keyword)
    raise NotImplementedError("MCP client is not yet implemented")
