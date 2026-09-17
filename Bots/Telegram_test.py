import sqlite3
import asyncio
from telegram import Update ,InlineKeyboardButton , InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes , CallbackQueryHandler,ConversationHandler ,MessageHandler ,filters
import re

DB_Path = "Bots/bot_database.db"
Token = "8697463306:AAHd5wJDu9E7vJFEs5qMn9XXw60XdXnjUBs"
WAITING_FOR_TASK ,WAITING_FOR_REMOVE = range(2)

async def save_user(user_id , username):
    with  sqlite3.connect(DB_Path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    print (f"Try {username} Saved in {user_id}.....")

async def save_task(user_id ,task_name,date):
    with  sqlite3.connect(DB_Path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (user_id,task,date) VALUES (?,?,?)" , (user_id,task_name,date)
            )
        conn.commit()
    print(f"Try Task saved from {user_id} in {date}......")

async def get_tasks(user_id):
    with  sqlite3.connect(DB_Path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = ?" , (user_id,)
        )
        return list(cursor.fetchall())

async def remove_task(task_id):
    with  sqlite3.connect(DB_Path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE id = ?" ,(task_id,)
        )
    print (f"Try delete Task {task_id}...... ")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update,context,update.message.reply_text, True)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE ,rep,isrep):
    try:
        await save_user(update.effective_user.id , update.effective_user.first_name )
        print("Saved !")
    except Exception as e:
        print(f"Failed : {e}")

    
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

    if isrep:
        await rep(
            "Wellcome to bisto_to_do list \n Select..." , reply_markup=reply_markup
    )

async def start_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text("write the task or '/cancel' to cancel this process ")
    
    print(f"User {query.from_user.id} Wants to add task")
    return WAITING_FOR_TASK


async def receive_task_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_name = update.message.text 
    id = update.message.from_user.id
    date = update.message.date
    
    try:
        await save_task(id,task_name,date)
        print(f"Saved Successfully :{id}")
        await update.message.reply_text("Your task saved successfully")
    
    except Exception as e:
        print(f"unsaved Error {e} :{id}")
        await update.message.reply_text("Error happend while saving your task , please try again")
    
    
    return await end_conv(update,context,update.message.reply_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Process Canceled .")
    return ConversationHandler.END

async def getlist(update: Update, context: ContextTypes.DEFAULT_TYPE, isrep=True):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    tasks = await get_tasks(user_id)
    
    
    mas =""
    for c,task in enumerate(tasks):
        mas+=f"Task ({c+1}) : {task[2]} \n Date : {task[3]}\n"
        mas+='*'*50
        mas+='\n\n'
    
    rep=update.callback_query.message.reply_text
    await rep(mas) if mas else await rep("You don't  have tasks")
    
    print(f"{user_id} get his list {tasks}")

    await menu(update,context,update.callback_query.message.reply_text,isrep)

async def start_remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    await getlist(update,context,False)
    
    tasks = await get_tasks(user_id)
    task_num = len(tasks)

    keyboard = []

    for i in range(1, task_num + 1):

        button = InlineKeyboardButton(f"Task ({i})", callback_data=f"task_{tasks[i-1][0]}")
        
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text("Select Task to remove :", reply_markup=reply_markup)
    
    print(f"{user_id}: Want to delete task")
    return WAITING_FOR_REMOVE

async def removing_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    clicked_data = query.data  
    if not re.match(r"^task_\d+$", clicked_data):
        await query.message.reply_text("Please Select task to delete or '/cancel' to cancel ")
        return WAITING_FOR_REMOVE
    task_id = clicked_data[5:]

    try:
        await remove_task(task_id)
        await query.message.reply_text("Task Deleted!")
        print(f"Task deleted {task_id}")

    except Exception as e:
        print(f"Error While deleting message {e}")
        await query.message.reply_text("Failed to delete task , Please try again")

    return await end_conv(update,context,query.message.reply_text)

async def end_conv(update:Update,context,rep):
    await menu(update,context,rep,True)
    return ConversationHandler.END




async def main ():
    Bot = Application.builder().token(Token).build()
    handel = Bot.add_handler
    print("Bot is running")
    
    
    addremove_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_task, pattern="btn_add"),
            CallbackQueryHandler(start_remove_task, pattern="btn_remove")
        ],
        states={
            WAITING_FOR_TASK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_task_text)
            ],
            
            WAITING_FOR_REMOVE: [
                CallbackQueryHandler(removing_task)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )
    
    handel(addremove_handler)
    handel(CommandHandler ("start" , start))
    handel(CommandHandler ("start" , start))
    handel(CallbackQueryHandler(getlist,"btn_list"))
    
    
    await Bot.initialize()
    await Bot.start()
    await Bot.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())