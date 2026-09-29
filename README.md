# Flow2Code

A dataset for generating code from flowcharts. Each task includes reference code, a code flowchart, a UML flowchart, a pseudocode flowchart, and two DOT representations.

| Package | Programs | Images | Download |
|---|---:|---:|---|
| Main dataset | **5,622** | **16,866** | [Main archive](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/flow2code-main-5622.tar.gz) |
| Supplementary: HumanEval-X JavaScript | **164** | **492** | [Supplementary archive](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/flow2code-supplementary-humaneval-x-javascript-164.tar.gz) |

The main dataset covers 15 programming languages and combines ClassEval (100), HumanEval-X (492), MBXP (4,277), and MCEval (753). HumanEval-X JavaScript is distributed separately; MBXP and MCEval JavaScript are included in main. The two packages have no overlapping task IDs.

## Get the data

The repository contains task records and manifests. Download either archive above and extract it into the repository root or an empty directory:

```bash
# Main dataset
tar -xzf flow2code-main-5622.tar.gz

# Optional supplementary dataset
tar -xzf flow2code-supplementary-humaneval-x-javascript-164.tar.gz
```

Each archive is complete: it includes task records, original task/test fields, reference code, all images and DOT files, license notices, and the validation script. Either archive can be used independently. [SHA256SUMS](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/SHA256SUMS) provides archive checksums; [packages.json](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/packages.json) provides package sizes and counts. See the [v1.0.0 release](https://github.com/hml-github/Flow2Code/releases/tag/v1.0.0) for all downloads.

## Read a task

Python 3.10 or later is sufficient; no packages need to be installed. Run this example from the repository or archive extraction root:

```python
import json
from pathlib import Path

root = Path('.')
index = root / 'data/manifest.jsonl'
# For the supplement, use:
# index = root / 'supplementary/humaneval_x_javascript/manifest.jsonl'

with index.open(encoding='utf-8') as f:
    item = json.loads(next(f))
lines = (root / item['record_file']).read_text(encoding='utf-8').splitlines()
task = json.loads(lines[item['record_line'] - 1])

print(task['uid'])
print(task['reference_code'])
print(root / task['assets']['flowchart']['path'])
```

## Verify files

```bash
python3 scripts/validate_dataset.py                         # main
python3 scripts/validate_dataset.py --bundle supplementary  # supplement
python3 scripts/validate_dataset.py --bundle all            # both
```

The validator checks task counts, record links, asset completeness and every asset's SHA-256. Before downloading assets, use `--metadata-only` to check the repository's structured records. It does not execute dataset code or calculate benchmark scores.

## Format and scope

See [DATASET.md](DATASET.md) for per-language counts and the record schema. No train/test split is assigned. This repository provides the dataset and its integrity checker; an evaluation harness and model inference pipeline are not included. Original test fields remain available in `source_record` for researchers implementing their own evaluation.

The 50 MCEval HTML tasks have empty original `test` fields; their task descriptions, reference code and diagrams are included. Nonempty tests in other subsets follow their source benchmark's format and require a suitable evaluation environment.

## Sources and licenses

Tasks originate from [ClassEval](https://github.com/FudanSELab/ClassEval), [HumanEval-X](https://github.com/zai-org/CodeGeeX), [MBXP](https://github.com/amazon-science/mxeval), and [MCEval](https://github.com/MCEVAL/McEval). See [LICENSES.md](LICENSES.md) for source attribution and per-subset terms; there is no single license covering all data. The validation script is MIT-licensed.
