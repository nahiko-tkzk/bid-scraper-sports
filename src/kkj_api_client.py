"""直接API呼び出し（フォールバック）"""

import logging
import requests

logger = logging.getLogger(__name__)

KKJ_API_BASE = "http://www.kkj.go.jp/api/"


def search_bids(keyword: str, **params) -> list[dict]:
    """KKJ APIに直接リクエストして検索する。

    Args:
        keyword: 検索キーワード
        **params: 追加の検索パラメータ

    Returns:
        検索結果のリスト
    """
    # TODO: KKJ API仕様に沿ったリクエスト実装
    logger.info("KKJ API検索: keyword=%s", keyword)
    raise NotImplementedError("KKJ API client is not yet implemented")
