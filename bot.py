import os
import json
import logging
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# === SOZLAMALAR ===
BOT_TOKEN = os.environ.get("8951465330:AAH5RLqC_R44Mac0fkmUiGeBvRx1WMgjJ9A")        # Railway Variables dan o'qiladi
CHANNEL_ID = os.environ.get("1002889671666")      # Masalan: -1001234567890
TIMEZONE = "Asia/Tashkent"
SEND_HOUR = 21
SEND_MINUTE = 0
DATA_FILE = "bot_data.json"
IMAGES_FOLDER = "images"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# === MA'LUMOTLAR BILAN ISHLASH ===

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"sent_images": [], "all_images": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def scan_images_folder():
    if not os.path.exists(IMAGES_FOLDER):
        os.makedirs(IMAGES_FOLDER)
        logger.info(f"'{IMAGES_FOLDER}' papkasi yaratildi")
        return []

    supported = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
    images = sorted([
        f for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith(supported)
    ])

    data = load_data()
    data["all_images"] = images
    save_data(data)
    logger.info(f"{len(images)} ta rasm topildi")
    return images

def get_next_image():
    data = load_data()
    all_images = data.get("all_images", [])
    sent_images = data.get("sent_images", [])
    remaining = [img for img in all_images if img not in sent_images]

    if not remaining:
        logger.info("Barcha rasmlar yuborildi! Ro'yxat yangilanmoqda...")
        data["sent_images"] = []
        save_data(data)
        remaining = all_images

    if not remaining:
        logger.warning("Hech qanday rasm topilmadi!")
        return None

    return remaining[0]

def mark_as_sent(image_name):
    data = load_data()
    if image_name not in data["sent_images"]:
        data["sent_images"].append(image_name)
    save_data(data)


# === ASOSIY FUNKSIYA ===

async def send_daily_image(bot: Bot):
    image_name = get_next_image()
    if not image_name:
        logger.error("Yuborish uchun rasm topilmadi!")
        return

    image_path = os.path.join(IMAGES_FOLDER, image_name)
    if not os.path.exists(image_path):
        logger.error(f"Rasm fayli topilmadi: {image_path}")
        return

    try:
        with open(image_path, "rb") as photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo)
        mark_as_sent(image_name)
        logger.info(f"✅ Rasm yuborildi: {image_name}")
    except Exception as e:
        logger.error(f"❌ Xato: {e}")


# === KOMANDALAR ===

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    total = len(data.get("all_images", []))
    sent = len(data.get("sent_images", []))
    await update.message.reply_text(
        f"🤖 Rasm yuborgich bot\n\n"
        f"📁 Jami rasmlar: {total}\n"
        f"✅ Yuborilgan: {sent}\n"
        f"⏳ Qolgan: {total - sent}\n\n"
        f"⏰ Har kuni {SEND_HOUR:02d}:{SEND_MINUTE:02d} da yuboradi\n\n"
        f"Komandalar:\n"
        f"/status - Holat\n"
        f"/scan - Rasmlarni qayta skanerlash\n"
        f"/send\\_now - Hozir yuborish (test)"
    )

async def status_command(update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    total = len(data.get("all_images", []))
    sent = len(data.get("sent_images", []))
    next_img = get_next_image()
    await update.message.reply_text(
        f"📊 Bot holati:\n\n"
        f"📁 Jami: {total} ta rasm\n"
        f"✅ Yuborilgan: {sent} ta\n"
        f"⏳ Qolgan: {total - sent} ta\n"
        f"🔜 Keyingi: {next_img or 'Yo\\'q'}"
    )

async def scan_command(update, context: ContextTypes.DEFAULT_TYPE):
    images = scan_images_folder()
    if images:
        text = f"🔍 {len(images)} ta rasm topildi:\n\n" + "\n".join([f"  • {img}" for img in images])
    else:
        text = "❌ Rasm topilmadi. 'images/' papkasiga rasm qo'shing."
    await update.message.reply_text(text)

async def send_now_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Rasm yuborilmoqda...")
    await send_daily_image(context.bot)
    await update.message.reply_text("✅ Bajarildi!")


# === ISHGA TUSHIRISH ===

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi! Railway Variables ga qo'shing.")
        return
    if not CHANNEL_ID:
        logger.error("❌ CHANNEL_ID topilmadi! Railway Variables ga qo'shing.")
        return

    scan_images_folder()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("send_now", send_now_command))

    scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))
    scheduler.add_job(
        send_daily_image,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
        args=[app.bot],
        id="daily_image",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"⏰ Scheduler ishga tushdi: har kuni {SEND_HOUR:02d}:{SEND_MINUTE:02d} da yuboradi")

    logger.info("🤖 Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
