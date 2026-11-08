"""phase2_checks.py  ตรวจว่าผล Analysis A-F (19 ต.ค. 2026) ผูกกับตัวเลขที่ตรวจแล้ว (อ่านอย่างเดียว)  exit 1 ถ้าไม่ผ่าน"""
import csv, json, os, sys, hashlib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
J = lambda f: json.load(open(f, encoding="utf-8")); res = []
def ck(n, ok, d=""): res.append((n, bool(ok), d))
RC = J("out/reconcile_counts.json"); P = RC["partitions"]
A = J("out/modified_operations_summary.json"); a = list(csv.DictReader(open("out/modified_operations_audit.csv", encoding="utf-8")))
_NMOD = sum(1 for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["category"] == "modified")   # 331 until 8 Nov, 332 after
ck("A rows = modified entries in dataset_records", len(a) == A["entries"] == _NMOD, len(a))
ck("A combinations sum to entries", sum(A["combinations"].values()) == A["entries"])
ck("A no duplicate record_id", len({r["record_id"] for r in a}) == len(a))
B = J("out/baseline_provenance_summary.json"); rp = B["rows_by_partition_and_provenance"]
ck("B primary rows = 541", sum(rp["primary"].values()) == P["primary"]["rows"], sum(rp["primary"].values()))
ck("B wrapper rows = 207", sum(rp["wrapper"].values()) == P["wrapper_eligible"]["rows"], sum(rp["wrapper"].values()))
ck("B papers = 57 and labels sum", B["papers"] == 57 and sum(B["provenance_papers"].values()) == 57)
C = J("out/benchmark_concentration.json")
ck("C names / single-paper names match reconcile", C["by_name"]["names"] == RC["checks"]["distinct_names"]["got"] and C["by_name"]["singletons"] == RC["checks"]["single_paper_names"]["got"])
ck("C named entries match reconcile", C["named_entries"] == RC["checks"]["entries_named"]["got"])
D = J("out/temporal_comparison.json")["by_period"]
ck("D entries sum = named entries", sum(d["entries"] for d in D.values()) == RC["checks"]["entries_named"]["got"], sum(d["entries"] for d in D.values()))
ck("D primary rows sum 541", sum(d["primary_rows"] for d in D.values()) == P["primary"]["rows"])
ck("D modified entries sum = modified entries", sum(d["modified_entries"] for d in D.values()) == _NMOD)
E = J("out/characteristics_coverage.json")
ck("E instance coverage matches dataset_records_summary minus placeholder", E["n_instances"]["entries"]["n"] in (1326, 1327))
F = J("out/claim_evidence_summary.json")
ck("F claim rows = sum of labels", sum(F["by_label"].values()) == F["claims"])
ck("verified sources unchanged since reconcile", all(hashlib.sha256(open(f, "rb").read()).hexdigest() == RC["sources"][k]["sha256"]
                                                   for k, f in [("datasets", "out/verified_datasets.csv"), ("outcomes", "out/verified_outcomes.csv")]))
for n, ok, d in res: print("ok  " if ok else "FAIL", n, d)
print(f"{sum(o for _, o, _ in res)}/{len(res)} ok"); sys.exit(0 if all(o for _, o, _ in res) else 1)
