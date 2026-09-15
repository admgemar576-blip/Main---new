import sqlite3
import asyncio
from telegram import Update ,InlineKeyboardButton , InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes , CallbackQueryHandler
from helpers.Py import get_message_type as gmt , getinfo as gi

DB_Path = "Bots/bot_database.db"
Token = "8697463306:AAHd5wJDu9E7vJFEs5qMn9XXw60XdXnjUBs"

async def save_user(user_id , username):
    with  sqlite3.connect(DB_Path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    print (f"{username} Saved in {user_id}")

@gi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user(update.effective_user.id , update.effective_user.first_name )
    await update.message.reply_text(f"You : {update.effective_user.username} , ID:{update.effective_user.id}")
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add", callback_data="btn_add"),
            InlineKeyboardButton("➖ Remove", callback_data="btn_remove"),
        ],
        [
            InlineKeyboardButton("📋 List", callback_data="btn_list")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.message.reply_text(
        "Wellcome to bisto_to_do list \n Select..." , reply_markup=reply_markup
    )

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def main ():
    Bot = Application.builder().token(Token).build()
    handel = Bot.add_handler
    print("Bot is running")
    
    handel(CommandHandler ("start" , start))
    handel(CommandHandler ("start" , start))
    handel(CallbackQueryHandler ("add-btn" , add_task))
    
    await Bot.initialize()
    await Bot.start()
    await Bot.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())