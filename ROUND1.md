# Round 1: exact marked HTML with less tokenizer work

Competition: markdown-render-speed-02, “Make Markdown rendering faster”,
$250 pot, deadline 2026-11-16T20:30:00Z. Built in this recorded session from
the supplied kit and original writing. No earlier entry was consulted.

## Contract and provenance

`parse.js` is a fork of the kit's marked 18.1.3 ES module (upstream reference
SHA-256 `e76f3b37046a5d294159872002e5f6fcda8ed232e1be45ff76b3863f2919dae3`).
Its synchronous named `parse(markdown)` export returns exact marked default
HTML: GFM enabled, breaks/pedantic/async disabled. No HTML normalization.
The upstream LICENSE is retained byte for byte; NOTICE retains the kit notice
and appends a description of this modified fork. New work is MIT-licensed.

`main.ts` is an authored driver following the kit's starter contract. It reads
every `{id, markdown}` from `/input/cases.json`, calls parse separately in
array order, and writes one JSON array of strings to `/output/html.json`.
Only the starter's MAKEFUN_INPUT_DIR and MAKEFUN_OUTPUT_DIR directory
overrides are read. The kit calls its starter `baselines/`; it contains no
separate `starter/` directory.

Each call uses marked's fresh options, lexer, link map, tokens, tokenizer and
renderer. Nested delimiter bounds belong to that tokenizer. There is no
input recognition, output table, block cache, result memoization or persistent
document state. Persistent lookup tables contain grammar regexes only.
Reference definitions still resolve through marked's original block/inline
phases. Delimiter rules, numeric-reference decoding, escaping and HTML
rendering are retained.

## Design and recorded revisions

1. Assembled the unchanged marked source at parse.js and the root driver.
   Graded before optimization: 720/720, byte-identical to the house driver.
2. Revision pass 1 (`tools/revise1.py`): guarded block and inline tokenizer
   calls by possible first character, without changing precedence. Leading
   spaces retain all possibly indented block rules. Added a whole remaining
   inline-suffix shortcut when no Markdown trigger, line ending, email marker
   or URL introducer occurs. It uses marked's numeric decoder outside raw HTML
   and preserves raw state and adjacent-text merging. Suffixes after inline
   constructs take the same path. Delimiter-free strings bypass bounds scans.
   Regraded: 720/720, byte-identical.
3. Revision pass 2 (`tools/revise2.py`): moved nested delimiter bounds from
   repeated WeakMap insertion/deletion to the current tokenizer's stack, with
   finally-based pop. Masking passes skip strings lacking their necessary
   backslash/backtick/bracket/angle triggers. List first lines use indexOf/slice
   instead of split arrays. Tab expansion and its leading-whitespace replace
   skip tab-free strings. The six list-marker regexes and four indentation
   variants of each list-continuation grammar are constructed before parsing,
   after the upstream grammar constants are initialized.
   Regraded: 720/720, byte-identical.

The parser remains the supplied generated/minified module with focused edits;
the two Python revision scripts show the changes as explicit replacements.
The original module remains in the external kit for differential comparison.

## Grading evidence

All three kit CLI grades used the process driver and worktree mode, two
executions per grade, the supplied scorer and the kit-verified practice set.
Each returned `{cases_passed:720,cases_total:720,passed:1}` and passed all 71
group checks. Each CLI log also reports its L1 regrade reproduced byte for
byte. Logs: `evidence/step1-grade.log`, `step2-grade.log`, `step3-grade.log`.

The baseline driver and each revision were additionally executed directly and
their html.json files compared with `cmp`. All matched byte for byte:

```text
html.json SHA-256:
e7e89c4fba2c45b1c4aa96c46c987e46c75a9fcdd08916b58ae7f2a7d7851724
```

Practice input SHA-256:
`350e706096061b38bcd58922f09855e38e50e86222ad7a3505ff9d2b2ddda2c1`.
Practice reference SHA-256:
`0037fb033e09d312e2b19ae58e73e14a38cf4a1be0a7030656ee6cdea308695d`.
These are the kit's published commitments, not embedded runtime data.

The first CLI attempt encountered this host's `spawnSync git EPERM` restriction
with synchronous pipes. `tools/local-spawn.cjs` redirects synchronous child
streams through temporary regular files for the local CLI only. The same
unmodified CLI then completed all three grades. This preload is neither
imported by main.ts nor used for benchmarks or differential checks. No kit
file was modified. The CLI's cost/authorship rows have no transcripts attached;
local grades do not establish the site's transcript gate or prize eligibility.

## Independent differential check

`tools/differential.mjs` compares exact strings from this parse export against
the kit's unmodified marked module. It tested:

| Family | Inputs |
| --- | ---: |
| CommonMark and GFM spec examples | 680 |
| Practice generated documents | 40 |
| New documents from the kit generator, four deterministic SHA-256 seeds | 160 |
| Deterministic randomized Markdown mixtures | 12,000 |
| Targeted entity, raw HTML, nesting, reference-state and suffix cases | 13 |
| Total | 12,893 |

Zero mismatches. There is also an isolation assertion after all other calls.
Random mixtures include malformed/nested delimiters, links, definitions,
raw tags, comments, fences, lists, tables, line endings, tabs, Unicode,
NUL, numeric and named entities, email addresses and GFM URL syntax.
Every failure would throw and print its complete input and first difference;
no test was removed to obtain this result. Fresh generator outputs are created
in temporary directories and deleted afterward, keeping the repository small.
Counts and aggregate differential digest are in `evidence/differential.json`.

## Performance measurement

`tools/benchmark.py` runs the kit baseline driver and this main.ts on the full
720-case practice workload in a fresh Node process each time. One untimed
fresh-process warmup per implementation precedes nine pairs. Pair order
alternates baseline/entry and entry/baseline. CPU is child user plus system
usage from Python's RUSAGE_CHILDREN delta; the parent is excluded. Each run
includes Node startup, module initialization, JSON input/output and rendering.
Every warmup and measured output is compared byte for byte with the baseline.
No preload, persistent worker or repeated-parse warmup is used inside a run.

| Driver | Median CPU seconds, 9 measured runs |
| --- | ---: |
| Kit baseline | 1.850493 |
| Entry | 1.614445 |

Baseline/entry median ratio: **1.146210×**. Entry uses **12.755952% less CPU**.
Median CPU difference: 0.236048 s. Raw CPU and wall samples, exact medians,
method and output hash are in `evidence/benchmark.json` and `benchmark.log`.

## Limits and reproduction

The host runs **Node v24.22.1**. The competition's pinned runtime is
**Node v22.23.4**, per RULES.txt. The CLI additionally notes its own server
harness version is v26.13.1; that is separate from the entry container pin.
The process driver runs locally without container isolation. This is a local
CPU comparison, with startup included and no null-control subtraction, CPU
pinning, cgroup accounting, confidence test, or official CPU-heat measurement.
No claim is made about final-set speed, official ranking or prize qualification.
Finite differential testing cannot prove equivalence for every possible string;
custom marked extensions and nondefault options are outside this entry's API
contract. The unseen scored seed was not available or used.

Reproduction commands are in README.md. All runtime dependencies are built-in
Node modules or parse.js. No network, downloads, native code, WebAssembly,
wallets, credentials, submission or repository publication were used. Practice
inputs and HTML outputs remain outside the entry tree; the entry is comfortably
below the 1 MiB cap. The witness recorder is managed by the surrounding session
and was not stopped or altered by this work.
