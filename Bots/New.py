import subprocess

def download_protected_m3u8(m3u8_url, output_filename="video.mp4"):
    # الهيدرز اللي السيرفر بيطلبها عشان يوافق يفتح الرابط
    headers = [
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer: "https://jawacademy.net",
        #"Origin: https://example.com"
    ]
    
    command = [
        "yt-dlp",
        m3u8_url,
        "-o", output_filename
    ]
    
    for header in headers:
        command.extend(["--add-header", header])
    
    try:
        print("Satrt downloading")
        subprocess.run(command, check=True)
        print(f"Downloaed Succefly : {output_filename}")
    except subprocess.CalledProcessError as e:
    print(f"Error While downloading : \n {e}")

# مثال للاستخدام:
download_protected_m3u8("https://jaw.aisevenp.com/bcdn_token=HS256-J7-4I5o1SWWIRT8uy27XqTfRdB4U6rNPJgRjvMO6CdY&token_path=%2Fa9a3330c-2577-4a4a-9411-5062b63d6e89%2F&expires=1789782078/a9a3330c-2577-4a4a-9411-5062b63d6e89/240p/video.m3u8")


async def abot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    

    role = check_role(user.id)
    
    if role != "admin":
        await update.message.reply_text("❌ عذراً، هذا البوت مخصص للإداريين فقط ولا توجد لك صلاحية هنا.")
        print(f"محاولة دخول غير مصرح بها من المستخدم: {user.id} ({user.first_name})")
        return

    keyboard = [
        [InlineKeyboardButton("📊 تقارير المبيعات", callback_data="admin_reports")],
        [InlineKeyboardButton("👥 ترقية مستخدم لبائع", callback_data="admin_make_seller")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"مرحباً بك يا أستاذ {user.first_name} في لوحة تحكم الأدمن 🛡️", 
        reply_markup=reply_markup
    )
