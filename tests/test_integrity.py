import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import SHOPS, HTML, PREF_REGION, REGIONS, validate_dataset, validate_html

class TestMapIntegrity(unittest.TestCase):
    def test_prefectures_and_regions(self):
        self.assertEqual(len(PREF_REGION),47)
        self.assertEqual(len(REGIONS),10)
        self.assertEqual(REGIONS['中部'],['新潟県','山梨県','長野県','岐阜県','静岡県','愛知県'])
        self.assertEqual(REGIONS['北陸'],['富山県','石川県','福井県'])
        self.assertEqual(REGIONS['近畿'],['三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県'])
    def test_shop_and_html_alignment(self):
        d=json.loads(SHOPS.read_text(encoding='utf-8'))
        validate_dataset(d)
        h=HTML.read_text(encoding='utf-8')
        validate_html(h,d['shops'])
        self.assertIn(f'全国{len(d["shops"])}店舗',h)
    def test_no_duplicate_ids(self):
        shops=json.loads(SHOPS.read_text(encoding='utf-8'))['shops']
        self.assertEqual(len(shops),len({x['id'] for x in shops}))
    def test_map_handles_empty_prefectures(self):
        h=HTML.read_text(encoding='utf-8')
        self.assertIn('PREF_CENTERS[pref]',h)
        self.assertIn('rememberPref()',h)
        self.assertIn('focusPrefMap',h)

if __name__=='__main__': unittest.main()
