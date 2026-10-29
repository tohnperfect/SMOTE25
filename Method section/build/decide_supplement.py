"""Record P's decision of 28 Oct 2026: experiments reported only in supplementary
material count. GAMO (P40) stays Binary + Multiclass; its data types gain Tabular
(supplement Sec. 4, Tables 7-8). Usage: decide_supplement.py MAP"""
import json, re, sys

path = sys.argv[1]
html = open(path, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)', html, flags=re.S)
D = json.loads(m.group(2))
p = next(q for q in D if q['uid'] == 'P40')
assert p['acronym'] == 'GAMO' and p['class_category'] == 'Binary + Multiclass'
if 'Tabular' not in p['data_type']:
    p['data_type'].append('Tabular')
p['pdf_check_note'] = ('Decided by P (28 Oct 2026): experiments reported in supplementary material count, so the '
                       'two-class and multiclass tabular runs of the supplement (Tables 7-8) make GAMO Binary + Multiclass; '
                       'on images alone it is Multiclass only. Core is debatable: the generator is a learned network and '
                       'joins the family only through the convex-combination rule.')
data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
open(path, 'w', encoding='utf-8', newline='\n').write(html[:m.start(2)] + data + html[m.end(2):])
print('ok', p['data_type'])
