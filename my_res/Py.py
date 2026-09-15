from functools import wraps
from telegram import Update 
from telegram.ext import ContextTypes

def get_message_type(message):
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


