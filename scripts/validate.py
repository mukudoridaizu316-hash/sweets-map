"""Fail CI if shop data/map semantics are inconsistent or UI markers disappear."""
from common import SHOPS, HTML, read_json, validate_dataset, validate_html

def main():
    data=read_json(SHOPS)
    validate_dataset(data)
    validate_html(HTML.read_text(encoding='utf-8'),data['shops'])
    print(f'Validated: {len(data["shops"])} shops, 47 prefectures, 10 regions; HTML synced')
if __name__=='__main__': main()
