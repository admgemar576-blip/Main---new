import logging
import os
import random
import re
import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

DB_NAME = "english_bot.db"
WAITING_FOR_FILE = 1


# ------------------- إعداد قاعدة البيانات ------------------- #
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE,
            meaning TEXT,
            correct_answers INTEGER DEFAULT 0,
            wrong_answers INTEGER DEFAULT 0,
            correct_streak INTEGER DEFAULT 0,
            knowledge_percentage REAL DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER,
            term TEXT,
            is_correct INTEGER,
            answered_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    # Migration: لو الجدول اتعمل قبل ما نضيف correct_streak
    try:
        cursor.execute(
            "ALTER TABLE vocabulary ADD COLUMN correct_streak INTEGER DEFAULT 0"
        )
    except sqlite3.OperationalError:
        pass  # العمود موجود بالفعل
    conn.commit()
    conn.close()


# ------------------- وظائف قاعدة البيانات ------------------- #
def get_random_word(excluded_ids=None):
    """جلب كلمة عشوائية غير مكتملة المعرفة ومش اتسألت في السيشن دي"""
    excluded_ids = excluded_ids or []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = (
        "SELECT id, term, meaning, knowledge_percentage FROM vocabulary "
        "WHERE knowledge_percentage < 100"
    )
    params = []
    if excluded_ids:
        placeholders = ",".join("?" * len(excluded_ids))
        query += f" AND id NOT IN ({placeholders})"
        params.extend(excluded_ids)
    query += " ORDER BY RANDOM() LIMIT 1"

    cursor.execute(query, params)
    word = cursor.fetchone()
    conn.close()
    return word


def get_wrong_options(correct_meaning, count=3):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT meaning FROM vocabulary WHERE meaning != ? ORDER BY RANDOM() LIMIT ?",
        (correct_meaning, count),
    )
    wrong = [row[0] for row in cursor.fetchall()]
    conn.close()
    return wrong


def update_stats(word_id, is_correct):
    """
    تحديث الإحصائيات باستخدام معادلة أكثر واقعية:
    - streak_score: بيعتمد على عدد الإجابات الصح المتتالية (4 متتالية = 100%)
    - overall_accuracy: نسبة الصح للإجمالي
    - النتيجة النهائية = مزيج من الاتنين، عشان إجابة صح واحدة متدّيش 100% فوراً
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT correct_answers, wrong_answers, correct_streak, knowledge_percentage, term "
        "FROM vocabulary WHERE id = ?",
        (word_id,),
    )
    correct, wrong, streak, old_pct, term = cursor.fetchone()

    if is_correct:
        correct += 1
        streak += 1
    else:
        wrong += 1
        streak = 0

    total = correct + wrong
    overall_accuracy = (correct / total) * 100 if total else 0
    streak_score = min(100, streak * 25)  # 4 إجابات صح متتالية = مستوى كامل
    new_pct = round(0.7 * streak_score + 0.3 * overall_accuracy, 1)
    new_pct = min(new_pct, 100.0)

    cursor.execute(
        """
        UPDATE vocabulary
        SET correct_answers = ?, wrong_answers = ?, correct_streak = ?, knowledge_percentage = ?
        WHERE id = ?
        """,
        (correct, wrong, streak, new_pct, word_id),
    )
    conn.commit()
    conn.close()

    newly_mastered = old_pct < 100 and new_pct >= 100
    return new_pct, newly_mastered, term


def log_answer(word_id, term, is_correct):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (word_id, term, is_correct) VALUES (?, ?, ?)",
        (word_id, term, int(is_correct)),
    )
    conn.commit()
    conn.close()


def get_total_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(knowledge_percentage) FROM vocabulary")
    total_words, avg_knowledge = cursor.fetchone()
    conn.close()
    return total_words or 0, round(avg_knowledge or 0, 1)


def count_mastered():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE knowledge_percentage >= 100")
    n = cursor.fetchone()[0]
    conn.close()
    return n


def count_unmastered():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE knowledge_percentage < 100")
    n = cursor.fetchone()[0]
    conn.close()
    return n


def add_words(word_list):
    """إضافة كلمات جديدة، مع تجاهل أي كلمة موجودة بالفعل (بالاسم)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    added, skipped = 0, 0
    for term, meaning in word_list:
        cursor.execute("SELECT id FROM vocabulary WHERE term = ?", (term,))
        if cursor.fetchone():
            skipped += 1
            continue
        cursor.execute(
            "INSERT INTO vocabulary (term, meaning, correct_answers, wrong_answers, "
            "correct_streak, knowledge_percentage) VALUES (?, ?, 0, 0, 0, 0)",
            (term, meaning),
        )
        added += 1
    conn.commit()
    conn.close()
    return added, skipped


def get_logs_text(limit=30):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT term, is_correct, answered_at FROM logs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    conn.close()

    if not rows:
        return "مفيش أي لوجات لسه."

    lines = [f"📜 *آخر {len(rows)} من إجمالي {total} محاولة:*\n"]
    for term, is_correct, ts in rows:
        icon = "✅" if is_correct else "❌"
        lines.append(f"{icon} {term} — {ts}")
    return "\n".join(lines)


def get_words_text(correct=True):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT term, COUNT(*) c FROM logs WHERE is_correct = ? GROUP BY term ORDER BY c DESC",
        (1 if correct else 0,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "مفيش بيانات كفاية لسه."

    total_answers = sum(c for _, c in rows)
    icon = "✅" if correct else "❌"
    title = "الكلمات اللي جاوبت عليها صح" if correct else "الكلمات اللي غلطت فيها"
    lines = [f"{icon} *{title}* (إجمالي {total_answers} مرة):\n"]
    for term, c in rows[:40]:
        lines.append(f"• {term} — {c} مرة")
    return "\n".join(lines)


def parse_md_table(content):
    """
    بارسينج بسيط لجدول ماركداون:
    | Term | Meaning |
    |------|---------|
    | word | معنى    |
    """
    lines = [l.strip() for l in content.splitlines() if l.strip().startswith("|")]
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue  # سطر الفاصل بين الهيدر والداتا
        rows.append(cells)

    if not rows:
        return []

    header = [c.lower() for c in rows[0]]
    if any(k in header for k in ["term", "word", "كلمة", "meaning", "معنى"]):
        rows = rows[1:]

    words = []
    for row in rows:
        if len(row) >= 2 and row[0] and row[1]:
            words.append((row[0], row[1]))
    return words


# ------------------- الأوامر والتعامل مع البوت ------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["used_ids"] = set()  # ريستارت للسيشن
    total, avg = get_total_stats()
    mastered = count_mastered()
    welcome_text = (
        "👋 أهلاً بك في بوت تسميع الإنجليزي!\n\n"
        f"📚 عدد الكلمات في بنك الأسئلة: {total}\n"
        f"🏆 كلمات وصلت 100%: {mastered}\n"
        f"📊 متوسط نسبة معرفتك الكلية: {avg}%\n\n"
        "اضغط /quiz للبدء، /stats للإحصائيات، /details للتفاصيل، أو /add لإضافة كلمات جديدة."
    )
    await update.message.reply_text(welcome_text)


async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    used_ids = context.user_data.setdefault("used_ids", set())
    word_data = get_random_word(excluded_ids=list(used_ids))

    if not word_data:
        if count_unmastered() == 0:
            message = "🎉 مبروك! خلصت كل الكلمات في القاموس ووصلت 100% في كل حاجة!"
        else:
            message = "✅ خلصت كل أسئلة السيشن دي! دوس /start عشان تبدأ سيشن جديدة."
        target = update.message or update.callback_query.message
        await target.reply_text(message)
        return

    word_id, term, correct_meaning, current_pct = word_data
    used_ids.add(word_id)

    wrong_options = get_wrong_options(correct_meaning, count=3)
    options = wrong_options + [correct_meaning]
    random.shuffle(options)

    keyboard = []
    for option in options:
        is_correct_flag = "1" if option == correct_meaning else "0"
        callback_data = f"ans|{word_id}|{is_correct_flag}"
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    question_text = (
        "🧠 *ما هو معنى التعبير/الكلمة التالية؟*\n\n"
        f"📌 *{term}*\n\n"
        f"📈 نسبة معرفتك بها حالياً: `{current_pct}%`"
    )

    target = update.message or update.callback_query.message
    await target.reply_text(question_text, parse_mode="Markdown", reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    word_id = int(data[1])
    is_correct = data[2] == "1"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT term, meaning FROM vocabulary WHERE id = ?", (word_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        await query.edit_message_text("⚠️ الكلمة دي اتشالت من القاموس.")
        return
    term, meaning = row

    new_pct, newly_mastered, _ = update_stats(word_id, is_correct)
    log_answer(word_id, term, is_correct)

    if is_correct:
        response_text = (
            "✅ *إجابة صحيحة!* 🎉\n\n"
            f"🔹 *{term}* = {meaning}\n"
            f"📈 نسبتك دلوقتي: {new_pct}%"
        )
    else:
        response_text = (
            "❌ *إجابة خاطئة!*\n\n"
            f"🔹 *{term}* معناها الصحيح: *{meaning}*\n"
            f"📉 نسبتك دلوقتي: {new_pct}%"
        )

    await query.edit_message_text(text=response_text, parse_mode="Markdown")

    if newly_mastered:
        await query.message.reply_text(
            f"🏆 مبروك! أنهيت كلمة *{term}* ووصلت لـ 100% معرفة بيها!",
            parse_mode="Markdown",
        )

    await send_quiz(update, context)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total, avg = get_total_stats()
    mastered = count_mastered()
    await update.message.reply_text(
        "📊 *إحصائياتك الحالية:*\n\n"
        f"🔹 إجمالي الكلمات/التعبيرات: {total}\n"
        f"🏆 كلمات اتقنتها (100%): {mastered}\n"
        f"🎯 نسبة المعرفة العامة: {avg}%",
        parse_mode="Markdown",
    )


async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 اللوجات الشاملة", callback_data="details_logs")],
        [InlineKeyboardButton("✅ الكلمات الصح", callback_data="details_correct")],
        [InlineKeyboardButton("❌ الكلمات الغلط", callback_data="details_wrong")],
    ]
    await update.message.reply_text(
        "اختار تفاصيل إيه عايز تشوف:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "details_logs":
        text = get_logs_text()
    elif query.data == "details_correct":
        text = get_words_text(correct=True)
    elif query.data == "details_wrong":
        text = get_words_text(correct=False)
    else:
        text = "❓"

    await query.message.reply_text(text, parse_mode="Markdown")


# ------------------- إضافة كلمات من ملف .md ------------------- #
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📎 ابعتلي ملف .md فيه جدول بالكلمات (عمود Term وعمود Meaning) وأنا هضيفهم "
        "لقاعدة البيانات.\nاستخدم /cancel للإلغاء."
    )
    return WAITING_FOR_FILE


async def receive_md_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document or not document.file_name.endswith(".md"):
        await update.message.reply_text(
            "❌ لازم تبعت ملف بصيغة .md فيه جدول. جرب تاني أو /cancel."
        )
        return WAITING_FOR_FILE

    file = await document.get_file()
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    words = parse_md_table(content)
    if not words:
        await update.message.reply_text(
            "❌ مش لاقي جدول صحيح في الملف. تأكد إن فيه عمودين (Term و Meaning) وابعت تاني."
        )
        return WAITING_FOR_FILE

    added, skipped = add_words(words)
    await update.message.reply_text(
        f"✅ تمت الإضافة!\n➕ كلمات جديدة: {added}\n⏭️ اتجاهلت (موجودة بالفعل): {skipped}"
    )
    return ConversationHandler.END


async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ اتلغى.")
    return ConversationHandler.END


# ------------------- التشغيل الرئيسي للبوت ------------------- #
def main():
    init_db()

    TOKEN = '8601249864:AAFnaUGcXqdqrJoIkFjTNGt5zRDwHWtWGf4'
    #os.environ.get("BOT_TOKEN_QUIZS")
    if not TOKEN:
        raise SystemExit(
            "❌ محتاج تحط التوكن في متغير البيئة BOT_TOKEN قبل ما تشغّل البوت.\n"
            "مثال (Linux/Mac): export BOT_TOKEN='التوكن بتاعك'\n"
            "مثال (Windows PowerShell): $env:BOT_TOKEN='التوكن بتاعك'"
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_quiz))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("details", details))

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={WAITING_FOR_FILE: [MessageHandler(filters.Document.ALL, receive_md_file)]},
        fallbacks=[CommandHandler("cancel", cancel_add)],
    )
    app.add_handler(add_conv)

    app.add_handler(CallbackQueryHandler(handle_answer, pattern=r"^ans\|"))
    app.add_handler(CallbackQueryHandler(details_callback, pattern=r"^details_"))

    print("🚀 البوت يعمل الآن...")
    app.run_polling()


if __name__ == "__main__":
    main()