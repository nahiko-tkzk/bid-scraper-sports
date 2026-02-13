# bid-scraper-sports

スポーツ・アーバンスポーツ関連の入札情報を自動収集し、Slackに通知するツール。

## 概要

官公需情報ポータルサイト（KKJ）の検索APIを使って、スポーツ関連の入札・公募情報を定期的に収集し、Slackチャンネルに通知します。

## セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集してSlack Bot Tokenなどを設定
```

## 使い方

```bash
python -m src.bid_scraper
```

## 構成

```
src/
  bid_scraper.py      - メインスクリプト
  mcp_client.py       - MCP接続・ツール呼び出し
  kkj_api_client.py   - 直接API呼び出し（フォールバック）
  slack_notifier.py   - Slack投稿ロジック
  config.py           - 設定・キーワード定義
data/
  sent_ids.json       - 重複通知防止用（自動生成）
```
