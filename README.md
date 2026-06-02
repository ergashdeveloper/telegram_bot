# 📸 Kunlik Rasm Yuboruvchi Telegram Bot

Har kuni soat 21:00 da kanalga avtomatik rasm yuboradi.
31 ta rasm birin-ketin yuboriladi, takrorlanmaydi.

---

## 🛠 O'rnatish

### 1. Python o'rnatish
Python 3.10+ bo'lishi kerak.

### 2. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Bot yaratish (@BotFather)
1. Telegramda @BotFather ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `MyDailyPicsBot`)
4. Bot username kiriting (masalan: `my_daily_pics_bot`)
5. Olingan **TOKEN**ni nusxalab oling

### 4. `bot.py` faylini tahrirlash
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"  # Tokeningiz
CHANNEL_ID = "@your_channel"  # Kanalingiz username
```

**Kanal ID ni aniqlash:**
- Public kanal: `@kanal_nomi`
- Private kanal: `-1001234567890` (botni admin qiling, so'ng IDni oling)

### 5. Botni kanalga admin qilish
1. Kanalingizga kiring → Sozlamalar → Adminlar
2. Botingizni admin qiling
3. "Xabar yuborish" huquqini bering

### 6. Rasmlarni qo'shish
```
telegram_bot/
├── bot.py
├── requirements.txt
├── images/          ← Shu papkaga rasmlarni joylashtiring
│   ├── 01.jpg
│   ├── 02.jpg
│   ├── ...
│   └── 31.jpg
```

Rasmlar **alifbo tartibida** yuboriladi.
Tartibni nazorat qilish uchun raqam bilan nomlang: `01.jpg`, `02.jpg`, ...

### 7. Botni ishga tushirish
```bash
python bot.py
```

---

## 📋 Komandalar (Admin uchun)

| Komanda | Vazifasi |
|---------|----------|
| `/start` | Bot haqida ma'lumot |
| `/status` | Nechta yuborilgani, qanchasi qolganini ko'rish |
| `/scan` | Rasmlar papkasini qayta skanerlash |
| `/send_now` | Hoziroq rasm yuborish (test uchun) |

---

## ⚙️ Sozlamalar (`bot.py` ichida)

```python
TIMEZONE = "Asia/Tashkent"   # Vaqt zonasi
SEND_HOUR = 21               # Soat (21 = 21:00)
SEND_MINUTE = 0              # Daqiqa
IMAGES_FOLDER = "images"     # Rasmlar papkasi nomi
```

---

## 🔄 Qanday ishlaydi?

1. Bot `images/` papkasidagi barcha rasmlarni `bot_data.json` ga saqlaydi
2. Har kuni 21:00 da keyingi yuborilmagan rasmni oladi
3. Rasmni kanalga yuboradi va "yuborilgan" deb belgilaydi
4. 31 ta rasm tugagach, ro'yxat yangilanadi va boshidan boshlanadi

---

## 🖥 Serverda doim ishlab turishi uchun (Linux)

### screen yordamida:
```bash
screen -S telegram_bot
python bot.py
# Ctrl+A, keyin D - fonga o'tkazish
```

### systemd service:
```ini
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Daily Image Bot
After=network.target

[Service]
WorkingDirectory=/path/to/telegram_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

---

## ⚠️ Xatolar

| Xato | Yechim |
|------|--------|
| `Unauthorized` | Token noto'g'ri |
| `Chat not found` | CHANNEL_ID noto'g'ri yoki bot admin emas |
| Rasm topilmadi | `images/` papkasi bo'sh |
