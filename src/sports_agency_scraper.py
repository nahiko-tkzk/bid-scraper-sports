"""スポーツ庁 公募情報ページのスクレイピング"""

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import SEARCH_DAYS_BACK

logger = logging.getLogger(__name__)

BASE_URL = "https://www.mext.go.jp"
BOSHU_URL = f"{BASE_URL}/sports/b_menu/boshu/index.htm"

# 和暦→西暦の変換テーブル
_ERA_MAP = {
    "令和": 2018,
    "平成": 1988,
}

_DATE_RE = re.compile(
    r"(令和|平成)(\d+)年(\d+)月(\d+)日"
)


def _wareki_to_date(text: str) -> datetime | None:
    """和暦の日付文字列をdatetimeに変換する。"""
    m = _DATE_RE.search(text)
    if not m:
        return None
    era, year, month, day = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    offset = _ERA_MAP.get(era)
    if offset is None:
        return None
    return datetime(offset + year, month, day)


def _extract_id(href: str) -> str:
    """URLパスからID部分を抽出する（例: jsa_00395）。"""
    m = re.search(r"(jsa_\d+)", href)
    return m.group(1) if m else href.rstrip("/").split("/")[-1].replace(".htm", "").replace(".html", "")


def fetch_boshu(days_back: int = SEARCH_DAYS_BACK) -> list[dict]:
    """スポーツ庁の公募情報ページから案件を取得する。

    ページはdt（日付）/dd（リンク付きタイトル）のペアで構成されている。

    Returns:
        過去days_back日以内の案件リスト
    """
    logger.info("スポーツ庁公募ページ取得: %s", BOSHU_URL)

    resp = requests.get(BOSHU_URL, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, "html.parser")
    cutoff = datetime.now() - timedelta(days=days_back)

    results = []

    for dt in soup.find_all("dt"):
        date = _wareki_to_date(dt.get_text())
        if date is None:
            continue
        if date < cutoff:
            continue

        dd = dt.find_next_sibling("dd")
        if not dd:
            continue

        link = dd.find("a", href=True)
        if not link:
            continue

        href = link["href"]
        full_url = urljoin(BASE_URL, href)
        title = link.get_text(strip=True)
        item_id = _extract_id(href)

        results.append({
            "id": item_id,
            "title": title,
            "organization": "スポーツ庁",
            "prefecture": "東京都",
            "city": "",
            "category": "公募",
            "cft_issue_date": date.strftime("%Y-%m-%d"),
            "url": full_url,
        })

    logger.info("スポーツ庁公募: %d件取得（過去%d日間）", len(results), days_back)
    return results
