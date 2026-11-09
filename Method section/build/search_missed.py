"""For the SMOTE-family papers a search string misses, check whether OpenAlex holds an
abstract for them (missing abstracts are a known cause of low recall). Usage, from the
repo root: python "Method section/build/search_missed.py" """
import json, os, urllib.request

ROOT = os.getcwd()
R = json.load(open(os.path.join(ROOT, 'Method section', 'search', 'openalex_search.json'), encoding='utf-8'))
corpus = {c['acronym']: c for c in R['corpus']}
best = max(R['summary']['strings'].items(), key=lambda kv: kv[1]['recall_sf'])
print('best string:', best[0], best[1]['recall_sf'], '/', R['summary']['sf_with_record'])
sf = [c for c in R['corpus'] if c['sf']]
print('SF without OpenAlex record:', [c['acronym'] for c in sf if not c['oa']])
rows = []
for c in sf:
    if not c['oa']:
        continue
    w = json.load(urllib.request.urlopen('https://api.openalex.org/works/' + c['oa'] + '?select=id,title,abstract_inverted_index,type,primary_location', timeout=60))
    has_abs = bool(w.get('abstract_inverted_index'))
    src = ((w.get('primary_location') or {}).get('source') or {}).get('display_name')
    rows.append((c['acronym'], c['year'], has_abs, c['acronym'] in best[1]['missed_sf'], src))
print('SF with record:', len(rows), '| with abstract in OpenAlex:', sum(r[2] for r in rows))
for r in rows:
    if r[3] or not r[2]:
        print(('MISSED ' if r[3] else 'found  ') + ('abstract' if r[2] else 'NO abstract'), '|', r[0], r[1], '|', r[4])
json.dump({'best': best[0], 'rows': rows}, open(os.path.join(ROOT, 'Method section', 'search', 'missed_check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
