# Flow2Code: Evaluating Large Language Models for Flowchart-based Code Generation Capability

**Mengliang He, Jiayi Zeng, Yankai Jiang, Wei Zhang, Zeming Liu, Xiaoming Shi, and Aimin Zhou**

East China Normal University · Shanghai AI Lab · Beihang University

**Findings of ACL 2025** · [Paper](https://aclanthology.org/2025.findings-acl.425/) · [PDF](https://aclanthology.org/2025.findings-acl.425.pdf) · [Dataset download](https://github.com/hml-github/Flow2Code/releases/tag/v1.0.0) · [Citation](#citation)

## Overview

This repository hosts the official dataset for **Flow2Code**, a benchmark for evaluating whether multimodal language models can translate flowcharts into code. Flowcharts express program logic through visual structure, including branches, loops, and operation sequences. Flow2Code studies how well models recover that logic across different diagram styles and programming languages.

The benchmark pairs **5,622 reference programs** with **16,866 flowcharts** across **15 programming languages**. It combines tasks from ClassEval, HumanEval-X, MBXP, and MCEval, with three diagram representations for every program. The paper describes the dataset construction and quality review, evaluates 13 multimodal language models, and examines supervised fine-tuning. Its experiments identify challenges in interpreting UML and pseudocode flowcharts and show improvements from fine-tuning.

## Task definition

Given a flowchart and an instruction specifying the target programming language, a model generates code implementing the depicted program logic. Each task offers three alternative visual inputs:

| Flowchart type | Representation |
|---|---|
| Code flowchart | Program operations and control flow with code-level labels |
| UML flowchart | The program represented in UML-style flowchart notation |
| Pseudocode flowchart | Program logic expressed with natural-language node labels |

The paired reference program and original benchmark task/test fields support further evaluation. The three images correspond to the same task and are alternative representations, rather than three independent programs.

## Dataset construction

The paper constructs flowcharts from selected reference solutions in the four source benchmarks. Visustin produces code and UML flowcharts and DOT representations. GPT-4o rewrites DOT node labels into natural-language descriptions, Gemini-2.0 checks the transformations, and Graphviz renders the pseudocode flowcharts. Human review checks the diagrams against the source programs and validates the pseudocode transformations. See Section 3 of the [paper](https://aclanthology.org/2025.findings-acl.425/) for the construction and review procedure.

## Dataset statistics

| Source | Programs in main | Languages in main |
|---|---:|---:|
| ClassEval | 100 | 1 |
| HumanEval-X | 492 | 3 |
| MBXP | 4,277 | 7 |
| MCEval | 753 | 15 |
| **Total** | **5,622** | **15 distinct languages** |

Each program has three PNG flowcharts, giving **16,866 images** in the main dataset. The languages are Python, C++, Java, JavaScript, C#, PHP, Ruby, C, Fortran, HTML, Pascal, Perl, Shell, Tcl, and Visual Basic. Full per-language counts are in [DATASET.md](DATASET.md#main-dataset).

| Package | Programs | Images | Download |
|---|---:|---:|---|
| Main dataset | **5,622** | **16,866** | [Main archive](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/flow2code-main-5622.tar.gz) |
| Supplementary: HumanEval-X JavaScript | **164** | **492** | [Supplementary archive](https://github.com/hml-github/Flow2Code/releases/download/v1.0.0/flow2code-supplementary-humaneval-x-javascript-164.tar.gz) |

The supplement provides 164 additional HumanEval-X JavaScript tasks. MBXP and MCEval JavaScript are included in main. The two packages have no overlapping task IDs.

## Dataset format and repository structure

Task records use JSON Lines, with one object per task. Each record includes:

| Field | Contents |
|---|---|
| `uid`, `dataset`, `language`, `task_id` | Task identity and source benchmark |
| `reference_code` | Prepared reference program corresponding to the diagrams |
| `source_record` | Original selected task, including source-specific problem, solution, and test fields |
| `assets` | Paths, sizes, and SHA-256 hashes for the reference code file, three PNG images, and two DOT files |
| `bundle`, `split`, `license` | Package membership, split designation, and source license |

```text
data/
  manifest.jsonl                         Main task index
  summary.json                           Counts and schema version
  records/<dataset>/<language>.jsonl     Full task records
  assets/<dataset>/<language>/<type>/    Assets from the download archive
supplementary/humaneval_x_javascript/    Separate supplementary package
scripts/validate_dataset.py              Data integrity checker
DATASET.md                               Full schema and per-language counts
LICENSES.md                              Source attribution and license terms
```

The manifest locates each full record through `record_file` and the one-based `record_line`. Asset paths are relative to the repository or archive extraction root. See [DATASET.md](DATASET.md) for the complete schema.

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

## Evaluation scope

This release provides the full dataset and an integrity checker. The paper reports a 9:1 training/test split for its fine-tuning experiments; this release uses `split: "unspecified"` and does not distribute that experimental split. Researchers should define and report their own partitions and state whether they use the main package, supplement, or both.

An evaluation harness and model inference pipeline are not included. Original test fields remain available in `source_record`, but follow their source benchmark's format and require a suitable evaluation environment. The 50 MCEval HTML tasks have empty original `test` fields; their task descriptions, reference code, and diagrams are included.

## Sources and licenses

Tasks originate from [ClassEval](https://github.com/FudanSELab/ClassEval), [HumanEval-X](https://github.com/zai-org/CodeGeeX), [MBXP](https://github.com/amazon-science/mxeval), and [MCEval](https://github.com/MCEVAL/McEval). See [LICENSES.md](LICENSES.md) for source attribution and per-subset terms; there is no single license covering all data. The validation script is MIT-licensed.

## Citation

If you use Flow2Code in your research, please cite our paper:

```bibtex
@inproceedings{he-etal-2025-flow2code,
  title = "{F}low2{C}ode: Evaluating Large Language Models for Flowchart-based Code Generation Capability",
  author = "He, Mengliang and Zeng, Jiayi and Jiang, Yankai and Zhang, Wei and Liu, Zeming and Shi, Xiaoming and Zhou, Aimin",
  booktitle = "Findings of the Association for Computational Linguistics: ACL 2025",
  month = jul,
  year = "2025",
  address = "Vienna, Austria",
  publisher = "Association for Computational Linguistics",
  pages = "8124--8146",
  doi = "10.18653/v1/2025.findings-acl.425",
  url = "https://aclanthology.org/2025.findings-acl.425/"
}
```
