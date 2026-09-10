# eIDAS Study Manual — English Edition

English edition of a 231-page German eIDAS study and audit manual, produced by a
multi-agent translation, verification and typesetting pipeline.

Source regulation: **Regulation (EU) No 910/2014**, consolidated version of
18 October 2024 (CELEX `02014R0910-20241018`), eIDAS / eIDAS 2.0.

## Status

Pilot covering **Articles 5a–5f — 69 norm blocks, 74 typeset pages**.
The full manual holds 220 norm blocks across 64 articles plus reference parts C–I.

| Check | Result |
|---|---|
| Verbatim quotations character-exact vs. official English | 27 / 27 |
| Block, field and ordering parity DE ↔ EN | 69 / 69 |
| Modality mapping (SHALL / SHALL NOT / MAY …) | 1:1, no softening |
| Defined terms vs. the 57 Article 3 definitions | no non-official variant found |
| Audit checks phrased as answerable questions | 69 / 69 |
| Retrieval cues within the 90-character limit | 69 / 69 |

## Terminology

Defined terms are not translated freely. The consolidated Regulation is aligned
article by article in both languages (`reference/articles_aligned.json`, 82/82
articles), and the 57 definitions of Article 3 form the binding glossary
(`reference/glossary_art3.json`). Passages marked ✓ are copied verbatim from the
official English text, never translated for this edition.

### A divergence between the language versions

Official German 5a(11) provides the Wallet under a *"notifizierten"* electronic
identification scheme; the official **English** 5a(11) omits "notified", and
5a(22) disapplies Article 9 (the notification procedure) to Wallets in both
languages. The German manual is faithful to its own language version; the
English edition follows the English wording. See `corpus/en` block `5a|Abs. 11`.

## Pipeline

```
extract2 → normalize → align ──────────────► reference (glossary, aligned articles)
parse_blocks ──────────────────────────────► 220 norm blocks, field-structured
        │
        ├─ translate    8 agents, one per batch
        ├─ verify       3 independent lenses per batch
        │               (legal fidelity · official terminology · completeness)
        ├─ repair       verifier findings, re-checked before applying
        ├─ learning     the manual's 9 evidence-based principles
        ├─ design   ⇄   learning agent reviews the design spec back
        └─ boss         independent spot-check, then release decision
```

`verify_quotes.py` and `lint.py` are runnable gates, not reports:
quotations are compared character-by-character against the official English text.

## Layout

Modality is encoded as colour **and** silhouette (seven distinguishable badges);
priority is achromatic and positional, in separate height zones at the page edge,
so the two codes never share a channel. Red denotes prohibition only — deadlines
are marked typographically — and all text colours meet a 4.5:1 contrast floor.
