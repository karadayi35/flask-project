from flask import Flask, jsonify,render_template, url_for
from flask_cors import CORS
from telethon import TelegramClient, events
import asyncio
import threading
import time
import re

# Flask uygulaması
app = Flask(__name__)
CORS(app)

# Telegram API Bilgileri
api_id = '21745249'
api_hash = '89cf10c8782c9c54b671fc5736ddcf3b'
session_name = 'user_session'
group_id = -1001216775179  # Hedef grup ID'si

# Mesajları saklamak için bir liste
messages = []
filtered_messages = []  # Filtrelenmiş mesajlar için ayrı bir liste
bot_messages = []  # Botların düzenli mesajları için ayrı bir liste

@app.route("/")
def index():
    # icons dizisi
    icons = [
        url_for('static', filename='icons/icon1.png'),
        url_for('static', filename='icons/icon2.png'),
        url_for('static', filename='icons/icon3.png'),
        url_for('static', filename='icons/icon4.png'),
        url_for('static', filename='icons/icon5.png'),
        url_for('static', filename='icons/icon6.png')
    ]

    # bots dizisi
    bots = [
        { "name": "Academybot", "icon": url_for('static', filename='icons/moderator.png'),
          "message": "Telegram group: <a href='https://t.me/rouletteacademycanada'>Click</a>" },
        { "name": "StakeBot", "icon": url_for('static', filename='icons/slotticabot.png'),
          "message": "Best Casino Go: <a href='https://stake.com/?c=9dd9dbc553'>Click</a>" },
        { "name": "Slotticabot", "icon": url_for('static', filename='icons/slotticabot.png'),
          "message": "Best Casino Go: <a href='https://gopartner.link/?a=205678&c=184089&s1=6028'>Click</a>" },
        { "name": "BetsioBot", "icon": url_for('static', filename='icons/slotticabot.png'),
          "message": "Best Casino Go: <a href='https://t.ly/9-D_G'>Click</a>" }
    ]

    return render_template("index.html", icons=icons, bots=bots)
@app.route("/get_messages", methods=["GET"])
def get_messages():
    """JSON formatında mesajları döndür."""
    global filtered_messages
    return jsonify(filtered_messages)

def is_valid_message(message_text):
    """
    Mesajın geçerli olup olmadığını kontrol eder.
    - İçerik bağlantı içeriyorsa (https://, t.me, vb.) False döner.
    """
    if re.search(r'(https?://|t\.me)', message_text):  # Bağlantı içerikleri filtrele
        return False
    return True

async def fetch_messages():
    """Telegram'dan mesajları sürekli çeken fonksiyon."""
    global messages, filtered_messages
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("Telegram'a bağlanıldı!")

        @client.on(events.NewMessage(chats=group_id))
        async def handler(event):
            # Mesajı atan kullanıcı bilgilerini al
            sender = await event.get_sender()
            username = sender.username or sender.first_name or "Anonim"
            message_text = event.message.text

            # Eğer mesajı atan 'Coolestbot' ise, mesajı alma
            if username == "Coolestbot":
                return

            # Mesajın geçerliliğini kontrol et
            if not is_valid_message(message_text):
                print(f"Geçersiz mesaj atlandı: {message_text}")
                return

            # Mesajı listeye ekle
            new_message = {
                "author": username,
                "content": message_text
            }
            messages.append(new_message)
            print(f"Yeni mesaj alındı: {username} - {message_text}")

        await client.run_until_disconnected()

def process_messages():
    """Mesajları 3 saniye arayla işleyen fonksiyon."""
    global messages, filtered_messages
    while True:
        if messages:
            message = messages.pop(0)  # İlk mesajı listeden al
            filtered_messages.append(message)  # Filtrelenmiş mesajlar listesine ekle
            print(f"Mesaj işlendi: {message['content']}")
        time.sleep(6)  # Her mesaj arasında 6 saniye bekle

def start_fetching():
    """Telegram mesajlarını çekmeyi başlat."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_messages())

if __name__ == "__main__":
    # Telegram mesajlarını ayrı bir thread'de çek
    thread = threading.Thread(target=start_fetching)
    thread.start()

    # Mesaj işleme fonksiyonunu ayrı bir thread'de çalıştır
    process_thread = threading.Thread(target=process_messages)
    process_thread.start()

    # Flask API'yi başlat
    app.run(host="0.0.0.0", port=5000)
