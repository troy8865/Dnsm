from yt_dlp import YoutubeDL

# URL → Dosya adı eşleşmeleri
channels = {
    "https://www.youtube.com/live/JCSOAmBeXnY?si=J0X3y15T0bBuMzXS": "sıfır tv",
    "https://www.youtube.com/live/YAsY48Ipkbo?si=vp4Qp7L_7e6XEf9u": "sözcü",
    "https://www.youtube.com/live/ztmY_cCtUl0?si=QaOpvWJQiRsDE8HX": "haber global",
    "https://www.youtube.com/live/VBU0QX6brew?si=wJT7enGilUeKfg9q": "tele1",
    "https://www.youtube.com/live/6N8_r2uwLEc?si=iaP8-tAjcUFKbECt": "halk tv",
    "https://www.youtube.com/live/JCSOAmBeXnY?si=Pou_eZrdZR8Csr6C": "kanal s",
    "https://www.youtube.com/live/ytlbCsbKdAQ?si=lf6HejUpxInIvNjx": "krt",
    "https://www.youtube.com/live/RdpqsTbi_KU?si=oFSNUIfFwnWgBYWd": "ulusal kanal",
    "https://www.youtube.com/live/ogxgOjWLwj0?si=9hPeOqg5zD97UGsG": "trt haber"
}

for url, filename in channels.items():
    ydl_opts = {'format': 'best'}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)

            # Stream URL tespiti
            if "url" in info:
                stream_url = info["url"]
            elif "entries" in info and info["entries"]:
                stream_url = info["entries"][0]["url"]
            else:
                stream_url = url

            # Dosya adı .m3u
            m3u_file = f"{filename}.m3u"

            # M3U oluştur
            with open(m3u_file, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"#EXTINF:-1,{filename}\n")
                f.write(f"{stream_url}\n")

            print(f"Oluşturuldu: {m3u_file}")

        except Exception as e:
            print(f"Hata oluştu: {url} -> {e}")
