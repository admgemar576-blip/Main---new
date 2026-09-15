import os
import random
import time
from playwright.sync_api import sync_playwright

def run():
    # 1. رابط الموقع المستهدف (غير الرابط هنا)
    TARGET_URL = "https://bassthalk.com"

    with sync_playwright() as p:
        # تشغيل المتصفح مع إبطاء العمليات قليلاً (slow_mo) لتجنب كشف البوتات  
        browser = p.chromium.launch(
            headless=True,
            slow_mo=300  # تأخير 300 مللي ثانية بين كل أداء وأخر
        )
        
        # إعداد الـ Context لتسجيل الفيديو بأبعاد HD
        context = browser.new_context(
            record_video_dir="./",
            record_video_size={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        try:
            # فتح الموقع
            page.goto(TARGET_URL, wait_until="domcontentloaded")

            page.click('text ="تسجيل الدخول" ')
            page.click('#phone')
            page.keyboard.type('01227513923', delay=50) # بيقلد الكتابة الطبيعية   

            page.click('#password')
            page.keyboard.type('Ahmedmody', delay=50) # بيقلد الكتابة الطبيعية   

            page.get_by_text("اضغط هنا").click()

            page.get_by_text("ارسال الكود").click()
            

            page.wait_for_timeout(2000)

        finally:
            # مسار الفيديو المؤقت من Playwright
            video_path = page.video.path() if page.video else None
            # إغلاق المتصفح والـ Context لحفظ الفيديو نهائياً
            context.close()
            browser.close()

            # إعادة تسمية ملف الفيديو إلى scrapres.webm في نفس الفولدر
            if video_path and os.path.exists(video_path):
                final_name = "./scrapres.webm"
                if os.path.exists(final_name):
                    os.remove(final_name)  # مسح الفيديو القديم لو موجود بنفس الاسم
                os.rename(video_path, final_name)
                print("Done !")


if __name__ == "__main__":
    run()