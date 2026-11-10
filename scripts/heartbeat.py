"""Weekly activity marker to reduce GitHub's 60-day scheduled-workflow idle disable risk.

This records *checks*, not falsely updated shop verification dates.
"""
import datetime as dt
from common import ROOT, read_json, write_json_if_changed
path=ROOT/'data'/'automation_status.json'
today=dt.datetime.now(dt.timezone.utc).date()
old=read_json(path) if path.exists() else {}
last=old.get('last_successful_check')
if not last or (today-dt.date.fromisoformat(last)).days>=7:
    write_json_if_changed(path,{'last_successful_check':today.isoformat(), 'note':'RSS checked / pipeline executed; does not imply newly verified shops'})
    print('weekly heartbeat recorded')
else: print('weekly heartbeat not due')
