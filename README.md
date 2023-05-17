# logreduce-tests: evaluation datasets

This repository contains annotated datasets to evaluate
logreduce anomaly detection capability.

Each dataset contains:

- *.good: a baseline log file.
- *.fail: a failure log file.
- inf.yaml: the anomalies annotation to be found in the failure logs.

## Usage

Perform the evaluation using the `test` subcommand, from the logreduce repository:

```ShellSession
$ cargo run -p logreduce-cli -- test ../logreduce-tests/datasets/*
```
