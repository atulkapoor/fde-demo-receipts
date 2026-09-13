"""perception: ocr-pipeline, via plain-python.

OCR pipeline: input_format == scanned_documents

Pixels to text, with everything that implies.

**The per-page error rate is the system's ceiling.** Measure it before promising
anything downstream, because no later component recovers a character that was
never read. A pipeline that reports 94% extraction accuracy and then quotes 97%
end-to-end is quoting a number that cannot exist.

Confidence per region is kept rather than averaged away. A page that is clean
except for the one box holding the account number is not a good page, and a
single page-level score says it is.

This is the contract; a real engine goes behind it. The choice among engines is
a decision in its own right -- one runs on a CPU and in an air gap, others need
a GPU and read tables far better -- and it belongs in the registry rather than
hard-coded here.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

# Below this, a region is not trusted and is queued for a human instead.
MIN_REGION_CONFIDENCE = 0.75

# How far down the page the letterhead runs. A receipt puts who and where at
# the top; below this the page is transaction lines.
HEADER_LINES = 12

# A printed money token, with the currency attached only when the scan
# attached it. "RM 26.10" is two tokens and the amount is "26.10"; "RM7.70"
# is one token and the amount is "RM7.70" -- the difference survives here
# because it survives in the annotation the corpus was verified against.
AMOUNT = re.compile(r"^(?:RM|MYR|\$)?-?\d[\d,]*\.\d{1,2}$")
CURRENCY = {"RM", "MYR", "$", "USD"}
# The GST codes a receipt prints against each row. Like the currency
# marker, a line made of nothing but one of these names nothing -- and read
# as a label it shifts every pairing below it by one, which is how the
# amount beside "final total" ends up being the change. A single-letter
# code is already excluded by length; these are the ones long enough to
# read as a word.
TAX_CODES = {"SR", "ZR", "ZRL", "OS", "ES", "NR", "TX", "SV"}
TOKENS = re.compile(r"[\s:]+")


class Perception:
    """Parser, as ocr-pipeline."""

    interface = "Parser"
    approach = "ocr-pipeline"
    stack = "plain-python"

    def __init__(
        self,
        engine: Callable[[Any], list[dict[str, Any]]] | None = None,
        critical_regions: set[str] | None = None,
    ) -> None:
        self._engine = engine
        # Regions where a low-confidence read matters regardless of the page
        # average -- an account number, a total, a date.
        self.critical = critical_regions or set()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        pages = []
        for page in payload.get("pages", []):
            regions = (self._engine or (lambda p: []))(page)
            weak = [r for r in regions if r.get("confidence", 0) < MIN_REGION_CONFIDENCE]
            critical_weak = [r for r in weak if r.get("name") in self.critical]

            pages.append({
                "id": page.get("id"),
                "text": "\n".join(r.get("text", "") for r in regions),
                "regions": regions,
                "weak_regions": [r.get("name") for r in weak],
                # A clean page with one bad box is not a clean page.
                "usable": not critical_weak,
                "needs_human": bool(critical_weak),
            })

        usable = [p for p in pages if p["usable"]]
        return {
            "pages": pages,
            # The ceiling. Nothing downstream exceeds it.
            "clean_share": len(usable) / (len(pages) or 1),
            "verify_queue": [p["id"] for p in pages if p["needs_human"]],
        }


# -- the engine behind the contract ------------------------------------------
#
# The corpus hands this build the scanner's own character output, so the
# pixel half of the pipeline is already done and the engine here is the
# other half: lines, a legibility score per line, and the label/value pairing
# a receipt's two-column tail needs. Swapping in tesseract (the alternative
# the registry lists) replaces the reading, not this pairing.
#
# It labels by layout role -- header, label, value -- and never by field
# name. Which line means "total" is the contract's question, and the contract
# belongs to the mapper.


def legibility(text: str) -> float:
    """A proxy, and named as one.

    Real OCR returns a confidence per character and this text arrived without
    one, so what is measurable here is how much a line looks like language:
    a row of single characters separated by spaces is what a bad scan leaves
    behind. Reported rather than averaged away, because the page that is
    clean except for one box is not a clean page.
    """
    if not text.strip():
        return 0.0
    tokens = text.split()
    singles = sum(1 for t in tokens if len(t) == 1)
    legible = " .,-&/()@:;#'\"%*+$!?_=[]"
    score = sum(c.isalnum() or c in legible for c in text) / len(text)
    if len(tokens) > 2 and singles / len(tokens) > 0.5:
        score *= 0.5
    return round(score, 2)


def amounts(text: str) -> list[str]:
    """Every money token on a line, as printed.

    The thousands separator stays: the verified annotation keeps it on one
    receipt here and drops it on another, and a normalization that wins the
    second loses the first. Left as printed, the two cases cost one each
    instead of the rule costing one and paying for one.
    """
    return [t for t in (p.strip(",;") for p in TOKENS.split(text)) if AMOUNT.match(t)]


def _is_value(region: dict[str, Any]) -> bool:
    """A line that carries nothing but money."""
    tokens = [t.strip(",;") for t in TOKENS.split(region["text"]) if t.strip(",;")]
    return bool(region["amounts"]) and all(
        AMOUNT.match(t) or t.upper() in CURRENCY for t in tokens
    )


def _is_label(region: dict[str, Any]) -> bool:
    """A line that names something and leaves its number elsewhere.

    Column furniture is not a label. A receipt's flattened tail interleaves
    the labels with a currency marker per row and, on a tax-coded line, a
    single letter -- neither names anything, and counted as labels they
    shift every pairing below them by however many of them there are. Read
    as neither, they end the run instead, and the label above keeps the
    amount printed under it.
    """
    if region["amounts"] or not any(c.isalpha() for c in region["text"]):
        return False
    named = region["text"].strip().strip("()[]:.,- ").upper()
    return len(named) > 1 and named not in CURRENCY and named not in TAX_CODES


def _furniture(region: dict[str, Any]) -> bool:
    """A line that is the column's marking rather than a row in it.

    A flattened tail prints the currency marker -- and on a tax-coded
    receipt the code -- on lines of their own, between the labels and the
    amounts those labels belong to. `_is_label` already declines to read
    them as labels, because naming nothing they would shift every pairing
    below them. Ending the run on them is the opposite mistake and just as
    expensive: it separates a label column from its own value column, and
    then the only thing left to pair the two is a forward search that has to
    reach past whatever sits in between. Stepped over, the columns are
    adjacent and `_pair` reads them by position.
    """
    if region["amounts"]:
        return False
    named = [word.strip("()[]:.,-").upper() for word in region["text"].split()]
    named = [word for word in named if any(c.isalpha() for c in word)]
    return bool(named) and all(word in CURRENCY or word in TAX_CODES
                               for word in named)


def _runs(regions: list[dict[str, Any]]) -> list[tuple[str | None, list]]:
    """The page as alternating runs of labels, amounts, and neither.

    Column furniture is not a run of its own -- see `_furniture`.
    """
    runs: list[tuple[str | None, list]] = []
    for region in regions:
        if _furniture(region):
            continue
        kind = "label" if _is_label(region) else "value" if _is_value(region) else None
        if kind and runs and runs[-1][0] == kind:
            runs[-1][1].append(region)
        else:
            runs.append((kind, [region]))
    return runs


def _pair(labels: list, values: list) -> None:
    """Read one label/amount column back into pairs.

    Alignment is done twice, from both ends, because a stray code line inside
    a run shifts one reading and not the other. Both are kept: an ambiguity
    the mapper can weigh beats one of them settled here by a coin.

    Only the labels-then-amounts order is read. The mirrored layout exists --
    a column of numbers with its labels printed underneath -- and it is not
    handled here, because the run of labels below it also carries the words
    that head the next block, so every alignment offered for it was wrong by
    however many of those there were. A pair that is wrong by construction is
    worse than a gap: the gap is visible in `unmapped`.
    """
    if len(labels) < 2 or len(values) < 2:
        return
    width = min(len(labels), len(values))
    for reading in (zip(labels, values),
                    zip(labels[-width:], values[-width:])):
        for label, value in reading:
            if value["amounts"][-1] not in label["values"]:
                label["values"].append(value["amounts"][-1])


def _split_column(before: list, values: list, after: list) -> None:
    """Pair a value column whose label column was flattened around it.

    The same two-column tail, read out in a different order: some of the
    labels, then every amount, then the rest of the labels. Each label
    takes the amount at its own position, counting through the half above
    the amounts and on into the half below -- the column has one label per
    amount, so the count is what fixes the alignment rather than a guess
    at an offset.

    Labels past that count belong to whatever block comes next: the run
    below a receipt's totals carries straight on into the heading of its
    tax summary, and those are not labels for these amounts. The half
    above must be short of the amounts for there to be anything to
    continue -- where it is not, `_pair` has already read the column.
    """
    labels = (before + after)[:len(values)]
    if len(values) < 2 or len(before) >= len(values) or len(labels) < len(values):
        return
    for label, value in zip(labels, values):
        if value["amounts"][-1] not in label["values"]:
            label["values"].append(value["amounts"][-1])


def _pair_columns(regions: list[dict[str, Any]]) -> None:
    """Pair every label with the amount its column printed for it.

    Receipts print the tail in two columns and the scan flattens it into one:
    seven labels, then the seven numbers that belong to them.
    """
    runs = _runs(regions)
    for (kind, run), (next_kind, next_run) in zip(runs, runs[1:]):
        if kind == "label" and next_kind == "value":
            _pair(run, next_run)
    for (above, before), (middle, values), (below, after) in zip(
            runs, runs[1:], runs[2:]):
        if above == "label" and middle == "value" and below == "label":
            _split_column(before, values, after)


def scan(page: Any) -> list[dict[str, Any]]:
    """One region per line of a scanned page."""
    text = page if isinstance(page, str) else (page or {}).get("text") or ""
    lines = [line.strip() for line in str(text).splitlines()]
    regions: list[dict[str, Any]] = []
    for number, line in enumerate(content for content in lines if content):
        on_line = amounts(line)
        regions.append({
            # Layout role, not field name.
            "name": "header" if number < HEADER_LINES else "body",
            "text": line,
            "confidence": legibility(line),
            "line": number,
            "amounts": on_line,
            # Every amount this line could be claiming, most likely first.
            "values": [on_line[-1]] if on_line and any(
                c.isalpha() for c in line) else [],
        })
    for region in regions:
        if region["name"] == "body" and _is_value(region):
            region["name"] = "value"
    _pair_columns(regions)
    return regions
