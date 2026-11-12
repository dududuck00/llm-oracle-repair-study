# Test oracle repair replication artifact

This artifact reproduces numerical results from the study of test oracle repair. It uses saved evaluation records and runs offline with Python 3.9 or newer and the standard library.

```bash
python3 artifact/verify_and_reproduce.py
```

The verifier checks file hashes, runs the bundled analysis in a temporary directory and reaggregates the two HumanEval sources into 105 result groups. It writes the reproduced HumanEval table rows to `artifact/reproduced/`.

## Studies and files

| Study | Evidence in this artifact |
| --- | --- |
| Evidence | Both HumanEval sources cover 164 tasks with eight fixed inputs per task. Qwen materials have five judges and Gemma materials have two. The 40 reused and 124 added tasks are subsets of each full source. |
| Representation | MBPP+ results for direct generation and explicit derivation with raw or automatically typed output, plus finite encoding controls. |
| Candidate decisions | Finite experiments on candidate supply and submission, including comparisons with submission-matched masks. |
| Actions | Finite cases that compare generated actions with decisions computed from the same semantic judgments. |

- `artifact/verify_and_reproduce.py` and `artifact/render_dual_source_tables.py` are the verification and HumanEval table entry points.
- `artifact/gemma-data.json`, `artifact/gemma-summary.json` and `artifact/qwen-summary.json` contain processed results. `artifact/gemma-PROTOCOL.json` records the Gemma-source settings.
- `artifact/replay-inputs.zip` contains the companion Qwen-source data, offline scoring and aggregation modules, and frozen inputs and outputs used by the verifier for MBPP+ and the finite controls.
- `artifact/expected/` contains the HumanEval rows checked by the verifier. `artifact/paper-tables/` contains reference copies of the 22 tables used by the current main and supplementary manuscripts. These copies include presentation changes made after the analysis was frozen.
- `artifact/SHA256SUMS.json` records the artifact file hashes.

The replay starts from processed records, including the original failure and deferral flags. A fresh inference run requires the corresponding benchmark and model versions. The benchmark sources are [HumanEval](https://github.com/openai/human-eval), [MBPP](https://github.com/google-research/google-research/tree/master/mbpp) and [EvalPlus](https://github.com/evalplus/evalplus).
