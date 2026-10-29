"""Merge the 28 Oct 2026 PDF check of the 37 SMOTE-family papers into
SMOTE25_Method_Map_1.html: class category (Binary only / Multiclass only /
Binary + Multiclass), how each method builds on SMOTE, corrected decision
points, and the page parts that show them. Usage: merge_pdf_check.py MAP RESULTS_DIR"""
import json, re, sys, glob, os

path, rdir = sys.argv[1], sys.argv[2]
html = open(path, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)', html, flags=re.S)
D = json.loads(m.group(2))
BY = {p['uid']: p for p in D}

R = {}
for f in sorted(glob.glob(os.path.join(rdir, '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        assert r['uid'] not in R, r['uid']
        R[r['uid']] = r
SF = [p for p in D if p['smote_based']]
assert set(R) == {p['uid'] for p in SF}, set(R) ^ {p['uid'] for p in SF}

# Provisional decisions for P (see class_flag): Loyalty-SMOTE only ever grows the
# smallest class and scores multiclass sets with binary metrics -> Binary only (rule 1);
# GLOS's only two-class run is a parameter-tuning demo on Sonar -> Multiclass only.
OVERRIDE = {'P74': 'B'}
CAT = {'B': 'Binary only', 'M': 'Multiclass only', 'BM': 'Binary + Multiclass'}
ORDER = ['Seed selection', 'Sample allocation', 'Neighbour choice', 'Placement rule', 'Post-filtering', 'Inside a pipeline']

changes = []
for uid, r in R.items():
    p = BY[uid]
    cat = OVERRIDE.get(uid, r['category'])
    assert cat in CAT and set(r['decision_points']) <= set(ORDER), uid
    via = [v for v in ORDER if v in r['decision_points']]
    if sorted(via) != sorted(p['smote_via']):
        changes.append((p['acronym'], p['smote_via'], via))
    p['smote_via_v1'] = p['smote_via']
    p['smote_via'] = via
    p['class_category'] = CAT[cat]
    p['class_evidence_pdf'] = r['class_evidence']
    p['class_reduced'] = r.get('reduced_multiclass') or ''
    p['class_multiclass_how'] = r.get('multiclass_how') or ''
    p['smote_explain'] = r['smote_explanation']
    notes = [x for x in (r.get('corrections'), r.get('flags')) if x]
    if uid in OVERRIDE:
        notes.insert(0, 'Provisional: the PDF check read this as %s; coded %s under rule 1 (only the smallest class is ever oversampled, binary metrics). Decision for P.' % (CAT[r['category']], CAT[cat]))
    if uid == 'P62':
        notes.insert(0, 'Provisional: Multiclass only; would be Binary + Multiclass if the two-class Sonar tuning run (Fig. 7) counts. Decision for P.')
    p['pdf_check_note'] = ' '.join(notes)
    p['pdf_checked'] = '28 Oct 2026'
    if p['smote_link']:
        p['smote_link'] = p['smote_link'].replace('�', '’')

from collections import Counter
cnt = Counter(p['class_category'] for p in SF)
print(cnt)
print('decision-point changes:', len(changes))
for c in changes:
    print('  ', c)

data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = html[:m.start(2)] + data + html[m.end(2):]


def rep(old, new):
    global html
    k = html.count(old)
    assert k == 1, (k, old[:90])
    html = html.replace(old, new)


# tab
rep('<button class="tab" role="tab" data-act="view" data-v="rule" id="tab-rule" type="button">Rule × tested</button>',
    '<button class="tab" role="tab" data-act="view" data-v="rule" id="tab-rule" type="button">Rule × tested</button>\n'
    '    <button class="tab" role="tab" data-act="view" data-v="cat" id="tab-cat" type="button">Class category</button>')
# state + constants
rep("  var S={view:'table',q:'',set:{},nontab:false,appr:{},data:{},type:{},via:{},rule:{},",
    "  var CATS=[['Binary only','every experiment that generates data is two-class, including multiclass sources reduced to two classes'],\n"
    "    ['Multiclass only','generates with three or more classes kept and is never run on two-class data'],\n"
    "    ['Binary + Multiclass','the same generator is run on two-class data and on data with three or more classes kept']];\n"
    "  var S={view:'table',q:'',set:{},nontab:false,appr:{},data:{},type:{},via:{},rule:{},cat:{},")
rep("    var ru=keys(S.rule); if(ru.length&&ru.indexOf(p.class_rule)<0) return false;",
    "    var ru=keys(S.rule); if(ru.length&&ru.indexOf(p.class_rule)<0) return false;\n"
    "    var ca=keys(S.cat); if(ca.length&&ca.indexOf(p.class_category)<0) return false;")
rep("""  g+='<div class="group"><span class="glab">Generation rule</span>';""",
    """  g+='<div class="group"><span class="glab">Class category</span>';\n"""
    """  CATS.forEach(function(x){g+=fbtn('cat',x[0],x[0]).replace('</button>',' <span class="n">'+cnt(function(p){return p.class_category===x[0];})+'</span></button>');});\n"""
    """  g+='</div>';\n"""
    """  g+='<div class="group"><span class="glab">Generation rule</span>';""")
rep("else if(a==='rule') on=!!S.rule[v];", "else if(a==='rule') on=!!S.rule[v]; else if(a==='cat') on=!!S.cat[v];")
rep("      else if(a==='rule'){S.rule[v]=!S.rule[v];}",
    "      else if(a==='rule'){S.rule[v]=!S.rule[v];}\n      else if(a==='cat'){S.cat[v]=!S.cat[v];}")
rep("S.via={};S.rule={};S.smote=false;", "S.via={};S.rule={};S.cat={};S.smote=false;")
# definition box
rep("""    RULES.map(function(x){return '<dt>'+esc(x[0])+'<span class="n">'+cnt(function(p){return p.class_rule===x[0];})+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>';""",
    """    RULES.map(function(x){return '<dt>'+esc(x[0])+'<span class="n">'+cnt(function(p){return p.class_rule===x[0];})+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>'+\n"""
    """    '<p><b>Class category</b> (SMOTE-family only, all 37 checked against the PDFs on 28 Oct 2026) says what each paper shows its generator doing. A multiclass source reduced to two classes counts as binary, and a multiclass extension that is only described does not count. The PDF check also confirmed or corrected the SMOTE steps listed above and wrote, for every paper, how its generator builds on SMOTE.</p><dl>'+\n"""
    """    CATS.map(function(x){return '<dt>'+esc(x[0])+'<span class="n">'+cnt(function(p){return p.class_category===x[0];})+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>';""")
rep("generation rule added 28 Oct 2026'", "generation rule and class category (PDF-checked) added 28 Oct 2026'")
# detail panel
rep("""      (p.class_rule?'<dt>Generation rule</dt>""",
    """      (p.class_category?'<dt>Class category</dt><dd><b>'+esc(p.class_category)+'</b><p class="linktxt">'+esc(p.class_evidence_pdf)+'</p>'+(p.class_reduced?'<p class="linktxt"><i>Reduced to two classes:</i> '+esc(p.class_reduced)+'</p>':'')+(p.class_multiclass_how?'<p class="linktxt"><i>Several classes:</i> '+esc(p.class_multiclass_how)+'</p>':'')+'</dd>'+\n"""
    """       '<dt>Builds on SMOTE (PDF)</dt><dd>'+esc(p.smote_explain)+(p.pdf_check_note?'<p class="linktxt warnline">'+esc(p.pdf_check_note)+'</p>':'')+'</dd>':'')+\n"""
    """      (p.class_rule?'<dt>Generation rule</dt>""")
rep("'class_rule','mc_strategy','class_rule_note','class_rule_source',",
    "'class_category','class_evidence_pdf','class_reduced','class_multiclass_how','smote_explain','smote_via_v1','pdf_check_note','pdf_checked','class_rule','mc_strategy','class_rule_note','class_rule_source',")
# category view
rep("  function syncPressed(){",
    """  function renderCat(r){
    var sf=r.filter(function(p){return p.smote_based;});
    if(!sf.length) return '<div class="none">No SMOTE-family papers match these filters.</div>';
    var h='<div class="codes"><span>SMOTE-family papers only, checked against the PDFs on 28 Oct 2026. Open a chip for the evidence and for how the method builds on SMOTE. Chip edge = Drive group.</span></div>';
    h+='<div class="gridbox"><table class="mx"><thead><tr>'+CATS.map(function(x){var n=sf.filter(function(p){return p.class_category===x[0];}).length;return '<th class="h-'+(x[0]==='Binary only'?'Binary':x[0]==='Multiclass only'?'Multiclass':'Both')+'">'+esc(x[0])+'<span class="n">'+n+'</span></th>';}).join('')+'</tr></thead><tbody><tr>';
    CATS.forEach(function(x){var c=sf.filter(function(p){return p.class_category===x[0];}).sort(function(a,b){return a.year-b.year;});h+='<td><p class="linktxt" style="color:var(--muted);font-size:.8rem;margin:0 0 8px">'+esc(x[1])+'</p>'+(c.length?'<div class="chips">'+c.map(function(p){return chip(p,'matrix');}).join('')+'</div>':'<span class="empty">\\u2013</span>')+'</td>';});
    return h+'</tr></tbody></table></div>';
  }

  function syncPressed(){""")
rep("S.view==='rule'?renderRule(r):renderTable(r);", "S.view==='rule'?renderRule(r):S.view==='cat'?renderCat(r):renderTable(r);")
rep("hv==='rule'||hv==='table'", "hv==='rule'||hv==='cat'||hv==='table'")

open(path, 'w', encoding='utf-8', newline='\n').write(html)
print('ok')
