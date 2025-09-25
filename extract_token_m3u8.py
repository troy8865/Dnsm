# extract_token_m3u8.py

import requests
import re

def extract_token_m3u8(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        # Sayfadaki m3u8 linklerini bul
        m3u8s = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\']*', resp.text)
        if m3u8s:
            for link in m3u8s:
                if "token=" in link or "signature=" in link:
                    return link
            return m3u8s[0]  # Token olmayan varsa onu da döndür
        return None
    except Exception as e:
        print(f"[HATA] {url} -> {e}")
        return None
