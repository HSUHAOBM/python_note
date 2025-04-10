
# pip install yt-dlp
import yt_dlp

url = ""

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',  # 下載檔名
    'format': 'bestvideo+bestaudio/best',  # 最佳畫質
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
