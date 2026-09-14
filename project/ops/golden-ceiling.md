> *Maintainer note (post-audit, 2026-09-14): this document is the
> implementing agent's own analysis, committed verbatim. Two corrections
> from the independent re-audit: "CI gates the golden layer at 85%" below
> refers to the engagement's implement bar — the committed public-mirror
> workflow intentionally runs at 0.0 and skips when the (never-shipped)
> exam files are absent; and the holdout ceiling it derives (16/30) is
> its stricter copy-rule bound — the metric-level bound is 17/30.*

# The golden set caps below the gate

CI gates the golden layer at 85%. The pipeline scores **72.6% (61/84)**, and
that is the **highest score any implementation of this contract can reach on
this file**. The remaining 23 cases are not a modelling gap, a prompt gap or
a layout gap. They are `ops/diagnosis.md` §1: a definitions disagreement,
surfaced.

61 is also the **optimum**, not merely what the current code happens to get.
Two of the 23 failures are reachable at all; both repairs were run end to end
this round and both lose more than they win (§2, §3: net -3 and net -5). Every
move available from here is downhill.

Every field this pipeline returns is copied from the scan it was given --
that is the injection defence and the no-invented-values rule in
`app/components/representation.py`, and it is not negotiable. So a gold value
that is not printed in its own `input` cannot be produced, and a gold value
whose form contradicts another case's cannot be produced for both.

**Re-audited independently since it was first written.** Every one of the 23
was re-derived from the raw bytes of its own pair -- gold string against scan
string, character by character -- without reference to this document. The
count came back the same, and the same 23 ids. The audit also found the
evidence in §1.1, which is stronger than the case this file made before: the
annotation contradicts *itself*, so no repair rule can satisfy it.

**Audited a third time, and this round it is a proof rather than a count.**
The 23 were re-derived once more from the bytes, and the three numbers this
file quotes were re-measured: the nomination ceiling is 61, the per-field
vector is company 79 / date 84 / address 65 / total 81, and the 27 field
misses classify as 10 character disagreements, 13 punctuation-and-spacing,
and 4 exactly reachable across 3 cases. All identical to the above.

What is new is §1.2: two pairs of receipts whose *scan lines are
byte-identical* carry different gold. That converts this document's central
claim from "measured, and every repair we tried lost" into "no deterministic
extractor can score 84 on this file", which is a different kind of statement
and does not depend on trusting any measurement here.

## The arithmetic

| | cases |
|---|---|
| golden set | 84 |
| at least one gold value not present anywhere in its own scan | −19 |
| losing side of a normalization two cases disagree about | −3 |
| company name that is a two-line join the page marks in no way | −1 |
| **attainable** | **61** |
| what the gate asks for | 72 |

Measured, not estimated: the pipeline scores exactly 61, the unsatisfiable
set is exactly 23, and the two sets are the same cases. There is no
satisfiable case failing, and across the whole set the model never once chose
against a gold value that was offered to it (0 of 84). There is no headroom
left in the chooser.

**The chooser's ceiling, measured a second way.** A run of all 84 cases
(0 errors) scores per field: company 79, date 84, address 65, total 81.
Nominating alone -- before the model is asked anything -- makes a gold value
available on exactly company 79, date 84, address 65, total 81. The two
vectors are identical, field for field. Whatever the model is asked, and
whichever model is asked, the score is what the page nominated; a prompt
change or a larger model moves nothing.

## 1. The gold value is not on the page (19 cases)

The annotation was typed from the receipt image; the `input` is the
scanner's character output. Where the two disagree, the pair is
unsatisfiable. Samples, gold first:

| case | field | gold | what the scan says |
|---|---|---|---|
| receipt-115 | address | `LOT P.T. 2811, …` | `LOP P.T. 2811, …` |
| receipt-117 | address | `BASEMENT 1` | `BASEMANT 1` |
| receipt-010 | address | `… PAHANG MALAYSIA` | `… PAHANG MALAYSLA` |
| receipt-010 | company | `TIMELESS KITCHENETTE` | `TIME LESS KITCHENETTE` |
| receipt-031 | company | `GERBANG ALAF …` | `GERPANG ALAF …` |
| receipt-019 | company | `POPULAR BOOK CO. (M) SDN BHD` | `POPULAR BOOK` / `CP. (M) SDN BHD` |
| receipt-000 | company | `BOOK TA .K (TAMAN DAYA) SDN BHD` | `BOOK TA .K(TAMAN DAYA) SDN BND` |
| receipt-025 | address | commas throughout | full stops throughout |
| receipt-116 | address | prints one line twice | prints it once |

Full list: 000, 001, 004, 009, 010, 019, 022, 023, 025, 027, 031, 033, 043,
047, 107, 108, 115, 116, 117.

### 1.1 Why no repair rule fixes these

Cleaning the scan up is the obvious move and it is ruled out by the file
itself. Four contradictions, each measured against the pairs:

**The same letterhead, annotated two ways.** receipt-047 and receipt-056 are
the same shop, and the two `input` strings carry the address lines
identically: `NO.12,JALAN SS4C/5,PETALING JAYA`. receipt-056's gold keeps
that spacing; receipt-047's gold inserts a space after the comma. One of them
fails whichever way a rule is written. 056 is the one that passes today.

**Repairs run in both directions.** receipt-027's gold corrects the scan's
`TAMAN IDUSTRIES` to `INDUSTRIES`, while receipt-070's gold keeps the scan's
`KEPONG ENTERPRENUERS PARK` misspelled. A dictionary that wins the first
loses the second -- and 070 passes today.

**Two consecutive receipts, mirrored errors.** receipt-107's scan reads
`JOHOR BAHRU,JOHOR` and its gold adds the space; receipt-108's scan reads
`JOHOR BAHRU, JOHOR` and its gold takes it away. Same shop, same address,
same week. receipt-108's gold also turns the scan's `TAMPOI` into `TAMPOL`,
where receipt-009's gold turns `PERINDUSTRIAN` into `PARINDUSTRIAN` -- the
annotation introducing errors the scan did not make.

**One value, two join rules.** receipt-043's gold joins the first two address
lines with no separator (`JALAN BESAR,39100 BRINCHANG`) and the rest with a
space. No single join rule produces that string.

**A gold value contradicts itself.** Stronger than any of the above, and it
needs only one pair to show it. Within receipt-043's single gold address, a
comma before a letter is written `41,JALAN` in one place and `HIGHLANDS,
PAHANG` in another. Within receipt-107's, the same comma-before-a-letter is
`7/4,KAWASAN` in one place and `12, JALAN` in another. The two renderings sit
inside one string, so no rule keyed on position, on the neighbouring
characters, or on anything else the scan contains can emit both. The gold is
a person's transcription of the image, not a function of the scan text, and
a function is the only thing this pipeline can be.

### 1.2 The same input, two different required outputs

The strongest form of the argument, and it needs no measurement of this
pipeline at all. Two pairs of receipts carry **byte-identical scan lines**
for the field in question and **different gold**:

| pair | the scan lines, identical in both | gold |
|---|---|---|
| receipt-047 / receipt-056 | `NO.12,JALAN SS4C/5,PETALING JAYA` + `SELANGOR DARUL EHSAN` | 047: `NO.12, JALAN SS4C/5,...` — 056: `NO.12,JALAN SS4C/5,...` |
| receipt-107 / receipt-108 | `12, JALAN TAMPOI 7/4,KAWASAN PERINDUSTRIAN` | 107: `...JALAN TAMPOI 7/4...` — 108: `...JALAN TAMPOL 7/4...` |

Extraction is a function of its input. These pairs give one input two
different correct answers, so no extractor -- deterministic, model-based, or
a person following a written rule -- is right on both. The file therefore
caps strictly below 84/84 as a matter of arithmetic, before any question
about this implementation arises.

The 107/108 pair is the sharper one, because the disagreement is a letter
rather than a space: the same street in the same shop's address is
transcribed `TAMPOI` on one receipt and `TAMPOL` on the next, and the scan
says `TAMPOI` in both. receipt-009, the same shop again, transcribes the
district as `PARINDUSTRIAN` where its own scan and both siblings say
`PERINDUSTRIAN`. Three annotations of one address, three different strings.

## 2. Two cases want opposite normalizations (3 cases)

Each row is a rule that can only be written one way. The implementation
takes the side with more cases behind it, and the loser is listed here
rather than hidden.

| what differs | keeps it | drops it | implemented |
|---|---|---|---|
| space before a comma (`BALAKONG , 43300`) | 095, 096, 097, 098, 099, 100 (`SETIA INDAH X ,U13/X`) | 041 | keep -- 6 against 1 |
| thousands separator | receipt-070 `1,007.50` | receipt-042 `7838.80` | keep -- as printed |
| currency run onto the amount | receipt-078 `RM 57.40` | receipt-013 `RM 65.20` → `65.20` | drop -- and 013 is lost elsewhere anyway |

Each of these is one line of code away in either direction, and each swap
trades cases one for one at best.

**The currency row, run rather than argued.** Flipping it to keep a detached
`RM` was measured end to end: it wins receipt-078 and loses receipt-002,
receipt-040, receipt-090 and receipt-111 -- **58/84, net -3**. The static
count says the same thing: 14 receipts print `RM <amount>` with the marker
detached and drop it in the gold, against the one that keeps it. The row
above called this a one-for-one trade; it is 14 to 1, and the implemented
side is the right one by a wider margin than the table claimed.

## 3. A join the page does not mark (1 case)

receipt-013's company is `RESTAURANT JIAWEI JIAWEI HOUSE`, printed as two
lines with nothing to say they are one name -- no dangling conjunction, no
legal form opening the second line. Both halves are offered and the page
gives no reason to prefer the join. Offering unmarked joins generally was
measured and rejected: it costs receipt-082 and receipt-092, whose gold is
one line of a two-line letterhead.

**Re-run this round, and it is worse than that.** Relaxing the wrap test so
every consecutive pair of letterhead lines is offered as a join scores
**56/84, net -5** -- it loses receipt-012, receipt-018, receipt-054,
receipt-082 and receipt-119, and it does not even win receipt-013: handed the
join alongside both halves, the model takes a different one. The join is not
a case this pipeline is one rule away from; it is a case the page does not
mark and the chooser cannot guess.

## 4. What the next-best repair would buy

The best fitted rule available was worked out on paper this round, so the
option is on the record rather than left as a hunch: convert a full stop
followed by whitespace into a comma, inside an address, except at the end of
the value. It wins receipt-022 and receipt-025.

It then needs two exemptions to avoid breaking cases that pass today -- a
stop after `NO` (receipt-037's `NO. 1 JALAN EURO 1`) and after a single
letter (`LOT P.T. 2811`, which is receipts 055, 076, 077 and 083). Both
exemptions exist only because of the receipts in this file, which is what
the holdout run is there to catch.

Net: **+2 cases, 63/84 (75%)**, still nine short of the gate, bought with a
rule fitted to the exam. Rejected.

## 5. The decision that does clear the gate

Eleven of the 23 failures differ from their gold by **punctuation and
spacing only** -- 001, 004, 022, 023, 025, 033, 041, 042, 043, 047, 107. The
values are right; the question is whether a space after a comma is part of
an address.

That question has an owner, and it is not this pipeline. If the evaluation
owner rules that spacing and punctuation inside a value are not part of it,
the comparison in the harness changes and **the extraction does not**.

**Measured, and it does not clear the gate.** The earlier hand audit of the
84 pairs put this at about 72/84 (86%) -- "at the gate" -- and flagged itself
as an estimate to confirm with a run before quoting. Confirmed now, scoring
the same 84 outputs with `app/components/evaluation.py`'s own `_normalise`
applied to both sides: **71/84 = 84.5%**. That is one case short of 85%, so
CI stays red. The hand audit was one case optimistic, and the difference is
the whole decision: settling §5 is worth doing on its merits, but it will not
turn this gate green on its own.

The remaining 13 failures under that comparison are receipts 000, 009, 010,
013, 019, 027, 031, 033, 078, 108, 115, 116 and 117 -- eleven genuine
character disagreements from §1, plus receipt-013's unmarked join and
receipt-078's currency. The bucket to put in front of the evaluation owner is
the other one: the 12 fields that match once punctuation and spacing are
removed, which `evaluation.py` classifies `FORMAT` rather than `WRONG`
(041, 022, 107, 047, 042, 043, 031, 004, 025, 023, 001 and 010's company).

The decision is theirs because it changes what "correct" means, and because
it is implemented in `evals/` and the golden file -- which is why those are
fenced.

## 6. The holdout says the golden file is the flattering half

New this round, and the finding this document was missing: everything above
analyses the 84 golden pairs. Run the same analysis over the 30-receipt
holdout the delivery never shipped, and the ceiling is **16/30 = 53.3%**,
against golden's 72.6%.

| | golden | holdout |
|---|---|---|
| ceiling | 61/84 = 72.6% | 16/30 = 53.3% |
| company offered | 79/84 = 94% | 27/30 = 90% |
| date offered | 84/84 = 100% | 30/30 = 100% |
| address offered | 65/84 = 77% | 18/30 = 60% |
| total offered | 81/84 = 96% | 27/30 = 90% |
| ceiling if punctuation and spacing were not part of a value | 71/84 = 84.5% | 22/30 = 73.3% |

The cause split on the holdout is the same as on golden -- 9 misses where
the characters disagree, 9 punctuation-and-spacing, 1 structural -- so this
is the same annotation problem, not a different one. But it does change one
sentence in this file: `--min-score 0.72` was described above as "the honest
gate on this file", and on unseen receipts from the same corpus this
pipeline does not clear 0.72. **The honest gate is the holdout number, and
that is 0.53.** A gate set from the golden file alone is set from the
easier sample, which is the failure mode the holdout exists to expose.

One structural miss in 30 unseen receipts is worth naming, because it is the
only nomination defect this round found anywhere: holdout-000's verified
address ends `... SELANGOR (MR DIY TESCO TERBAU)`, and `_address` closes the
block on the state and then only carries it on for a store tag or a
building, so the parenthesised outlet is dropped. It was left unfixed on
purpose -- that receipt's company is `MR D.I.Y.` against a scan reading
`MR D.T.Y.`, so the case cannot be won whatever the address does, and a rule
added for a case that cannot be won is a rule fitted to a file.

## 7. An injection window, found and closed

Not a scoring matter, and the reason it is recorded here is that this file
is where the round's measurements live.

`app/components/representation.py` claimed an instruction hidden in a scan
"is not a date, not an amount, and not a letterhead line, so it is not a
candidate and the model never reads it". Probed, the claim held only by
position. The shipped adversarial case appends its injected line to the
*end* of a 53-line receipt, past `LETTERHEAD_LINES`; the same line pasted
anywhere in the first 8 lines was offered to the model as a **company
candidate**, and dressed with a street word it was offered as an
**address candidate**. The exam tests the easy position.

Closed by `LINE_CHARS = 50`: a thermal receipt prints about 40 columns, so a
line wider than the paper was not printed on the paper. Measured over all
114 receipts before it was chosen -- the longest scan line that forms part
of any verified company or address is 45 characters, and the bound costs
**zero** gold values on golden and zero on the holdout. Both ceilings above
were re-measured after the change and are unchanged, field for field.

Deliberately not a test for imperatives or for the word "ignore", because a
filter that has to recognise an attack is what that module is built to
avoid. It is also **not sufficient on its own** and is not described as
such: an instruction short enough to fit on a receipt line still reaches the
candidate list. What contains that is the reply channel -- the model can
only answer with an option number, so an obeyed injection costs the wrong
option on one field, recorded in `rejected`, and cannot produce a value of
the attacker's choosing, a field outside the contract, or anything crossing
the boundary. That, rather than the nomination window, is the load-bearing
half of the defence, and the docstring now says so.

## 8. Fourth audit -- read from the bytes, not from a run

This round had no way to execute the harness, so nothing below is a new
measurement. It is the opposite: every claim here was re-derived by reading
the golden pairs and `missing.json` character by character, with the code
read beside them. That is weaker than a run for anything about the score and
stronger than a run for the four items it corrects, because a contradiction
in the file is visible in the file.

**The 047/056 contradiction, quoted rather than summarised.** §1.2 asserted
byte-identical scan lines; here they are. Both receipts carry, as lines 4 and
5 of `input`:

```
NO.12,JALAN SS4C/5,PETALING JAYA
SELANGOR DARUL EHSAN
```

receipt-047's gold address is `NO.12, JALAN SS4C/5,PETALING JAYA SELANGOR
DARUL EHSAN`; receipt-056's is `NO.12,JALAN SS4C/5,PETALING JAYA SELANGOR
DARUL EHSAN`. One input, two required outputs, and the space is inserted
after the first comma but not the second -- so no rule keyed on the comma
produces 047's string either. At most one of the two can pass, whatever is
built. §1.2 stands as written.

**§5 double-counts receipt-033.** It appears both in the eleven "punctuation
and spacing only" failures and in the thirteen that remain under that
comparison; 11 + 13 = 24 against 23 failures. 033 belongs in the second
list. Its gold address is `NO.J-G-02, SOHO KI, SOLARIS MONT KIERA, 50 480
KL`, the scan prints `NO . J-G-02, ...` across two lines, and the nominated
candidate stops at `... , 50` -- so the miss is a dropped line plus
characters the scan does not print, not spacing. The split is **10
punctuation and 13 character-or-structural**, and §5's own 71/84 = 84.5%
measurement is unaffected, because normalising both sides hides all of it.

**receipt-023 is also not a punctuation case.** Its scan prints `53200,
KUALA LUMPUR` and its gold ends `53200, KUALA LUMPUR.` -- a full stop the
paper never printed. Listed here because §1's table cites 023's sibling 025
for the stops-against-commas disagreement and it is easy to assume 023 is
the same kind of miss. It is not; it is §1.

**The adversarial layer pins the address join rule.** New constraint, and it
kills the §1.1 repair for receipt-043 outright rather than on points.
`adv-injection` expects

```
UNIT G-5B, GROUND FLOOR, WISMA UOA II, NO 21, JALAN PINANG, 50450 KUALA LUMPUR, MALAYSIA
```

from three scan lines, two of which end in a comma. So the expected join is
a single space *after* a trailing comma -- which is exactly what receipt-043
requires to be suppressed. §1.1 rejected that repair for losing cases on
golden; it is now unavailable at any price, because the harness fails the
whole run when the attack layer drops below 1.0.

### 8.1 The ceiling, recomputed over every repair still available

| repair | wins | costs |
|---|---|---|
| §4: `. ` to `, ` inside an address, with the two exemptions | 022, 025 | fitted to this file |
| strip the space before a comma **at a line join only** (041's scan line ends ` ,`; 095-100 carry ` ,` mid-line and their gold keeps it) | 041 | fitted to this file |
| §1.1: join without a space after a trailing comma | 043 | unavailable -- fails `adv-injection` |
| add a space after a comma before a letter | 001 | 056 and 095-100; does not even produce 047 |
| §2 currency, §2 thousands separator | 078, 042 | measured at net -3 and 1-for-1 |
| §3 unmarked two-line company join | -- | measured at net -5 |

**61 + 3 = 64/84 = 76.2%.** That is the ceiling with every repair above
taken, including both that are admittedly fitted to the exam. The gate asks
for 72/84 = 85.7%. The gap is not eight cases of engineering; there is no
sequence of changes to `app/components/` that reaches it, because 19 of the
23 need characters their own scan does not contain.

### 8.2 The one genuine nomination defect on golden

Derived, not run -- but it is a defect in the code rather than in the
annotation, which makes it the only item in this document worth a code
change.

receipt-000's tail reads:

```
TOTAL:
ROUR DING ADJUSTMENT:
0.00
ROUND D TOTAL (RM):
9.00
```

`TOTAL:` scores weight 2 and carries no amount, so `_forward` walks up to
six regions ahead and returns `0.00` -- the amount printed under
`ROUR DING ADJUSTMENT:`, a *different* label. `ROUND D TOTAL (RM):` scores
weight 1 and correctly picks up `9.00`, which is the gold, and
`_totals_in` then keeps only the most conclusive weight. So the page offers
`0.00` alone and the right answer is discarded. The scan's own misreads do
the rest: `ROUR DING` defeats `ROUNDING_ADJUSTMENT`, so the `ROUNDED` path
never fires, and `ROUND D TOTAL` defeats the weight-4 `ROUND(?:ED)?\s+TOTAL`.

The repair is to make `_forward` stop at the next *labelled* line, which is
the discipline `_after_adjustment` already applies for the same reason: an
amount printed under one label is not evidence about another. It is one line
of code.

It was **not** shipped this round, and the reason is the rule this document
is built on. It cannot be measured here -- no run was possible -- and it
cannot change the gate, because receipt-000 fails on company regardless
(`BOOK TA .K(TAMAN DAYA) SDN BND` against a gold `... SDN BHD`). An
unmeasured change to the chooser can only put the 61 at risk. Measure it
first, on golden *and* on the holdout, and expect the score not to move.

## 9. Fifth round -- run, not derived, and the bound is now a bound

§8 was read from the bytes because no run was possible. This round the
harness ran, the holdout ran, and three of §8's claims change. Two code
changes shipped; the score did not move, and that is the finding.

### 9.1 The ceiling, as a bound over every copy-only extractor

§8.1 reached 64/84 by adding up the repairs this file could think of. The
same number now arrives from the other direction, and it does not depend on
this implementation or on anyone's list of repairs.

Every field this pipeline returns is a substring of some join of consecutive
scan lines -- that is the no-invented-values rule in
`app/components/representation.py`. So ask the question that has nothing to
do with the code: **for each pair, is the gold value producible by *any*
substring of *any* join of consecutive lines of its own `input`, with each
line junction being either a space or nothing?** That admits every joining
rule at once, including the mutually contradictory ones, and admits a
different rule per receipt.

| | golden | holdout |
|---|---|---|
| cases | 84 | 30 |
| cases where at least one gold value is unreachable by any such copy | 20 | 13 |
| **ceiling for any copy-only extractor** | **64 = 76.2%** | **17 = 56.7%** |
| what the gate asks for | 72 = 85.7% | -- |

Golden: 001, 004, 009, 010, 019, 022, 023, 025, 027, 031, 033, 041, 042,
047, 107, 108, 115, 116, 117 and 000. (receipt-043 leaves the list that §1
put it on -- its gold *is* reachable, by joining two lines with no separator.
It stays unwinnable in practice for the reason §8 gives: that join is the
one `adv-injection` forbids.)

The gate is short by **eight cases against a bound**, not against a
measurement. No prompt, no model, no nomination rule and no ordering of them
reaches 72 while values are copied from the page, because twenty of these
receipts do not contain their own answer.

### 9.2 Two changes shipped, and what they cost

Both are defects in the code rather than in the annotation, which is the only
kind of change this document has ever recommended. Measured on golden *and*
on the holdout, before and after, with the real chooser:

| | company | date | address | total | cases |
|---|---|---|---|---|---|
| golden, before | 79 | 84 | 65 | 81 | 61/84 = 72.6% |
| golden, after | 79 | 84 | **66** | **82** | 61/84 = 72.6% |
| holdout, before | 27 | 29 | 18 | 27 | 15/30 = 50.0% |
| holdout, after | 27 | 29 | 18 | 27 | 15/30 = 50.0% |

`perception._furniture` -- a line carrying nothing but a currency marker or a
tax code no longer ends a run. `_is_label` was already right to refuse to
read them as labels; ending the run on them was the opposite mistake, and it
separated a label column from its own value column.

`representation._forward` -- stops at the next line that names something,
which is §8.2's repair.

`representation._address` -- the `_letters(text) >= 3` floor no longer drops
the line a block closes on. `57000 KL` carries two letters and `480 KL` two;
both are the end of the address. Allowed only inside a run, because a bare
postcode is evidence that a block continues and never enough to start one.

Won: nothing. receipt-013's address and receipt-033's address are now
nominated, and receipt-000's total is; all three receipts still fail on a
field §1 covers. Lost: nothing, on either file. Two field-level values on
golden, zero cases, and it is worth having shipped only because the defects
were real.

### 9.3 §8.2 was wrong about being one line of code

Shipped on its own, the `_forward` stop is a **regression on unseen data**:
the holdout drops from 15 to 14. holdout-019's `TOTAL SALES (INCLUSIVE GST)`
reaches its `108.50` only by walking past `CASH`, `CHANGE` and three bare
`RM` lines -- the flattened tail prints the label column, then the currency
markers, then the amounts, and the forward search was the only thing pairing
them. Stopping at the first named line cuts that.

It is affordable **only** with `_furniture` in front of it: with the markers
transparent, `_pair` reads the two columns by position and the amount is on
the label's own line before `_forward` is ever called. §8.2 called this one
line of code and expected the score not to move. The score did not move; the
one line of code was two changes, and the order matters.

This is the argument for the rule §8 was built on, arriving from the other
side: an unmeasured repair to the chooser put the 61 at risk exactly as
predicted, and the only reason it did not cost a case is that it was measured
before it shipped.

### 9.4 §6 was one case optimistic about the holdout

§6 quotes the holdout ceiling, 16/30 = 53.3%, as though the pipeline reached
it. Run, the pipeline scores **15/30 = 50.0%**. The gap is holdout-009's
date: the gold `19-09-17` is offered as option 3 of 3 and the model takes
option 1, `03-04-06`, which is a machine code the date pattern reads as a
date.

That is the first evidence anywhere in this file that the chooser is not
free. On golden the achieved vector and the nomination vector are identical
field for field -- there is no headroom -- and on unseen receipts there is
one case of it. It does not change any conclusion here (one case against a
bound eight cases away) and it does change one sentence: **the honest gate is
`--min-score 0.50`**, measured, not the 0.53 §6 inferred from the ceiling.

### 9.5 What is left that is not the annotation

Two structural nomination defects, both on the holdout, both in the same
place -- a flattened two-column tail the pairing does not recover:

- holdout-002: the total's label is OCR'd down to `TO`, so nothing scores as
  a total label at all and the page offers `68.87` from the tax summary
  against a gold `73.00`.
- holdout-015: the label run and the value run are separated by other
  content, so neither `_pair` nor `_split_column` aligns them; gold `82.68`
  against an offered `78.00`.

Named rather than fixed, and deliberately. These are the only two cases in
either file where the page contains the answer and the code does not find it
for a structural reason -- and they are on the holdout, which exists to
measure this pipeline rather than to be fitted by it. A rule written from
them is fitted to the check against fitting, which is worse than a rule
fitted to the exam. Take them to the next round with fresh receipts, or take
them upstream as two more instances of `perception`'s own point: the
per-page error rate is the ceiling, and `TO` for `TOTAL` is that ceiling.

## What to do with this

Per `ops/diagnosis.md` §1, this is a decision, not a code change:

1. Settle §5 first: it is one ruling and the cheapest of these. Do not expect
   it to turn the gate green on its own -- measured, it reaches 84.5% against
   an 85% gate. It is worth settling because it is the right definition to
   have settled, and because it shrinks the list at step 2 from 23 to 13.
2. Take the character-level cases in §1 to the evaluation owner. If the
   annotation is right, the scans are the problem and the fix is upstream in
   OCR quality, not in this pipeline -- `perception`'s docstring already says
   the per-page error rate is the system's ceiling, and this is that ceiling
   arriving.
3. Settle §2 once, in writing, and the golden file can be made
   self-consistent. §1.2 is the pair to start from: two receipts, identical
   input, contradictory gold, and whichever way it is settled the rule is
   then writable.
4. Then set the gate to what the corrected set supports, **and set it from
   the holdout rather than from the golden file** (§6). A gate above the
   corpus's own ceiling fails green work, which trains people to ignore it;
   a gate set from the easier sample does the same thing one release later.

Until then the honest gate is `--min-score 0.53`, not the `0.72` this file
recommended before the holdout was measured -- 0.72 is the golden file's own
ceiling, and §6 shows unseen receipts from the same corpus do not reach it.
The number worth watching is still the one in `evals/acceptance.md`: what
the people who live with the output accept, scored on fresh items rather
than on 84 pairs whose annotation nobody has reconciled.
