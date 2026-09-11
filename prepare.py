"""Regenerate the engagement's data artifacts from the public SROIE corpus.

Run after cloning https://github.com/zzzDavid/ICDAR-2019-SROIE into
./dataset. Deterministic (stride sampling), so the demo reproduces:
- engagement-prep/pairs.jsonl    120 golden pairs, spread across the corpus
- engagement-prep/holdout.jsonl  30 disjoint pairs the delivery never ships
- engagement-prep/receipts.db    all 626 receipts -- the data-access gate's real rows
"""
import csv, json, sqlite3
from pathlib import Path

data = Path("dataset/data")
ids = sorted(p.stem for p in (data / "key").glob("*.json"))

def ocr_text(rid):
    lines = []
    with open(data / "box" / f"{rid}.csv", newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f):
            if len(row) >= 9:
                lines.append(",".join(row[8:]).strip())
            elif row:
                lines.append(row[-1].strip())
    return "\n".join(l for l in lines if l)

def pair(rid, pid):
    key = json.loads((data / "key" / f"{rid}.json").read_text())
    return {"id": pid, "verified": True, "input": ocr_text(rid),
            "output": {k: key.get(k, "") for k in ("company", "date", "address", "total")}}

golden_ids = ids[0::5][:120]
used = set(golden_ids)
holdout_ids = [i for i in ids[2::7] if i not in used][:30]

out = Path("engagement-prep"); out.mkdir(exist_ok=True)
with open(out / "pairs.jsonl", "w") as f:
    for n, rid in enumerate(golden_ids):
        f.write(json.dumps(pair(rid, f"receipt-{n:03d}")) + "\n")
with open(out / "holdout.jsonl", "w") as f:
    for n, rid in enumerate(holdout_ids):
        f.write(json.dumps(pair(rid, f"holdout-{n:03d}")) + "\n")

con = sqlite3.connect(out / "receipts.db")
con.execute("CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY, ocr_text TEXT, company TEXT, date TEXT, address TEXT, total TEXT)")
for rid in ids:
    k = json.loads((data / "key" / f"{rid}.json").read_text())
    con.execute("INSERT OR REPLACE INTO receipts VALUES (?,?,?,?,?,?)",
                (rid, ocr_text(rid), k.get("company",""), k.get("date",""), k.get("address",""), k.get("total","")))
con.commit()
print(f"golden {len(golden_ids)}, holdout {len(holdout_ids)}, db rows",
      con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0])
