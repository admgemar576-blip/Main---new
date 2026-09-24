import sqlite3
import asyncio
from telegram import Update ,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes ,CallbackQueryHandler
from functools import wraps

# ==================== (Database) ====================
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_tables()

    def init_tables(self):
        """إنشاء الجداول تلقائياً عند بدء التشغيل"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # جدول المنتجات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products(
                    id INTEGER PRIMARY KEY, 
                    code TEXT NOT NULL UNIQUE, 
                    price DECIMAL(10, 2) NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL, 
                    rate REAL,
                    isactive BOOLEAN DEFAULT 1, 
                    image BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # جدول المستخدمين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE,
                    address TEXT,
                    national_id_image BLOB, 
                    role TEXT CHECK(role IN ('admin', 'seller', 'customer')) NOT NULL DEFAULT 'customer',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );           
            """)
            
            # جدول الطلبات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL, 
                    seller_id INTEGER,   
                    product_id INTEGER NOT NULL,  
                    quantity_bought INTEGER NOT NULL, 
                    total_price DECIMAL(10, 2) NOT NULL,    
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id),
                    FOREIGN KEY (seller_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
            """)
            conn.commit()

    def check_role(self, telegram_id: int) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
            role = cursor.fetchone()
            return str(role[0]).upper() if role else "NONE"

    def save_user(self, telegram_id: int, username: str, phone: str = None, role: str = "customer"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (telegram_id, name, role, phone) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET name=excluded.name
                """, 
                (telegram_id, username, role, phone)
            )
            conn.commit()

    def get_user_data(self,tel_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE telegram_id = ? " ,(tel_id,)
            )
            
            return cursor.fetchone()

# ====================  (BaseBot) ====================
class BaseBot:
    def __init__(self, token: str, db_manager: DatabaseManager):
        self.token = token
        self.db = db_manager
        self.app = Application.builder().token(self.token).build()
        self.register_handlers()

    def register_handlers(self):
        """تُستخدم لتسجيل الأوامر المشتركة (تُعَدّل في الأبناء)"""
        pass

    async def start(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()


# ==================== (CustomerBot) ====================
class CustomerBot(BaseBot):
    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.bot_start))
        self.app.add_handler(CommandHandler("shop", self.shop_list))

    async def bot_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.db.save_user(user.id, user.first_name, role="customer")
        
        role = self.db.check_role(user.id)
        
        if role in ["SELLER", "ADMIN"]:
            await update.message.reply_text(f"Hello {role} {user.first_name}!")
        elif role == "CUSTOMER":
            await update.message.reply_text(f"Welcome {user.first_name} to our shop, check new items! '/shop' ")
        else:
            await update.message.reply_text(f"Welcome {user.first_name} to our shop, you can provide info to register.")


# ====================  BaseBot (AdminBot) ====================
class AdminBot(BaseBot):
    
    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.admin_start))
        #self.app.add_handler(CommandHandler("stats", self.admin_stats))
        self.app.add_handler(CommandHandler("dashboard" ,self.display_dashboard))

    def admin_required(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            role = self.db.check_role(user_id)
            
            if role != "ADMIN":
                print(f"⚠️ Security Alert: User {user_id} tried to access admin command.")
                
                if update.message :
                    await update.message.reply_text("Sorry ! this bot for admins only!")
                elif update.callback_query:
                    await update.callback_query.answer("Sorry ! this bot for admins only!")
                return  
                
            return await func(self, update, context, *args, **kwargs)
        return wrapper

    @admin_required
    async def admin_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        
        await update.message.reply_text(f"🔐 Welcome Admin Dashboard, {user.first_name}. System is secure.")

    @admin_required
    async def display_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("add special customer", url ="https://humble-goggles-r7gpj76699jwcxvgr-8000.app.github.dev/jform"),
                InlineKeyboardButton("add seller", url = "https://humble-goggles-r7gpj76699jwcxvgr-8000.app.github.dev/form")
                
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("___ Dashboard ___" ,reply_markup= reply_markup  ) 



  #  async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #    await update.message.reply_text("📊 System Statistics: All operational.")
        


# ==================== Main Function ====================

async def main():
    DB_PATH = "bot_shop_database.db"
    CUSTOMER_TOKEN ="8729539758:AAHfLgrs-fVHX8klZJVYXdVDy00GGHwlV-w" 
    ADMIN_TOKEN ="8601249864:AAElTuvuudBi-5ELp4JPuugMJytuqIlVwcI"    

    db_manager = DatabaseManager(DB_PATH)

    shop_bot = CustomerBot(CUSTOMER_TOKEN, db_manager)
    admin_bot = AdminBot(ADMIN_TOKEN, db_manager)

    print("🚀 All Bots are running concurrently ...")

    await shop_bot.start()
    await admin_bot.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bots were stopped safely.")
        
#Stopped#