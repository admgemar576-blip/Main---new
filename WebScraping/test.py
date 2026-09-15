import yt_dlp

m3u8_url = r"https://jaw.aisevenp.com/bcdn_token=HS256-PmHMnUwhdj0YlUU6qKixXgX3Jsl2R5H7VFJkdg5i4yQ&token_path=%2F31001cbe-1b7c-4b7c-a2b5-d5e2fd70ad10%2F&expires=1788920589/31001cbe-1b7c-4b7c-a2b5-d5e2fd70ad10/360p/video.m3u8"

ydl_opts = {
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://jawacademy.net/",
    },
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
  ydl.download([m3u8_url])
  
