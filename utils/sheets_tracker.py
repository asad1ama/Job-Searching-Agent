from utils.logger import setup_logger
import json, os

logger = setup_logger()

class SheetsTracker:
    def __init__(self):
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not self.sheet_id:
            raise ValueError("GOOGLE_SHEET_ID not set")

    def log_jobs(self, results: list):
        from datetime import datetime
        import gspread
        from google.oauth2.service_account import Credentials

        creds_path = os.getenv("GOOGLE_CREDS_PATH", "config/google_creds.json")
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(self.sheet_id).sheet1

        today = datetime.now().strftime("%Y-%m-%d")
        rows = []
        for r in results:
            rows.append([
                r.get("platform", ""),
                r.get("title", ""),
                r.get("company", ""),
                r.get("location", ""),
                r.get("match_score", ""),
                r.get("status", "ready_to_apply"),
                r.get("url", ""),
                today,
            ])

        sheet.append_rows(rows)
        logger.info(f"  ✅ Logged {len(rows)} jobs to Google Sheets")