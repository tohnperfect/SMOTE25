"""Identification stage of the SMOTE25 systematic search on OpenAlex.

For each candidate search string: the number of records (2002-2026), and its recall
on the SMOTE25 core corpus (how many corpus papers with an OpenAlex record it finds),
for all 76 papers and for the 37 SMOTE-family papers. Writes
Method section/search/openalex_search.json. Usage (from the repo root):
  python "Method section/build/search_openalex.py"
No API key or e-mail is sent; results depend on the date of the run.
"""
import json, re, time, urllib.parse, urllib.request, datetime, os, csv

ROOT = os.getcwd()
API = 'https://api.openalex.org/works'
YEARS = 'publication_year:2002-2026'
TYPES = 'type:article|preprint|book-chapter|review'

# Candidate strings. OpenAlex boolean search: AND, OR, NOT, quotes, parentheses.
STRINGS = {
    'S1 SMOTE named': ('title_and_abstract.search', '"SMOTE" OR "synthetic minority oversampling" OR "synthetic minority over-sampling"'),
    'S2 oversampling + imbalance': ('title_and_abstract.search', '(oversampling OR "over-sampling" OR "synthetic minority") AND (imbalanced OR imbalance OR "minority class")'),
    'S3 S2 in title only': ('title.search', 'SMOTE OR oversampling OR "over-sampling" OR "synthetic minority"'),
    'S4 method focus': ('title_and_abstract.search', '(SMOTE OR oversampling OR "over-sampling" OR "synthetic minority") AND (imbalanced OR imbalance OR "minority class") AND (propose OR proposed OR novel OR "new method" OR algorithm)'),
    'S5 final (S1 or S2, wider)': ('title_and_abstract.search', '(SMOTE OR oversampling OR "over-sampling" OR "synthetic minority" OR "adaptive synthetic" OR "synthetic samples" OR "synthetic instances") AND (imbalanced OR imbalance OR "minority class" OR "minority classes")'),
}


def get(params):
    url = API + '?' + urllib.parse.urlencode(params, safe=':|,')
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # rate limit or network hiccup
            time.sleep(2 + 3 * attempt)
            last = e
    raise last


def count(field, q, extra=''):
    flt = ','.join(x for x in (f'{field}:{q}', YEARS, TYPES, extra) if x)
    return get({'filter': flt, 'per-page': 1})['meta']['count']


def matched(field, q, ids):
    hits = set()
    for k in range(0, len(ids), 40):
        chunk = ids[k:k + 40]
        flt = ','.join([f'{field}:{q}', 'ids.openalex:' + '|'.join(chunk)])
        res = get({'filter': flt, 'per-page': 50, 'select': 'id'})
        hits |= {w['id'].rsplit('/', 1)[-1] for w in res['results']}
    return hits


# corpus: Section 7 OpenAlex ids, joined to Method Map uids through the key map
s7 = json.load(open(os.path.join(ROOT, 'Evaluation section', 'section07-coded-data.json'), encoding='utf-8'))
oa = {r['key']: r.get('openalex_id') for r in s7}
km = list(csv.DictReader(open(os.path.join(ROOT, 'Data section', 'out', 'section7_key_map.csv'), encoding='utf-8')))
mm = open(os.path.join(ROOT, 'SMOTE25_Method_Map_1.html'), encoding='utf-8').read()
D = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', mm, flags=re.S).group(1))
title2p = {p['title'].lower()[:40]: p for p in D}
byacr = {p['acronym']: p for p in D}
# titles written differently in the two sources
TITLE_FIX = {'MWMOTE-2014': 'MWMOTE', 'A-SUWO-2016': 'A-SUWO', 'G-SMOTE-2019': 'G-SMOTE'}
corpus = []
for row in km:
    p = byacr.get(TITLE_FIX.get(row['section7_key'], '')) or title2p.get(row['section7_title'].lower()[:40])
    corpus.append({'key': row['section7_key'], 'title': row['section7_title'], 'year': int(row['year']),
                   'oa': oa.get(row['section7_key']), 'sf': bool(p and p['smote_based']),
                   'acronym': p['acronym'] if p else row['data_section_key']})
ids_all = [c['oa'] for c in corpus if c['oa']]
ids_sf = [c['oa'] for c in corpus if c['oa'] and c['sf']]

out = {'run': datetime.date.today().isoformat(), 'filters': [YEARS, TYPES], 'corpus_with_record': len(ids_all),
       'sf_with_record': len(ids_sf), 'strings': {}}
for name, (field, q) in STRINGS.items():
    n = count(field, q)
    h = matched(field, q, ids_all)
    out['strings'][name] = {'field': field, 'query': q, 'records': n,
                            'recall_all': len(h), 'recall_sf': len(h & set(ids_sf)),
                            'missed_sf': sorted(c['acronym'] for c in corpus if c['sf'] and c['oa'] and c['oa'] not in h)}
    print(name, n, len(h), '/', len(ids_all), 'SF', len(h & set(ids_sf)), '/', len(ids_sf))
    time.sleep(1)
os.makedirs(os.path.join(ROOT, 'Method section', 'search'), exist_ok=True)
json.dump({'summary': out, 'corpus': corpus}, open(os.path.join(ROOT, 'Method section', 'search', 'openalex_search.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('corpus', len(corpus), 'with record', len(ids_all), 'SF with record', len(ids_sf))
