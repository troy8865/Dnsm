# generate_dynamic_m3u8.py

import os
from extract_token_m3u8 import extract_token_m3u8

def generate_live_m3u8(channel_name, url, output_folder="stream"):
    os.makedirs(output_folder, exist_ok=True)
    stream_file = os.path.join(output_folder, f"{channel_name}.m3u8")

    live_url = url
    if not url.endswith(".m3u8"):
        live_url = extract_token_m3u8(url)
    if not live_url:
        print(f"[X] {channel_name} için m3u8 bulunamadı.")
        return

    content = (
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        f"#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720\n"
        f"{live_url}\n"
    )

    with open(stream_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[✓] {channel_name}.m3u8 güncellendi.")
