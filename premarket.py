"""夜盤盤前快報

早上備援排程（台灣 06:37 / 07:17 / 08:07 / 08:47；RunLog 防重複）讀昨晚台指期夜盤
+ 昨日選股訊號，推播今日開盤方向預判與個股順風/逆風對照。

執行: uv run python premarket.py
"""

import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from stock_strategies.night_session import get_night_session
from stock_strategies.sheet import read_latest_signals, report_already_sent, mark_report_sent
from stock_strategies.notify import send_telegram, format_premarket
from stock_strategies.time_utils import taiwan_date_str


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

    report_date = taiwan_date_str()
    if report_already_sent("premarket", report_date):
        print(f"✅ {report_date} 盤前快報已推播過，略過重複排程")
        return

    # 1. 取得台指期夜盤
    print(f"[{datetime.now()}] 取得台指期夜盤...")
    night = get_night_session()
    if night:
        print(f"  → {night['date']} 夜盤 {night['pct']:+.2f}% ({night['label']})")
    else:
        print("  → 夜盤資料暫時取不到")

    # 2. 讀昨日訊號（沿用收盤後排程寫進 Signals 分頁的結果）
    #    讀 300 筆以涵蓋多日（單日掃描可能就數十筆 SKIP），
    #    format_premarket 會自動挑「最近一批有 BUY/WATCH」的日期。
    print("讀取昨日訊號...")
    try:
        signals = read_latest_signals(limit=300)
    except Exception as e:
        print(f"⚠️ 讀取訊號失敗: {e}", file=sys.stderr)
        signals = []
    print(f"  → {len(signals)} 筆")

    # 3. 發送 Telegram 盤前快報
    print("發送 Telegram 盤前快報...")
    send_telegram(format_premarket(night, signals))
    mark_report_sent("premarket", report_date)
    print("✅ 完成")


if __name__ == "__main__":
    main()
