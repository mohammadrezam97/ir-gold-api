from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import asyncio
import logging

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Gold 18k Price API")

# آدرس کامل API tgju.org با پارامتر rev
API_URL = "https://call3.tgju.org/ajax.json?rev=qSWqGFf7BRyFsEb3KAxCatXkNmFEZgxCh6Y7HYGqZWVYsrt4hecUMX3e2"

# حافظه موقت برای ذخیره قیمت
gold_data = {
    "price": None,
    "high": None,
    "low": None,
    "change": None,
    "change_percent": None,
    "time": None
}

async def fetch_gold_price():
    """دریافت قیمت طلای ۱۸ عیار از tgju.org"""
    global gold_data
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(API_URL, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                g = data["current"]["retail_gerami"]  # کلید طلای ۱۸ عیار
                gold_data = {
                    "price": g["p"],
                    "high": g["h"],
                    "low": g["l"],
                    "change": g["d"],
                    "change_percent": g["dp"],
                    "time": g["t"]
                }
                logging.info(f"Updated gold price: {gold_data['price']}")
            else:
                logging.warning(f"Failed to fetch gold price, status: {resp.status_code}")
    except Exception as e:
        logging.error(f"Error fetching gold price: {e}")

# اجرای پس‌زمینه برای آپدیت هر ۳۰ ثانیه یکبار
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(fetch_gold_price()), "interval", seconds=30)
scheduler.start()

@app.on_event("startup")
async def startup_event():
    await fetch_gold_price()

@app.get("/gold18")
def get_gold18():
    return gold_data
