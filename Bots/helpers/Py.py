from functools import wraps
from telegram import Update 
from telegram.ext import ContextTypes
import sqlite3

def get_message_type(message):
    if message is None:
        return "None"
    if message.text: return "text"
    elif message.photo: return "photo"
    elif message.video: return "video"
    elif message.document: return "document"
    elif message.voice: return "voice"
    elif message.audio: return "audio"
    elif message.sticker: return "sticker"
    elif message.location: return "location"
    elif message.contact: return "contact"
    else: return "unknown"

about_message = []

def getinfo(func):
    @wraps(func) 
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        user = msg.from_user
        
        info = {
            "text": msg.text,
            "date": str(msg.date),
            "type": get_message_type(msg),
            "user_id": user.id,
            "username": user.username
        }
        
        about_message.append(info)
        print("Logged Message Info:", info) 
        
        return await func(update, context)
        
    return wrapper




def create_tasks_table():
    DB_PATH = "Bots/bot_database.db"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

    # إنشاء جدول tasks مع ربطه بجدول users
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT NOT NULL,
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

    conn.commit()
    print("تم إنشاء جدول المهام (tasks) وربطه بالمستخدمين بنجاح!")


