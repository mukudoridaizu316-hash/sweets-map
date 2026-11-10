"""Find unverified leads via public news RSS, never add them to shops."""
from __future__ import annotations
import datetime as dt
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from common import ROOT, REGIONS, read_json, write_json_if_changed, valid_public_https

OUT=ROOT/'data'/'discovered_articles.json'
ALL=[p for arr in REGIONS.values() for p in arr]
# Rotate across all 47 prefectures; three every run, including empty prefectures.
now=dt.datetime.now(dt.timezone.utc)
slot=int(now.timestamp()//3600)
start=(slot*3)%47
prefs=[ALL[(start+i)%47] for i in range(3)]
seen=read_json(OUT) if OUT.exists() else []
seen_urls={r['url'] for r in seen}
added=0

for pref in prefs:
    # Neutral discovery only; headlines are not proof that a shop exists.
    q=f'{pref} (洋菓子店 OR 和菓子店 OR パティスリー) (新店 OR 老舗 OR 取材) when:30d'
    rss='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'ja','gl':'JP','ceid':'JP:ja'})
    try:
        req=urllib.request.Request(rss,headers={'User-Agent':'SweetsMapResearch/1.0 (public RSS; no automatic publishing)'})
        with urllib.request.urlopen(req,timeout=12) as resp:
            raw=resp.read(750_000)
        root=ET.fromstring(raw)
        for item in root.findall('./channel/item')[:12]:
            title=(item.findtext('title') or '').strip()[:200]
            link=(item.findtext('link') or '').strip()
            if not valid_public_https(link) or link in seen_urls or not title: continue
            seen.append({'title':title,'url':link,'pref':pref,'discovered_at':now.date().isoformat(),'status':'unverified','note':'RSS headline is not proof; requires independent source/address/product checks'})
            seen_urls.add(link);added+=1
    except Exception as exc:
        print(f'RSS unavailable for {pref}: {type(exc).__name__}: {exc}',file=sys.stderr)
    time.sleep(0.4)

# Retain at most 1000 leads; public RSS often includes duplicates and irrelevant pages.
# Do not delete source evidence from the verified shops dataset.
seen=seen[-1000:]
write_json_if_changed(OUT,seen)
print(f'RSS researched prefectures: {", ".join(prefs)}; new unverified leads: {added}; total queued: {len(seen)}')
