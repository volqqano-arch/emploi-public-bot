import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random

# CONFIG
URL = "https://www.emploi-public.ma/fr/concours-liste"
TELEGRAM_TOKEN = "8433126797:AAGkkozkRrOqAZUHNIqptIKHbGYkTCvkEw8"
CHAT_ID = "8419252694"
HISTORY_FILE = "seen_jobs.json"

# Human-like headers
HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ])
}

# Send Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, data=data)
    print("Telegram status:", r.status_code)
    time.sleep(random.uniform(1, 3))  # human-like pause

# Load saved jobs
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Save seen jobs
def save_history(jobs):
    with open(HISTORY_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

# Scraper logic
def scrape():
    print("Starting scrape...")
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    seen_jobs = load_history()
    current_jobs = []
    new_jobs = []

    items = soup.select("div.s-item a.card")
    print(f"Found {len(items)} concours cards")

    for a in items:
        title_tag = a.select_one("h2.card-title")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        href = a.get("href")
        if not href:
            continue
        job_id = href  # unique by href
        current_jobs.append(job_id)
        if job_id not in seen_jobs:
            full_link = "https://www.emploi-public.ma" + href
            msg = f"🚨 *Nouveau Concours*\n\n*{title}*\n[Voir l'annonce]({full_link})"
            new_jobs.append(msg)
            if len(new_jobs) >= 3:  # limit per run to be human-like
                break

    for msg in new_jobs:
        send_telegram(msg)

    if new_jobs:
        save_history(current_jobs)
        print(f"Sent {len(new_jobs)} new job alerts")
    else:
        print("No new jobs found")

if __name__ == "__main__":
    scrape()
