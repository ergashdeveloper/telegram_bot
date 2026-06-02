import os
import json
import logging
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# === SOZLAMALAR ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"       # @BotFather dan olingan token
CHANNEL_ID = "@your_channel_name"       # Kanal username yoki -100xxxxxxxxxx
TIMEZONE = "Asia/Tashkent"              # O'zbekiston vaqti
SEND_HOUR = 21                          # Yuborish soati (21:00)
SEND_MINUTE = 0
DATA_FILE = "bot_data.json"
IMAGES_FOLDER = "images"               # Rasmlar saqlanadigan papka

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# === MA'LUMOTLAR BILAN ISHLASH ===

def load_data():
    """JSON fayldan ma'lumotlarni yuklash"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"sent_images": [], "all_images": []}

def save_data(data):
    """Ma'lumotlarni JSON faylga saqlash"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_next_image():
    """Keyingi yuborilmagan rasmni topish"""
    data = load_data()
    all_images = data.get("all_images", [])
    sent_images = data.get("sent_images", [])

    # Hali yuborilmagan rasmlar
    remaining = [img for img in all_images if img not in sent_images]

    if not remaining:
        logger.info("Barcha rasmlar yuborildi! Ro'yxat yangilanmoqda...")
        data["sent_images"] = []
        save_data(data)
        remaining = all_images

    if not remaining:
        logger.warning("Hech qanday rasm topilmadi!")
        return None

    # Tartibda birinchisini olish
    next_image = remaining[0]
    return next_image

def mark_as_sent(image_name):
    """Rasmni yuborilgan deb belgilash"""
    data = load_data()
    if image_name not in data["sent_images"]:
        data["sent_images"].append(image_name)
    save_data(data)

def scan_images_folder():
    """images/ papkasidagi rasmlarni skanerlash va ro'yxatga qo'shish"""
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

    logger.info(f"{len(images)} ta rasm topildi: {images}")
    return images


# === ASOSIY FUNKSIYALAR ===

async def send_daily_image(bot: Bot):
    """Kunlik rasm yuborish"""
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
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
            )
        mark_as_sent(image_name)
        logger.info(f"✅ Rasm yuborildi: {image_name}")

    except Exception as e:
        logger.error(f"❌ Rasm yuborishda xato: {e}")


# === BOT KOMANDALAR ===

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uchun /start komandasi"""
    data = load_data()
    total = len(data.get("all_images", []))
    sent = len(data.get("sent_images", []))
    remaining = total - sent

    await update.message.reply_text(
        f"🤖 Rasm yuborgich bot\n\n"
        f"📁 Jami rasmlar: {total}\n"
        f"✅ Yuborilgan: {sent}\n"
        f"⏳ Qolgan: {remaining}\n\n"
        f"⏰ Har kuni soat {SEND_HOUR:02d}:{SEND_MINUTE:02d} da yuboradi\n\n"
        f"Komandalar:\n"
        f"/status - Holat\n"
        f"/scan - Rasmlarni qayta skanerlash\n"
        f"/send_now - Hozir yuborish (test)"
    )

async def status_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Bot holati"""
    data = load_data()
    total = len(data.get("all_images", []))
    sent = len(data.get("sent_images", []))
    remaining = total - sent
    next_img = get_next_image()

    await update.message.reply_text(
        f"📊 Bot holati:\n\n"
        f"📁 Jami: {total} ta rasm\n"
        f"✅ Yuborilgan: {sent} ta\n"
        f"⏳ Qolgan: {remaining} ta\n"
        f"🔜 Keyingi: {next_img or 'Yo\'q'}"
    )

async def scan_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Rasmlarni qayta skanerlash"""
    images = scan_images_folder()
    await update.message.reply_text(
        f"🔍 Skanerland: {len(images)} ta rasm topildi\n\n"
        + "\n".join([f"  • {img}" for img in images]) if images else "❌ Rasm topilmadi"
    )

async def send_now_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Test uchun hozir yuborish"""
    await update.message.reply_text("📤 Rasm yuborilmoqda...")
    await send_daily_image(context.bot)
    await update.message.reply_text("✅ Yuborildi!")


# === ASOSIY ISHGA TUSHIRISH ===

def main():
    # images/ papkasini skanerlash
    scan_images_folder()

    # Applicationni yaratish
    app = Application.builder().token(BOT_TOKEN).build()

    # Komandalarni qo'shish
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("send_now", send_now_command))

    # Scheduler - har kuni 21:00 da yuborish
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

    # Botni ishga tushirish
    logger.info("🤖 Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
