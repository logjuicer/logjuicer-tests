# logjuicer-tests: evaluation datasets

This repository contains annotated datasets to evaluate
[logjuicer](https://github.com/logjuicer/logjuicer-tests) anomaly detection capability.

Each dataset contains:

- *.good: a baseline log file.
- *.fail: a failure log file.
- inf.yaml: the anomalies annotation to be found in the failure logs.

## Usage

Perform the evaluation using the `test` subcommand, from the logjuicer repository:

```ShellSession
$ cargo run -p logjuicer-cli -- test ../logjuicer-tests/datasets/*
```
