"""Shared validation for the nationwide sweets map (no guessing of shop facts)."""
from __future__ import annotations
import ipaddress
import json
import re
import socket
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SHOPS = ROOT / 'data' / 'shops.json'
HTML = ROOT / 'site' / 'index.html'
REGIONS = {
    '北海道':['北海道'],
    '東北':['青森県','岩手県','宮城県','秋田県','山形県','福島県'],
    '関東':['茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県'],
    '中部':['新潟県','山梨県','長野県','岐阜県','静岡県','愛知県'],
    '北陸':['富山県','石川県','福井県'],
    '近畿':['三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県'],
    '中国':['鳥取県','島根県','岡山県','広島県','山口県'],
    '四国':['徳島県','香川県','愛媛県','高知県'],
    '九州':['福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県'],
    '沖縄':['沖縄県'],
}
PREF_REGION = {p:r for r, ps in REGIONS.items() for p in ps}
REQUIRED = ['id','name','region','pref','city','address','sweet','genre','note','source','added','verified']


def read_json(path:Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json_if_changed(path:Path, obj) -> bool:
    content=json.dumps(obj, ensure_ascii=False, indent=2)+'\n'
    if path.exists() and path.read_text(encoding='utf-8')==content:
        return False
    path.write_text(content, encoding='utf-8')
    return True


def valid_public_https(url:str) -> bool:
    if not isinstance(url,str) or len(url)>2048:
        return False
    try:
        p=urlsplit(url)
        if p.scheme!='https' or not p.hostname or p.username or p.password:
            return False
        host=p.hostname.casefold().rstrip('.')
        if host in ('localhost','localhost.localdomain') or '.' not in host:
            return False
        try:
            ip=ipaddress.ip_address(host)
            if not ip.is_global: return False
        except ValueError:
            if host.endswith(('.local','.internal','.test','.invalid')):
                return False
        return True
    except Exception:
        return False


def normalized(s:str)->str:
    import unicodedata
    return re.sub(r'[\s\u3000,，、.．・\-−ー:：/／()（）「」『』]+','',unicodedata.normalize('NFKC',str(s))).casefold()


def validate_dataset(data):
    assert isinstance(data,dict) and 'schema_version' in data and 'last_updated' in data
    assert isinstance(data.get('shops'),list)
    assert len(PREF_REGION)==47
    ids=set(); keys=set()
    for i,s in enumerate(data['shops']):
        assert all(k in s for k in REQUIRED), f'missing keys: shop index {i}'
        assert isinstance(s['id'],int) and s['id']>0 and s['id'] not in ids, f'duplicate ID {s["id"]}'
        ids.add(s['id'])
        assert s['pref'] in PREF_REGION and s['region']==PREF_REGION[s['pref']], f'wrong region: {s["name"]}'
        for k in ('name','city','address','sweet','genre','source','added','verified'):
            assert isinstance(s[k],str) and s[k].strip(), f'missing {k}: {s["name"]}'
        assert s['pref'].replace('県','').replace('府','').replace('都','') in s['address'] or s['pref'] in s['address'], f'address/pref mismatch: {s["name"]}'
        assert valid_public_https(s['source']), f'unsafe source: {s["source"]}'
        key=(normalized(s['name']),normalized(s['address']))
        assert key not in keys,f'duplicate shop {s["name"]}'
        keys.add(key)


def extract_base_shops(html:str):
    m=re.search(r'// SHOPS_DATA_BEGIN\s*const BASE_SHOPS\s*=\s*(\[.*?\]);\s*// SHOPS_DATA_END',html,re.S)
    if not m: raise ValueError('Cannot identify exactly one BASE_SHOPS data block')
    return json.loads(m.group(1))


def validate_html(html:str,shops):
    assert html.count('// SHOPS_DATA_BEGIN')==1 and html.count('// SHOPS_DATA_END')==1
    assert extract_base_shops(html)==shops, 'HTML and JSON are out of sync'
    for token in ('PREFECTURES_BY_REGION','ALL_PREFECTURES','REGION_FOR_PREF','PREF_CENTERS','selectPref','focusPrefMap','prefSelect','prefBar'):
        assert token in html, f'map feature missing: {token}'
    r=re.search(r'const PREFECTURES_BY_REGION=(\{.*?\});',html,re.S)
    assert r and json.loads(r.group(1))==REGIONS, '47-prefecture navigation was changed'
    for pref in PREF_REGION:
        assert f'"{pref}"' in html, f'prefecture center missing: {pref}'
