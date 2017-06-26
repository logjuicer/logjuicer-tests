#!/bin/env python3
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import glob
import json
import os
import subprocess
import yaml

import numpy as np

DEBUG=False

def usage():
    p = argparse.ArgumentParser()
    p.add_argument("--debug", action="store_true", help="Print debug")
    p.add_argument("cases", default=['tests/*'], nargs='*')
    args = p.parse_args()
    if args.debug:
        global DEBUG
        DEBUG=True
    return args

def run(case_path):
    info = yaml.safe_load(open(os.path.join(case_path, "inf.yaml")))
    good_path = glob.glob(os.path.join(case_path, "*.good"))[0]
    fail_path = glob.glob(os.path.join(case_path, "*.fail"))[0]

    cmd = ["logreduce", "--baseline", good_path, fail_path,
           "--output-format", "json", "--context-length", "0"]
    if info.get("max-distance"):
        cmd.extend(["--max-distance", str(info["max-distance"])])
    if DEBUG:
        print("Running [%s]" % " ".join(cmd))
        stderr = None
    else:
        stderr = subprocess.PIPE
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr)
    results = json.loads(p.communicate()[0].decode('utf-8'))
    accuracy = []
    for anomaly in info["anomalies"]:
        if anomaly["lines"][-1] == "\n":
            anomaly["lines"] = anomaly["lines"][:-1]
        anomaly["found"] = False
        for _, result in results.items():
            if anomaly.get("filename"):
                # TODO: check filename chunks
                pass
            result.setdefault("found", [])
            chunk_pos = 0
            for chunk in result["chunks"]:
                if anomaly["lines"] in chunk:
                    anomaly["found"] = True
                    result["found"].append(chunk_pos)
                    break
                chunk_pos += 1
            if anomaly["found"]:
                break
        if anomaly["found"]:
            accuracy.append(1.)
        elif not anomaly.get("optional"):
            accuracy.append(0.)
            if DEBUG:
                print("Didn't catch anomaly: [%s]" % anomaly["lines"])

    # Look for falsepositive
    false_positives = []
    for _, result in results.items():
        chunk_pos = 0
        for chunk in result["chunks"]:
            if chunk_pos in result["found"]:
                false_positives.append(0.)
            else:
                if DEBUG:
                    print("False positive found: [%s]" % chunk)
                false_positives.append(1.)
            chunk_pos += 1

    return np.mean(accuracy), np.mean(false_positives)


def main():
    args = usage()
    accuracies, fps = [], []
    for case in args.cases:
        for case_path in glob.glob(case):
            if case_path[-1] == "/":
                case_path = case_path[:-1]
            accuracy, false_positives = run(case_path)
            print("%20s: %03.2f%% accuracy, %03.2f%% false-positive" % (
                os.path.basename(case_path), accuracy * 100,
                false_positives * 100))
            accuracies.append(accuracy)
            fps.append(false_positives)
    mean_accuracy = np.mean(accuracies)
    mean_fp = np.mean(fps)
    result = "SUCCESS" if mean_accuracy > 0.95 and mean_fp < 0.25 else "FAILED"
    print("%s: %03.2f%% accuracy, %03.2f%% false-positive" % (
        result, mean_accuracy * 100, mean_fp * 100))
    exit(result != "SUCCESS")


if __name__ == "__main__":
    main()
