"""Add the generation-rule fields (class_rule, mc_strategy, class_rule_note,
class_rule_source) to the 37 SMOTE-family records of SMOTE25_Method_Map_1.html
and the page parts that show them. Every text replacement must match once."""
import json, re, sys

path = sys.argv[1]
html = open(path, encoding='utf-8').read()

# ---------------------------------------------------------------- data
m = re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)', html, flags=re.S)
D = json.loads(m.group(2))
BY = {p['acronym']: p for p in D}

PDF = 'PDF checked 28 Oct 2026'
MAP = 'Method Map record (multiclass_handling, class_setting_evidence; read 6 Oct 2026)'

# Multiclass-rule methods: how they handle several classes.
STRAT = {
    'SMOTEBoost': 'Through the ensemble',
    'DSRBF / SSRBF (Static-SMOTE)': 'Class by class',
    'SCUT': 'To the mean class size',
    'SMOM': 'To the largest class',
    'GAMO': 'Per-class generator or region',
    'EMDO': 'Per-class generator or region',
    'RSMOTE': 'To the largest class',
    'GLOS': 'Per-class generator or region',
    'NROMM': 'Class by class',
    'OREM / OREM-M': 'Class by class',
    'MC-MBRC': 'Class by class',
    'MKC-SMOTE': 'To the largest class',
    'GDHS': 'To the mean class size',
}
# Verified against the PDF on 28 Oct 2026 (page references from the subagent reads).
CHECKED = {
    'SMOTEBoost': ('Multiclass rule',
        'Several classes are handled by AdaBoost.M2, not by SMOTE: the formal algorithm names one minority class '
        '(Fig. 1, p.111), and in the 5-class KDDCup-99 run each minority class (U2R, R2L) gets a hand-set SMOTE amount '
        '(Sec. 4, p.112). Only U2R results are tabulated (Table 3).'),
    'INOS': ('Binary rule',
        'Written for a positive vs a negative class (Sec. 3, p.3). 48 two-class tasks built from 7 UCR sets, one class '
        'vs the rest (Sec. 4.2, pp.7-8); no multiclass extension mentioned.'),
    'KNNOR': ('Binary rule',
        'Algorithms 1-2 split the data into Smin and Smaj (pp.4, 7). 19 KEEL two-class sets; image demos are also '
        'one class vs the rest. Per-class multiclass use is named only as future work (conclusion, p.16).'),
    'OREM / OREM-M': ('Multiclass rule',
        'OREM (Alg. 1) is two-class; OREM-M (Alg. 2, Sec. 3.2, p.6172) extends it: classes drawn in random order weighted '
        'by remaining quota, a synthetic point is dropped when its nearest neighbour is another minority class. OREM is '
        'tested on 28 two-class sets, OREM-M on 21 multiclass sets (never on two classes); OREMBoost on both.'),
    'Loyalty-SMOTE': ('Binary rule',
        'Loyalty and the Attraction relabelling use all classes, but SMOTE grows only one minority class (Sec. 3.3, p.6). '
        'The 5 multiclass sets are run as largest class vs smallest class and scored with binary metrics (Sec. 4.4.4, p.12). '
        'Earlier coded as native multiclass; corrected.'),
    'QC-SMOTE': ('One-vs-rest stated',
        'Each underrepresented class is the target against all other classes (Sec. 3.1, p.4; Sec. 3.7, p.7), but all 30 '
        'datasets are binary (Sec. 4.1, Table 1); the multiclass rule is never run.'),
}

n = {'Binary rule': 0, 'One-vs-rest stated': 0, 'Multiclass rule': 0}
for p in D:
    if not p['smote_based']:
        continue
    a = p['acronym']
    if a in CHECKED:
        rule, note = CHECKED[a]
        src = PDF
    else:
        rule = 'Multiclass rule' if p['multiclass_handling'] else 'Binary rule'
        note = p['multiclass_handling'] or p['class_setting_evidence']
        src = MAP
    p['class_rule'] = rule
    p['mc_strategy'] = STRAT.get(a, '') if rule == 'Multiclass rule' else ''
    p['class_rule_note'] = note
    p['class_rule_source'] = src
    n[rule] += 1
assert n == {'Binary rule': 23, 'One-vs-rest stated': 1, 'Multiclass rule': 13}, n
assert all(p['mc_strategy'] for p in D if p.get('class_rule') == 'Multiclass rule')
assert set(STRAT) <= set(BY) and set(CHECKED) <= set(BY)

data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = html[:m.start(2)] + data + html[m.end(2):]


def rep(old, new):
    global html
    k = html.count(old)
    assert k == 1, (k, old[:80])
    html = html.replace(old, new)


# ---------------------------------------------------------------- CSS
rep("table.mx tbody th{font:600 .9rem/1.25 var(--f-display)}",
    "table.mx tbody th{font:600 .9rem/1.25 var(--f-display)}\n"
    "table.rm tbody th .d{display:block;font:400 .74rem/1.4 var(--f-body);color:var(--muted);margin-top:3px}\n"
    "table.rm thead th:first-child{width:200px}\n"
    ".stratbox{margin-top:12px;background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:12px 14px;display:grid;gap:8px}\n"
    ".stratbox h3{margin:0;font:600 .95rem/1.3 var(--f-display)}\n"
    ".stratbox dl{display:grid;grid-template-columns:200px minmax(0,1fr);gap:6px 14px;margin:0}\n"
    ".stratbox dt{font-weight:600;font-size:.86rem}\n"
    ".stratbox dd{margin:0}\n"
    "@media (max-width:760px){.stratbox dl{grid-template-columns:minmax(0,1fr)}}")

# ---------------------------------------------------------------- tab
rep('<button class="tab" role="tab" data-act="view" data-v="flags" id="tab-flags" type="button">Year × flag</button>',
    '<button class="tab" role="tab" data-act="view" data-v="flags" id="tab-flags" type="button">Year × flag</button>\n'
    '    <button class="tab" role="tab" data-act="view" data-v="rule" id="tab-rule" type="button">Rule × tested</button>')

# ---------------------------------------------------------------- state, filters
rep("var S={view:'table',q:'',set:{},nontab:false,appr:{},data:{},type:{},via:{},smote:false,study:false,mismatch:false,sortKey:'year',sortDir:1,open:{}};",
    "var RULES=[['Binary rule','the generation rule is written for one minority class against the rest; more classes need decomposition or reduction'],\n"
    "    ['One-vs-rest stated','a rule for several classes is stated (each class against the rest) but never run on more than two classes'],\n"
    "    ['Multiclass rule','the rule itself generates for several classes (target sizes, class order, class-conditional generation or the ensemble)']];\n"
    "  var STRATS=['To the largest class','To the mean class size','Class by class','Per-class generator or region','Through the ensemble'];\n"
    "  var TESTED=[['Binary','Tested on binary only'],['Binary+Multiclass','Tested on both'],['Multiclass','Tested on multiclass only']];\n"
    "  var S={view:'table',q:'',set:{},nontab:false,appr:{},data:{},type:{},via:{},rule:{},smote:false,study:false,mismatch:false,sortKey:'year',sortDir:1,open:{}};")
rep("    if(S.study&&p.smote_rel!=='Study') return false;",
    "    if(S.study&&p.smote_rel!=='Study') return false;\n"
    "    var ru=keys(S.rule); if(ru.length&&ru.indexOf(p.class_rule)<0) return false;")
rep("""  g+='<div class="group"><span class="glab">Extends SMOTE via</span>';""",
    """  g+='<div class="group"><span class="glab">Generation rule</span>';\n"""
    """  RULES.forEach(function(x){g+=fbtn('rule',x[0],x[0]).replace('</button>',' <span class="n">'+cnt(function(p){return p.class_rule===x[0];})+'</span></button>');});\n"""
    """  g+='</div>';\n"""
    """  g+='<div class="group"><span class="glab">Extends SMOTE via</span>';""")
rep("else if(a==='mismatch') on=S.mismatch;",
    "else if(a==='mismatch') on=S.mismatch; else if(a==='rule') on=!!S.rule[v];")
rep("      else if(a==='mismatch'){S.mismatch=!S.mismatch;}",
    "      else if(a==='mismatch'){S.mismatch=!S.mismatch;}\n"
    "      else if(a==='rule'){S.rule[v]=!S.rule[v];}")
rep("S.via={};S.smote=false;", "S.via={};S.rule={};S.smote=false;")

# ---------------------------------------------------------------- definition box, meta
rep("""+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>';""",
    """+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>'+\n"""
    """    '<p><b>Generation rule</b> (SMOTE-family only) says how many classes the generator itself is written for; <b>tested on</b> says which data the paper ran it on (Experiments in paper). The two differ: a binary rule can be run on multiclass data reduced to two classes, and a multiclass rule may never be run on two classes. Six edge cases (SMOTEBoost, INOS, KNNOR, OREM/OREM-M, Loyalty-SMOTE, QC-SMOTE) were checked against the PDFs on 28 Oct 2026; the rest come from the record\\u2019s multiclass-handling field.</p><dl>'+\n"""
    """    RULES.map(function(x){return '<dt>'+esc(x[0])+'<span class="n">'+cnt(function(p){return p.class_rule===x[0];})+'</span></dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>';""")
rep("read 6 Oct 2026, +1 on 19 Oct 2026'", "read 6 Oct 2026, +1 on 19 Oct 2026 · generation rule added 28 Oct 2026'")

# ---------------------------------------------------------------- detail panel, CSV
rep("""      '<dt>Multi-class handling</dt><dd>'+val(p.multiclass_handling)+'</dd>'+""",
    """      '<dt>Multi-class handling</dt><dd>'+val(p.multiclass_handling)+'</dd>'+\n"""
    """      (p.class_rule?'<dt>Generation rule</dt><dd><b>'+esc(p.class_rule)+'</b>'+(p.mc_strategy?' · '+esc(p.mc_strategy):'')+'<p class="linktxt">'+esc(p.class_rule_note)+'</p><span class="warnline">'+esc(p.class_rule_source)+'</span></dd>':'')+""")
rep("'core_idea','multiclass_handling',", "'core_idea','multiclass_handling','class_rule','mc_strategy','class_rule_note','class_rule_source',")

# ---------------------------------------------------------------- rule x tested view
rep("  function syncPressed(){",
    """  function renderRule(r){
    var sf=r.filter(function(p){return p.smote_based;});
    if(!sf.length) return '<div class="none">No SMOTE-family papers match these filters.</div>';
    var h='<div class="codes"><span>SMOTE-family papers only. Rows: what the generation rule is written for. Columns: the class setting of the paper\\u2019s own experiments. Chip edge = Drive group.</span></div>';
    h+='<div class="gridbox"><table class="mx rm"><thead><tr><th>Generation rule</th>'+TESTED.map(function(t){var n=sf.filter(function(p){return p.paper_scope===t[0];}).length;return '<th class="h-'+(t[0]==='Binary+Multiclass'?'Both':t[0])+'">'+esc(t[1])+'<span class="n">'+n+'</span></th>';}).join('')+'</tr></thead><tbody>';
    RULES.forEach(function(x){
      var rr=sf.filter(function(p){return p.class_rule===x[0];});
      h+='<tr><th>'+esc(x[0])+'<span class="n"> · '+rr.length+'</span><span class="d">'+esc(x[1])+'</span></th>';
      TESTED.forEach(function(t){
        var c=rr.filter(function(p){return p.paper_scope===t[0];}).sort(function(a,b){return a.year-b.year;});
        h+='<td>'+(c.length?'<div class="chips">'+c.map(function(p){return chip(p,'matrix');}).join('')+'</div>':'<span class="empty">\\u2013</span>')+'</td>';
      });
      h+='</tr>';
    });
    h+='</tbody></table></div>';
    var mc=sf.filter(function(p){return p.class_rule==='Multiclass rule';});
    if(mc.length){
      h+='<div class="stratbox"><h3>How the multiclass rules handle several classes</h3><dl>';
      STRATS.forEach(function(s){var c=mc.filter(function(p){return p.mc_strategy===s;}).sort(function(a,b){return a.year-b.year;});if(!c.length) return;h+='<dt>'+esc(s)+' <span class="n mono">'+c.length+'</span></dt><dd><div class="chips">'+c.map(function(p){return chip(p,'matrix');}).join('')+'</div></dd>';});
      h+='</dl></div>';
    }
    return h;
  }

  function syncPressed(){""")
rep("S.view==='flags'?renderFlagTimeline(r):renderTable(r);",
    "S.view==='flags'?renderFlagTimeline(r):S.view==='rule'?renderRule(r):renderTable(r);")
rep("if(hv==='matrix'||hv==='timeline'||hv==='flags'||hv==='table') S.view=hv;",
    "if(hv==='matrix'||hv==='timeline'||hv==='flags'||hv==='rule'||hv==='table') S.view=hv;")

open(path, 'w', encoding='utf-8', newline='\n').write(html)
print('ok', n)
