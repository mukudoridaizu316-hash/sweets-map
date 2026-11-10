"""Strict recheck of externally curated candidates; cannot infer facts from headlines.

Candidates must supply name, pref, city, address, sweet, genre, note and source.
The source page must be HTTPS and contain name/address and the sweet term in
extracted text. A failed page, ambiguous text, or duplicate is skipped.
"""
import datetime as dt
import html as htmllib
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from common import ROOT, SHOPS, PREF_REGION, read_json, write_json_if_changed, normalized, valid_public_https, validate_dataset

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.buf=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript') and self.skip:self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.buf.append(data)


def page_text(url):
    if not valid_public_https(url): raise ValueError('non-public or non-HTTPS URL')
    # Uses only explicitly curated URLs. Never follow arbitrary links scraped from RSS.
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SweetsMapEvidenceChecker/1.0'})
    with urllib.request.urlopen(req,timeout=15) as response:
        if not valid_public_https(response.geturl()): raise ValueError('unsafe redirect')
        typ=response.headers.get('Content-Type','')
        if 'html' not in typ: raise ValueError('not HTML')
        page=response.read(1_000_000)
    parser=Text();parser.feed(page.decode('utf-8',errors='replace'))
    return normalized(' '.join(parser.buf))


def main():
    data=read_json(SHOPS);validate_dataset(data)
    path=ROOT/'data'/'verified_candidates.json'
    queue=read_json(path)
    if not isinstance(queue,list): raise ValueError('verified_candidates must be array')
    ids={s['id'] for s in data['shops']}
    uniques={(normalized(s['name']),normalized(s['address'])) for s in data['shops']}
    added=0;today=dt.date.today().isoformat()
    for c in queue:
        try:
            required=('name','pref','city','address','sweet','genre','note','source')
            if not isinstance(c,dict) or any(not isinstance(c.get(k),str) or not c[k].strip() for k in required):
                raise ValueError('missing required candidate fields')
            if c['pref'] not in PREF_REGION or not c['address'].startswith(c['pref']):
                raise ValueError('invalid prefecture or address')
            if not valid_public_https(c['source']):raise ValueError('invalid source')
            unique=(normalized(c['name']),normalized(c['address']))
            if unique in uniques: continue
            text=page_text(c['source'])
            # Deliberately strict: if a page abbreviates an address/product, keep
            # the record for editorial review instead of importing on guesses.
            if not all(normalized(c[k]) in text for k in ('name','address','sweet')):
                raise ValueError('source does not show exact name, address and sweet together')
            n=max(ids or {0})+1
            row={ 'id':n,'name':c['name'],'region':PREF_REGION[c['pref']],
                  'pref':c['pref'],'city':c['city'],'address':c['address'],
                  'sweet':c['sweet'],'genre':c['genre'],'note':c['note'],
                  'source':c['source'],'added':today,'verified':today }
            data['shops'].append(row); ids.add(n);uniques.add(unique);added+=1
            print(f'ACCEPTED {c["name"]}: source contained all evidence')
        except Exception as exc:
            print(f'PENDING {c.get("name", "unnamed") if isinstance(c,dict) else "invalid"}: {exc}',file=sys.stderr)
    if added:
        data['last_updated']=today
        validate_dataset(data)
        write_json_if_changed(SHOPS,data)
    print(f'Accepted {added} verified candidates; no 5-shop limit')

if __name__=='__main__': main()
