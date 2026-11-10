"""Keep the original 47-prefecture HTML intact except BASE_SHOPS and two stamps."""
import datetime as dt
import json
import re
from common import SHOPS, HTML, read_json, validate_dataset, validate_html


def build():
    data=read_json(SHOPS); validate_dataset(data)
    html=HTML.read_text(encoding='utf-8')
    if html.count('// SHOPS_DATA_BEGIN')!=1 or html.count('// SHOPS_DATA_END')!=1:
        raise ValueError('Unrecognized HTML. Refusing to overwrite.')
    record=json.dumps(data['shops'],ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pat=r'(?<=// SHOPS_DATA_BEGIN\n)const BASE_SHOPS=\[.*?\];(?=\n// SHOPS_DATA_END)'
    new,n=re.subn(pat,lambda _:f'const BASE_SHOPS={record};',html,flags=re.S)
    if n!=1: raise ValueError('Unexpected BASE_SHOPS syntax. Refusing overwrite.')
    new,n=re.subn(r'(<span id="total">)全国\d+店舗(</span>)',lambda m:f'{m.group(1)}全国{len(data["shops"])}店舗{m.group(2)}',new)
    if n!=1: raise ValueError('Could not update count label.')
    date=dt.date.fromisoformat(data['last_updated'])
    new,n=re.subn(r'(<span id="updated">)更新：[^<]+(</span>)',lambda m:f'{m.group(1)}更新：{date.year}年{date.month}月{date.day}日{m.group(2)}',new)
    if n!=1: raise ValueError('Could not update date label.')
    validate_html(new,data['shops'])
    if new!=html:
        HTML.write_text(new,encoding='utf-8')
        print(f'updated site/index.html with {len(data["shops"])} shops')
    else: print('no HTML change')

if __name__=='__main__': build()
