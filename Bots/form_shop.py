from fastapi import FastAPI, Form, Request, HTTPException , UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

DB_Path = "bot_shop_database.db"

# ==================== صفحة الـ HTML مع الـ Tailwind CSS ====================
HTML_FORM = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل عميل جديد - Bisto Shop</title>
    <!-- تضمين Tailwind CSS للتصميم السريع والمحترم -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">

    <div class="bg-gray-800 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-gray-700">
        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold text-indigo-400">Bisto Shop 🛒</h1>
            <p class="text-sm text-gray-400 mt-1">Enter user's information</p>
        </div>

        <!-- الفورم بترسل البيانات عبر POST لنفس الـ Endpoint -->
        <form action="/submit-form" method="POST" enctype="multipart/form-data" class="space-y-4">        
            
            <div>
                <label class="block text-sm font-medium mb-1">Name</label>
                <input type="text" name="name" maxlength="32" required 
                    class="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Phone number</label>
                <input type="text" name="phone" maxlength="20" required 
                    class="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Id</label>
                <input type="text" name="id" maxlength="20" required 
                    class="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500">
            </div>


            <div>
                <label class="block text-sm font-medium mb-1">address</label>
                <input type="text" name="address" required 
                    class="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500">
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Account type</label>
                <select name="role" required 
                    class="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500 text-gray-200">
                    <option value="" disabled selected>Select Account type...</option>
                    <option value="customer">(Customer)</option>
                    <option value="seller">(Seller)</option>
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">image</label>
                <input type="file" name="national_id_image" accept="image/*" required 
                    class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 cursor-pointer">
            </div>

            <button type="submit" 
                class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 font-semibold rounded-lg transition duration-200 shadow-lg">
                Sent User's data.
            </button>
        </form>
    </div>

</body>
</html>
"""

# ==================== المسارات (Endpoints) ====================

@app.get("/form", response_class=HTMLResponse)
async def show_form():
    return HTML_FORM


@app.post("/submit-form", response_class=HTMLResponse)
async def handle_form_submission(
    name: str = Form(...),
    phone: str = Form(...),
    id : str = Form(...),
    address: str = Form(...),
    role: str = Form(...),
    national_id_image: UploadFile = Form(...)
):



    try:
        image = await national_id_image.read()
        with sqlite3.connect(DB_Path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, phone, address, national_id_image , role , telegram_id)
                VALUES (?, ?, ?, ?, ? , ?)
                """,
                (name, phone, address, image , role , id)
            )
            conn.commit()
            
        return """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
            <div class="bg-gray-800 p-8 rounded-2xl shadow-2xl text-center max-w-sm border border-gray-700">
                <h1 class="text-2xl font-bold text-green-400 mb-2">تم التسجيل بنجاح! 🎉</h1>
                <p class="text-gray-400 mb-4">شكراً لك، تم حفظ بياناتك بنجاح في النظام.</p>
                <a href="/form" class="inline-block px-6 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium">رجوع</a>
            </div>
        </body>
        </html>
        """
    except sqlite3.IntegrityError:
        # لو الإيميل أو التليفون أو الرقم القومي متكررين
        return """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-900 text-gray-100 flex items-center justify-center min-h-screen">
            <div class="bg-gray-800 p-8 rounded-2xl shadow-2xl text-center max-w-sm border border-gray-700">
                <h1 class="text-2xl font-bold text-red-400 mb-2">خطأ في التسجيل! ⚠️</h1>
                <p class="text-gray-400 mb-4">عذراً، البريد الإلكتروني أو رقم الهاتف أو الرقم القومي مستخدم من قبل.</p>
                <a href="/form" class="inline-block px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium">حاول مرة أخرى</a>
            </div>
        </body>
        </html>
        """