# 安裝套件
# pip install yt-dlp
import yt_dlp


def download_youtube(url: str, mode: str = 'audio'):
    """
    下載 YouTube 內容
    如果需要登入才可瀏覽，可用 Get cookies.txt LOCALLY 瀏覽器套件 抓出 cookiefile
    :param url: YouTube 影片網址
    :param mode: 'audio' 只抓音訊, 'video' 抓整部影片
    """
    # 音訊
    if mode == 'audio':
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',   # 儲存檔名：影片標題.副檔名
            'format': 'bestaudio/best',        # 最佳音訊
            # 'cookiefile': 'www.youtube.com_cookies.txt',
            'verbose': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',   # 儲存成 mp3，也可改成 'm4a'
                    'preferredquality': '192',  # 音質 kbps
                }

            ],
            'progress_hooks': [
                lambda d: print(
                    f"下載進度: {d['downloaded_bytes'] / d['total_bytes']:.2%}") if d['status'] == 'downloading' else None
            ]
        }
    # 影片
    elif mode == 'video':
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',   # 儲存檔名：影片標題.副檔名
            'format': 'bestvideo+bestaudio/best',  # 最佳影片＋最佳音訊
            # 'cookiefile': 'www.youtube.com_cookies.txt',  # (可選)如果需要登入
            'verbose': True,
            'merge_output_format': 'mp4',  # 格式
            'progress_hooks': [
                lambda d: print(
                    f"下載進度: {d['downloaded_bytes'] / d['total_bytes']:.2%}") if d['status'] == 'downloading' else None
            ]
        }
    else:
        raise ValueError("mode 必須是 'audio' 或 'video'")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    url = ""

    # 選擇要抓「音訊」或「整部影片」
    # 清單網址也可以下載
    mode = 'audio'  # 'audio' 只抓音訊, 'video' 抓整部影片

    try:
        download_youtube(url, mode)
    except Exception as e:
        print(f"下載失敗: {e}")
