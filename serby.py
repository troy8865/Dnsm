import os
import requests
import traceback

def main():
    try:
        source_url = os.getenv("SOURCE_PLAYLIST_URL")
        old_url = "https://vavoo.to/vavoo-iptv/play/"
        new_url = os.getenv("BASE_URL")
        output_file = os.getenv("OUTPUT_FILE")

        response = requests.get(source_url)
        response.raise_for_status()

        content = response.text
        lines = content.strip().splitlines()

        updated_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("#EXTINF"):
                # Satırdaki URL'yi değiştir
                updated_lines.append(line.replace(old_url, new_url))
                if i + 1 < len(lines):
                    updated_lines.append(lines[i + 1].replace(old_url, new_url))
            else:
                # EXTINF olmayan satırları koru
                updated_lines.append(line)
            i += 1

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines))

        print(f"✅ {output_file} başarıyla oluşturuldu.")

    except Exception:
        print("❌ Bir hata oluştu:")
        print(traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    main()
