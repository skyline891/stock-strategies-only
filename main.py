"""
V3.0 每日選股訊號系統

執行: uv run python main.py
"""

import os
import sys
import time
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from stock_strategies.sheet import read_watchlist, append_signals
from stock_strategies.evaluate import evaluate
from stock_strategies.notify import send_telegram, format_messages


REQUIRED_ENV = [
    "FINMIND_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "GOOGLE_SHEET_ID",
    "GOOGLE_CREDS_JSON",
]


def main():
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        print(f"❌ 缺少環境變數: {missing}", file=sys.stderr)
        sys.exit(1)

    print(f"[{datetime.now()}] 讀取 watchlist...")
    watchlist = read_watchlist()
    print(f"  → {len(watchlist)} 檔啟用中")

    results = []
    for i, row in enumerate(watchlist, 1):
        sid = str(row["stock_id"])
        name = row.get("name", "")
        print(f"[{i}/{len(watchlist)}] {sid} {name}")
        r = evaluate(sid, name)
        if r:
            results.append(r)
        time.sleep(0.6)

    order = {"BUY": 0, "WATCH": 1, "SKIP": 2, "ERROR": 3}
    results.sort(key=lambda x: (order.get(x.get("action"), 4), -x.get("signal_score", 0)))

    print(f"\n{sum(1 for r in results if r['action']=='BUY')} BUY, "
          f"{sum(1 for r in results if r['action']=='WATCH')} WATCH")

    print("寫回 Google Sheet...")
    append_signals(results)

    print("發送 Telegram...")
    for msg in format_messages(results, watchlist):
        send_telegram(msg)
        time.sleep(0.5)

    print("✅ 完成")


if __name__ == "__main__":
    main()
