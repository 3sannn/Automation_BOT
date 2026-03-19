import gspread
import time
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

# ================= CONFIG =================
SHEET_ID = "13vRCGmd_uIH8Mx39WqXiU1cNDuJXea7v2ljsVwOstYs"
SERVICE_ACCOUNT_FILE = "E:/sheetapi.json"

# ================= GOOGLE SHEETS =================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ✅ FIXED: Use file instead of environment variable
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ================= GOOGLE ADS CHECK =================
def check_google_ads(page, query):
    try:
        page.goto("https://adstransparency.google.com/")
        page.wait_for_timeout(4000)

        page.fill("input", query)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        content = page.content().lower()

        if "no ads found" in content:
            return "No"
        else:
            return "Yes"

    except Exception as e:
        print("Google Ads Error:", e)
        return "Error"

# ================= META ADS CHECK =================
def check_meta_ads(page, query):
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&q={query}"

        page.goto(url)
        page.wait_for_timeout(6000)

        content = page.content().lower()

        if "no ads" in content:
            return "No"
        else:
            return "Yes"

    except Exception as e:
        print("Meta Ads Error:", e)
        return "Error"

# ================= MAIN LOOP =================
print("Bot started...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 👈 set False for debugging
    page = browser.new_page()

    while True:

        rows = sheet.get_all_values()

        for i in range(1, len(rows)):
            row_number = i + 1

            username = rows[i][1]        # Column B
            meta_status = rows[i][7]     # Column H
            google_status = rows[i][9]   # Column J

            if not username:
                continue

            # Skip already processed
            if meta_status and google_status:
                continue

            print(f"Checking row {row_number}: {username}")

            # 🔍 Meta Ads Check
            meta_result = check_meta_ads(page, username)
            sheet.update(f"H{row_number}", [[meta_result]])

            time.sleep(3)

            # 🔍 Google Ads Check
            google_result = check_google_ads(page, username)
            sheet.update(f"J{row_number}", [[google_result]])

            time.sleep(5)

        print("Cycle done. Waiting 5 minutes...")
        time.sleep(300)