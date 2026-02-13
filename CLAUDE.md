このプロジェクトは、官公需情報ポータルサイト検索APIを使って
スポーツ・アーバンスポーツ関連の入札情報を自動収集し、
Slackの #入札チャンネル (C0AF5TBN89X) に通知するツールです。

主な技術スタック:
- Python 3.10+
- MCP リモートサーバー: https://mcp.n-3.ai/mcp?tools=kkj-search
- フォールバック: http://www.kkj.go.jp/api/ （直接API）
- Slack Bot Token（chat.postMessage）
