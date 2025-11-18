from yt_dlp import YoutubeDL

channels = {
    "https://www.youtube.com/live/JCSOAmBeXnY?si=J0X3y15T0bBuMzXS": "sifir tv",
    "https://www.youtube.com/live/YAsY48Ipkbo?si=vp4Qp7L_7e6XEf9u": "sozcü",
    "https://www.youtube.com/live/ztmY_cCtUl0?si=QaOpvWJQiRsDE8HX": "haber global"
}

for url, filename in channels.items():

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best"
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)

            # canlı linki bulma
            stream_url = None

            if "url" in info:
                stream_url = info["url"]
            elif "entries" in info and info["entries"]:
                stream_url = info["entries"][0].get("url")

            if not stream_url:
                print(f"URL alınamadı: {filename}")
                continue

            # dosya oluştur
            m3u = f"{filename}.m3u"
            with open(m3u, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"#EXTINF:-1,{filename}\n")
                f.write(stream_url + "\n")

            print(f"✔ {m3u} güncellendi")

        except Exception as e:
            print(f"Hata: {filename} -> {e}")
