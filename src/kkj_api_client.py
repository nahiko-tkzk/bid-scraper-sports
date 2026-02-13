"""直接API呼び出し（フォールバック）"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from .config import SEARCH_DAYS_BACK, MAX_RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

KKJ_API_BASE = "http://www.kkj.go.jp/api/"

# XMLで返却されるフィールドの想定タグ名
_FIELD_MAP = {
    "Key": "id",
    "ProjectName": "title",
    "OrganizationName": "organization",
    "PrefectureName": "prefecture",
    "CityName": "city",
    "Category": "category",
    "CftIssueDate": "cft_issue_date",
    "ExternalDocumentURI": "url",
}


def _build_date_range(days_back: int) -> tuple[str, str]:
    today = datetime.now()
    start = today - timedelta(days=days_back)
    return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def search_bids(keyword: str, **params) -> list[dict]:
    """KKJ APIに直接リクエストして検索する。

    Returns:
        正規化された検索結果のリスト
    """
    logger.info("KKJ API検索: keyword=%s", keyword)

    date_from, date_to = _build_date_range(SEARCH_DAYS_BACK)

    query_params = {
        "Query": keyword,
        "Count": params.get("count", MAX_RESULTS_PER_QUERY),
        "CFT_Issue_Date": f"{date_from}/{date_to}",
    }

    resp = requests.get(KKJ_API_BASE, params=query_params, timeout=30)
    resp.raise_for_status()

    return _parse_xml(resp.text)


def _parse_xml(xml_text: str) -> list[dict]:
    """XMLレスポンスをパースして共通形式のリストに変換する。"""
    results = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.error("XMLパース失敗: %s", e)
        return results

    for item_elem in root.iter("item"):
        item = {}
        for xml_tag, norm_key in _FIELD_MAP.items():
            elem = item_elem.find(xml_tag)
            value = elem.text.strip() if elem is not None and elem.text else ""
            if norm_key == "cft_issue_date":
                value = value[:10]
            item[norm_key] = value
        if item.get("id"):
            results.append(item)

    logger.info("KKJ API検索結果: %d件取得", len(results))
    return results
