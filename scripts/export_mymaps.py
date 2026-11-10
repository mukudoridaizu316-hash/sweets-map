"""Export confirmed shops as an importable Google My Maps CSV.

GitHub data/shops.json remains the source of truth.
Import into My Maps using '住所' as location and '店名' as title.
A new CSV does NOT automatically update an existing My Map.
"""
import csv
import io
from pathlib import Path
from common import SHOPS, read_json, validate_dataset

OUTPUT = Path(__file__).resolve().parents[1] / "site" / "google-mymaps.csv"
FIELDS = ("店舗ID", "店名", "住所", "都道府県", "地方",
          "おすすめスイーツ", "ジャンル", "特徴", "出典URL", "最終確認日")


def plain(value):
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    # Avoid spreadsheet formula injection if exported data is opened in Sheets/Excel.
    if text.startswith(("=", "+", "-", "@")):
        text = "'" + text
    return text


def export():
    data = read_json(SHOPS)
    validate_dataset(data)
    if len(data["shops"]) > 2000:
        raise ValueError("My Maps CSV import limit is 2000 shops. Split into layers before exporting.")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow(FIELDS)
    for shop in data["shops"]:
        writer.writerow([
            shop["id"], plain(shop["name"]), plain(shop["address"]),
            plain(shop["pref"]), plain(shop["region"]), plain(shop["sweet"]),
            plain(shop["genre"]), plain(shop["note"]), plain(shop["source"]),
            plain(shop["verified"]),
        ])
    content = "\ufeff" + stream.getvalue()
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
        OUTPUT.write_text(content, encoding="utf-8", newline="")
        print(f"exported {len(data['shops'])} shops to {OUTPUT}")
    else:
        print(f"unchanged My Maps CSV ({len(data['shops'])} shops)")


if __name__ == "__main__":
    export()
