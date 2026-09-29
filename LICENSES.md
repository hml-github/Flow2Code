# Licenses and attribution

Data licenses apply separately to each source subset. They are not replaced by the software license.

## Data subsets

Preserved source material retains its upstream terms. Prepared programs, DOT representations and images are organized by source subset so that downstream users can retain the corresponding attribution and conditions; they are not relicensed as one permissive collection.

| Subset | Source notice | License information |
|---|---|---|
| ClassEval | [Official README, License section](https://github.com/FudanSELab/ClassEval#license) distinguishes code from data | Data: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/); [legal text](https://creativecommons.org/licenses/by-nc/4.0/legalcode) |
| HumanEval-X | [Official dataset card](https://huggingface.co/datasets/zai-org/humaneval-x) | Apache-2.0; [retained text](licenses/Apache-2.0.txt) |
| MBXP | [Official data LICENSE](https://github.com/amazon-science/mxeval/blob/main/data/mbxp/LICENSE) | CC BY 4.0; [retained text](licenses/CC-BY-4.0.txt) |
| MCEval | [Official README, License section](https://github.com/MCEVAL/McEval#license) and [dataset card](https://huggingface.co/datasets/Multilingual-Multimodal-NLP/McEval) | Data: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); [legal text](https://creativecommons.org/licenses/by-sa/4.0/legalcode) |

Preserve the noncommercial condition of the ClassEval subset and the share-alike condition of the MCEval subset when preparing downstream distributions. Per-record license fields identify the subset; they do not erase third-party rights in the original material.

## Attribution

Credit the Flow2Code paper for its flowchart benchmark and the corresponding source benchmark authors for the reused task/code/test material:

- ClassEval: *ClassEval: A Manually-Crafted Benchmark for Evaluating LLMs on Class-level Code Generation*, Du et al.; [source](https://github.com/FudanSELab/ClassEval).
- HumanEval-X: *CodeGeeX: A Pre-Trained Model for Code Generation with Multilingual Benchmarking on HumanEval-X*, Zheng et al.; [source](https://github.com/zai-org/CodeGeeX).
- MBXP: *Multi-lingual Evaluation of Code Generation Models*, Athiwaratkun et al.; [source](https://github.com/amazon-science/mxeval).
- MCEval: *McEval: Massively Multilingual Code Evaluation*, Chai et al.; [source](https://github.com/MCEVAL/McEval).

The dataset includes adapted reference programs and derived flowchart/DOT representations. Original selected task and test fields are retained in `source_record`. Preserve the corresponding source attribution and license terms when redistributing these materials.

## Validation tool

`scripts/validate_dataset.py` is covered by [the MIT license](licenses/Flow2Code-tools-MIT.txt). This software license does not apply to the task data, programs, tests, diagrams or DOT files.
