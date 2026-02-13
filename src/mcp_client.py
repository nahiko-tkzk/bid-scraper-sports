"""MCP接続・ツール呼び出し"""

import json
import logging
from datetime import datetime, timedelta

import requests

from .config import MCP_SERVER_URL, SEARCH_DAYS_BACK, MAX_RESULTS_PER_QUERY

logger = logging.getLogger(__name__)


def _build_cft_issue_date(days_back: int) -> str:
    """過去N日間の日付範囲文字列を生成する。"""
    today = datetime.now()
    start = today - timedelta(days=days_back)
    return f"{start.strftime('%Y-%m-%d')}/{today.strftime('%Y-%m-%d')}"


def _parse_sse_response(text: str) -> dict:
    """SSE形式のレスポンスからJSONを抽出する。"""
    for line in text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise ValueError("SSEレスポンスにdataフィールドがありません")


def search_bids(keyword: str, **params) -> list[dict]:
    """MCPサーバー経由でKKJ検索を実行する。

    Returns:
        正規化された検索結果のリスト
    """
    logger.info("MCP検索: keyword=%s", keyword)

    cft_date = params.get("cft_issue_date", _build_cft_issue_date(SEARCH_DAYS_BACK))
    count = params.get("count", MAX_RESULTS_PER_QUERY)

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "kkj-search",
            "arguments": {
                "query": keyword,
                "count": count,
                "cftIssueDate": cft_date,
            },
        },
    }

    resp = requests.post(
        MCP_SERVER_URL,
        json=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/event-stream",
        },
        timeout=30,
    )
    resp.raise_for_status()

    sse_data = _parse_sse_response(resp.text)

    if "error" in sse_data:
        raise RuntimeError(f"MCP error: {sse_data['error']}")

    content = sse_data["result"]["content"][0]["text"]
    result = json.loads(content)

    if result.get("isError"):
        raise RuntimeError(f"kkj-search error: {content}")

    hits = result.get("SearchHits", 0)
    logger.info("MCP検索結果: %d件ヒット (keyword=%s)", hits, keyword)

    return [_normalize(item) for item in result.get("SearchResult", [])]


def _normalize(item: dict) -> dict:
    """MCPレスポンスのフィールドを共通形式に変換する。"""
    return {
        "id": item.get("Key", ""),
        "title": item.get("ProjectName", ""),
        "organization": item.get("OrganizationName", ""),
        "prefecture": item.get("PrefectureName", ""),
        "city": item.get("CityName", ""),
        "category": item.get("Category", ""),
        "cft_issue_date": (item.get("CftIssueDate") or "")[:10],
        "url": item.get("ExternalDocumentURI", ""),
    }
