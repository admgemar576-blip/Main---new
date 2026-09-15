import asyncio
import os
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import random

async def run():
    URL = "https://mobizil.com"

    async with async_playwright() as p:
        # تشغيل المتصفح مع إزالة علامات الأتمتة تماماً
        browser = await p.chromium.launch(
            headless=True,  
            slow_mo=100,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1280,720"
            ]
        )
        
        context = await browser.new_context(
            record_video_dir="./",
            record_video_size={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="ar-EG",
            timezone_id="Africa/Cairo",
        )
        
        page = await context.new_page()

        # تطبيق الـ Stealth بقوة
        await Stealth().apply_stealth_async(page)

        # حقن كود جافاسكريفت يخفي أي أثر للـ Playwright/Selenium
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        links_list = []

        try:
            print("Open Page....")
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
# جوه الـ for loop بتاعت الصفحات:
            for c in range(2, 13):
                await page.goto(
                        URL + f"/mobiles/samsung/page/{c}",
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    # 1. حركة بشرية: اعمل سكرول خفيف لتحت ولتوقيت عشوائي
                await page.evaluate(
                        "window.scrollBy(0, window.innerHeight * 0.5);"
                    )  # ينزل نص الشاشة
                await page.wait_for_timeout(random.randint(1500, 3500))  # وقفة عشوائية

                anchors = await page.locator("article a, .post-item a").all()

                anchors = await page.locator("a[href*='mobizil.com']").all()

                for anchor in anchors:
                    href = await anchor.get_attribute("href")
                    if href and "samsung-galaxy" in href and href not in links_list:
                        links_list.append(href)
                    
                print(f"[+] Total Links so far: {len(links_list)} in page {c} ")

                # 2. استراحة عشوائية أطول شوية بين الصفحات وبعضها كأن البشري بياخد نفسه
                sleep_time = random.randint(4000, 8000)
                await page.wait_for_timeout(sleep_time)
                

                
                await page.wait_for_timeout(7000)
                print(f"[+] Reached to the page {c} Succufly!")

        except Exception as e:
            print(f"[-] Error Enter doesn't exist: {e}")

        finally:
            video_path = await page.video.path() if page.video else None
            await context.close()
            await browser.close()

            if video_path and os.path.exists(video_path):
                final_name = "./scrapres.webm"
                if os.path.exists(final_name):
                    os.remove(final_name)
                os.rename(video_path, final_name)
                print("Done !")
            with open ("links.json" , 'w' , encoding="utf-8") as L:
                json.dump(links_list, L, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(run())