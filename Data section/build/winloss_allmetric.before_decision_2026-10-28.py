"""All-metric win/tie/loss: proposed method vs SMOTE, per dataset, every metric the paper reports
with the classifier/condition fixed by rule A (ai-draft/full/*.json -> outcome.chosen).

Input : ai-draft/outcome/allmetric/<KEY>.json   (raw printed numbers, schema SCHEMA_ALLMETRIC.md)
        ai-draft/full/<KEY>.json                 (earlier rule-A extraction; used for cross-check)
Output: out/winloss_allmetric_rows.csv           one row per paper x metric x dataset
        out/winloss_allmetric_paper_reported.csv what each paper itself prints (marks/WTL/tests)
        out/winloss_allmetric_summary.json       counts by metric group, overall, per paper
        out/winloss_allmetric_crosscheck.csv     rule-A metric: new copy vs earlier copy

Result rule (no threshold): compare the printed numbers. win = proposed better in the
metric's direction, loss = worse, tie = printed values equal. Rows with a non-numeric value
on either side ("---", unreadable) are counted as 'not comparable'.
Metric groups come from METRIC_GROUP below (printed name -> group); nothing else is merged.
"""
import json, glob, os, re, csv, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, 'ai-draft', 'outcome', 'allmetric')
FULL = os.path.join(ROOT, 'ai-draft', 'full')
OUT = os.path.join(ROOT, 'out')

# printed metric name (lower-case, exact as extracted) -> group
METRIC_GROUP = {
 'g-m (g-mean)':'G-mean','g_mean':'G-mean','g-mean':'G-mean','gm':'G-mean','mgm':'G-mean','g-score (g)':'G-mean',
 'mgm [%]':'G-mean','mg':'G-mean','mg [%]':'G-mean','mg (geometric mean of per-class recalls)':'G-mean',
 'geometric mean':'G-mean','gm (g-mean)':'G-mean','g-m (g-mean)':'G-mean','g-mean x100':'G-mean',
 'auc':'AUC','auc x100':'AUC','maUC'.lower():'AUC','mauc (%)':'AUC','aucm (%)':'AUC','auroc':'AUC','auc-roc':'AUC',
 'auc (average auc)':'AUC','a-roc (area under roc curve)':'AUC','auc (%) mean(std), 10-fold cv':'AUC',
 'f_m (f-measure)':'F-measure','f-measure':'F-measure','f_measure':'F-measure','f1 score':'F-measure','f1-score':'F-measure',
 'f-value':'F-measure','f1-score (f1)':'F-measure','f_betam [%]':'F-measure','macro-f1':'F-measure','f1':'F-measure',
 'f-value (minority class)':'F-measure','weighted f1':'F-measure','f-m (f-measure)':'F-measure',
 'recall':'Recall/sensitivity','sensitivity':'Recall/sensitivity','recall (or true positive rate)':'Recall/sensitivity',
 'recall (minority class)':'Recall/sensitivity','recall (of the smallest minority class)':'Recall/sensitivity',
 'precision':'Precision','precision (minority class)':'Precision','precision (of the smallest minority class)':'Precision',
 'p20 (precision at top 20%)':'Precision',
 'oa':'Accuracy','accuracy':'Accuracy','cg (%) accuracy, generalization':'Accuracy',
 'pavg (%)':'Average class accuracy','avacc [%]':'Average class accuracy','average accuracy (avg-acc)':'Average class accuracy',
 'acsa (average class specific accuracy)':'Average class accuracy',
 'pmin (%)':'Minimum class recall','msg (%) minimum sensitivity, generalization':'Minimum class recall',
 'true negative rate':'Specificity','mcc':'MCC','cba [%]':'CBA','cen':'CEN',
 'aucprc (area under precision-recall curve)':'AUC-PR',
}
# comparator actually used as the "SMOTE" column (from the extraction notes)
COMPARATOR = {
 'AMDO':'OVO-SMOTE','EMDO':'Static-SMOTE','SOUP':'Static-SMOTE','OVO-SMOTE':'Static-SMOTE (Static-SMT)',
 'GDHS':'OVO-SMOTE','SHSampler':'OVO-SMOTE',
 'MC-MBRC':'uncertain: column printed "MDO", inferred to be SMOTE',
 'DSRBF':'SMOTE + MLP (proposed uses RBF network)','EasyEnsemble':'SMOTE + AdaBoost',
}
def comparator(k): return COMPARATOR.get(k, 'plain SMOTE')

def num(s):
    if s is None: return None
    m = re.search(r'-?\d+(?:\.\d+)?(?:[eE]-?\d+)?', str(s).replace(',', ''))
    return float(m.group()) if m else None

def main():
    rows, rep, xc = [], [], []
    unmapped = set()
    for f in sorted(glob.glob(os.path.join(IN, '*.json'))):
        d = json.load(open(f, encoding='utf-8')); k = d['key']
        for m in d['metrics']:
            g = METRIC_GROUP.get(m['metric'].strip().lower())
            if g is None: unmapped.add((k, m['metric'])); g = 'UNMAPPED'
            hib = m.get('higher_is_better')
            for r in m['rows']:
                p, s = num(r.get('proposed')), num(r.get('smote'))
                if p is None or s is None or hib not in (True, False): res = 'not comparable'
                elif p == s: res = 'tie'
                else: res = 'win' if ((p > s) == bool(hib)) else 'loss'
                rows.append(dict(paper=k, metric_printed=m['metric'], metric_group=g, higher_is_better=hib,
                    table=m.get('table'), page=m.get('page'), is_rule_A_metric=bool(m.get('is_existing_chosen')),
                    dataset_as_printed=r.get('dataset_as_printed'), proposed=r.get('proposed'), smote=r.get('smote'),
                    marks=r.get('marks', ''), result=res, comparator=comparator(k),
                    classifier=d.get('classifier'), proposed_column=d.get('proposed_column'), smote_column=d.get('smote_column')))
            pr = m.get('paper_reported') or {}
            rep.append(dict(paper=k, metric_printed=m['metric'], metric_group=g, table=m.get('table'),
                summary_rows=json.dumps(pr.get('summary_rows', []), ensure_ascii=False),
                wtl_vs_smote=pr.get('wtl_vs_smote', ''), stat_test=pr.get('stat_test', '')))
            if m.get('is_existing_chosen'):
                old = (json.load(open(os.path.join(FULL, k + '.json'), encoding='utf-8')).get('outcome') or {}).get('rows', [])
                od = {o['dataset_as_printed']: o for o in old}
                od.update({o['dataset_as_printed'].split(' (')[0]: o for o in old})  # earlier copy appended '(full name)'
                for r in m['rows']:
                    o = od.get(r.get('dataset_as_printed')) or od.get(str(r.get('dataset_as_printed')).split(' (')[0])
                    if o is None: xc.append(dict(paper=k, dataset=r.get('dataset_as_printed'), status='dataset not in earlier copy')); continue
                    same_p = num(o.get('proposed')) == num(r.get('proposed'))
                    same_s = num(o.get('smote')) == num(r.get('smote'))
                    xc.append(dict(paper=k, dataset=r.get('dataset_as_printed'),
                        old_proposed=o.get('proposed'), new_proposed=r.get('proposed'),
                        old_smote=o.get('smote'), new_smote=r.get('smote'),
                        status='match' if (same_p and same_s) else 'differs'))
    def w(path, data):
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            keys = []
            for x in data:
                for kk in x:
                    if kk not in keys: keys.append(kk)
            wr = csv.DictWriter(fh, fieldnames=keys); wr.writeheader(); wr.writerows(data)
    w(os.path.join(OUT, 'winloss_allmetric_rows.csv'), rows)
    w(os.path.join(OUT, 'winloss_allmetric_paper_reported.csv'), rep)
    w(os.path.join(OUT, 'winloss_allmetric_crosscheck.csv'), xc)

    def tally(sel):
        c = collections.Counter(r['result'] for r in sel)
        return dict(win=c['win'], tie=c['tie'], loss=c['loss'], not_comparable=c['not comparable'],
                    rows=len(sel), papers=len({r['paper'] for r in sel}))
    def block(sel):
        by_group = {g: tally([r for r in sel if r['metric_group'] == g])
                    for g in sorted({r['metric_group'] for r in sel})}
        return dict(overall_all_metrics=tally(sel), by_metric_group=by_group)
    plain = [r for r in rows if r['comparator'] == 'plain SMOTE']
    per_paper = {}
    for k in sorted({r['paper'] for r in rows}):
        sel = [r for r in rows if r['paper'] == k]
        per_paper[k] = dict(comparator=comparator(k), all_metrics=tally(sel),
            by_metric={m: tally([r for r in sel if r['metric_printed'] == m]) for m in dict.fromkeys(r['metric_printed'] for r in sel)})
    xcc = collections.Counter(x['status'] for x in xc)
    summ = dict(rule=__doc__.split('Result rule')[1].split('Metric groups')[0].strip(),
        all_comparators=block(rows), plain_smote_only=block(plain),
        rule_A_metric_only=block([r for r in rows if r['is_rule_A_metric']]),
        per_paper=per_paper, comparator_notes=COMPARATOR,
        crosscheck_rule_A=dict(xcc), unmapped_metrics=sorted(map(list, unmapped)))
    json.dump(summ, open(os.path.join(OUT, 'winloss_allmetric_summary.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('papers', len(per_paper), 'rows', len(rows), 'crosscheck', dict(xcc), 'unmapped', sorted(unmapped))
    print('ALL', summ['all_comparators']['overall_all_metrics'])
    print('PLAIN', summ['plain_smote_only']['overall_all_metrics'])
    for g, v in summ['all_comparators']['by_metric_group'].items(): print(' ', g, v)

if __name__ == '__main__':
    main()
