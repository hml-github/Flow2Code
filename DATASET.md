# Dataset format

## Main dataset

Counts refer to programs. Every program has three images: code flowchart, UML and pseudocode.

| Language | ClassEval | HumanEval-X | MBXP | MCEval | Total |
|---|---:|---:|---:|---:|---:|
| Python | 100 | 164 | 611 | 50 | 925 |
| C++ | 0 | 164 | 611 | 50 | 825 |
| Java | 0 | 164 | 611 | 53 | 828 |
| JavaScript | 0 | 0 | 611 | 50 | 661 |
| C# | 0 | 0 | 611 | 50 | 661 |
| PHP | 0 | 0 | 611 | 50 | 661 |
| Ruby | 0 | 0 | 611 | 50 | 661 |
| C | 0 | 0 | 0 | 50 | 50 |
| Fortran | 0 | 0 | 0 | 50 | 50 |
| HTML | 0 | 0 | 0 | 50 | 50 |
| Pascal | 0 | 0 | 0 | 50 | 50 |
| Perl | 0 | 0 | 0 | 50 | 50 |
| Shell | 0 | 0 | 0 | 50 | 50 |
| Tcl | 0 | 0 | 0 | 50 | 50 |
| Visual Basic | 0 | 0 | 0 | 50 | 50 |
| **Total** | **100** | **492** | **4,277** | **753** | **5,622** |

## Supplementary dataset

HumanEval-X JavaScript contains 164 additional programs and 492 images. It uses the same format as main, with a separate manifest. Report explicitly whether results use main, supplementary, or both; the main count excludes these 164 tasks.

## Directory layout

```text
data/                                    Main dataset
  manifest.jsonl                         One entry per task
  summary.json                           Counts and schema version
  records/<dataset>/<language>.jsonl     Full task records
  assets/<dataset>/<language>/<type>/    Downloaded files
supplementary/humaneval_x_javascript/     Supplementary dataset
  manifest.jsonl
  summary.json
  records/humaneval_x/javascript.jsonl
  assets/humaneval_x/javascript/<type>/
scripts/validate_dataset.py               Standard-library integrity checker
```

The asset directories are included in the downloadable archives, outside ordinary Git history. Structured records contain only the selected tasks, not unselected upstream datasets. Paths in all records are relative to the repository/archive extraction root.

## Record schema

| Field | Meaning |
|---|---|
| `uid` | Unique identifier: `dataset/language/id` |
| `dataset` | `classeval`, `humaneval_x`, `mbxp`, or `mceval` |
| `language` | Normalized language key, e.g. `cpp`, `csharp`, `javascript`, `vb` |
| `task_id` | Original source task identifier |
| `bundle` | `main` or `supplementary` |
| `license` | Source subset's license identifier |
| `split` | `unspecified`; no prescribed training/test split |
| `reference_code` | Prepared reference program used for the diagram task |
| `source_record` | Original selected task, including source-specific prompt, solution and test fields |
| `assets` | Paths, byte sizes and SHA-256 hashes for the six files listed below |

Asset keys are `code`, `flowchart`, `uml`, `pseudocode`, `dot`, and `pseudocode_dot`. Images are PNG files. `dot` is the source flowchart representation; `pseudocode_dot` contains natural-language labels. For example, `task['assets']['uml']['path']` locates the UML image.

The manifest contains task metadata and assets, plus `record_file` and a one-based `record_line` locating the full record. Use `uid` or source task IDs to join data; do not assume row positions match across languages.

`reference_code` is an adapted program and may differ from the source solution in `source_record`, which can be a function body or use another original input format. `source_record` follows its source benchmark's schema: ClassEval includes `solution_code` and `test`; the other sources include `canonical_solution` and `test`. These fields are data, not a uniform runnable evaluation interface. The integrity checker does not execute them or assess diagram semantics.

## Test-field coverage

The main dataset contains 5,572 records with nonempty original `test` fields. All 50 MCEval HTML records have `test: ""`, as in the source dataset; no replacement tests are supplied. Their reference code and three diagrams are present. All 164 supplementary records have nonempty original `test` fields. A nonempty field does not itself establish that a test can run without the source benchmark's language-specific setup.
