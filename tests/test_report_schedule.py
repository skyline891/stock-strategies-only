from datetime import datetime, timezone

import gspread

from stock_strategies import sheet
from stock_strategies.time_utils import taiwan_date_str


class FakeWorksheet:
    def __init__(self):
        self.rows = []

    def get_all_values(self):
        return self.rows

    def append_row(self, row):
        self.rows.append(row)

    def get_all_records(self):
        if not self.rows:
            return []
        headers = self.rows[0]
        return [dict(zip(headers, row)) for row in self.rows[1:]]


class FakeSpreadsheet:
    def __init__(self):
        self.sheets = {}

    def worksheet(self, name):
        if name not in self.sheets:
            raise gspread.WorksheetNotFound(name)
        return self.sheets[name]

    def add_worksheet(self, title, rows, cols):
        ws = FakeWorksheet()
        self.sheets[title] = ws
        return ws


def test_taiwan_date_uses_market_timezone_for_early_utc_run():
    utc_run_time = datetime(2026, 6, 22, 21, 37, tzinfo=timezone.utc)
    assert taiwan_date_str(utc_run_time) == "2026-06-23"


def test_report_log_marks_report_sent_once(monkeypatch):
    fake = FakeSpreadsheet()
    monkeypatch.setattr(sheet, "get_gsheet", lambda: fake)

    assert sheet.report_already_sent("premarket", "2026-06-23") is False

    sheet.mark_report_sent(
        "premarket",
        "2026-06-23",
        sent_at="2026-06-23T06:37:00+08:00",
    )

    assert sheet.report_already_sent("premarket", "2026-06-23") is True
    assert fake.worksheet("RunLog").rows == [
        sheet.RUN_LOG_HEADERS,
        ["premarket", "2026-06-23", "SENT", "2026-06-23T06:37:00+08:00"],
    ]
