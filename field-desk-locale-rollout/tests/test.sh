#!/bin/sh
set -eu
mkdir -p /logs/verifier
printf '%s\n' '{"overall":0.0,"functional_correctness":0.0,"constraint_satisfaction":0.0,"robustness":0.0,"artifact_quality":0.0}' > /logs/verifier/reward.json
python /tests/verify.py > /logs/verifier/test-stdout.txt 2>&1
cat /logs/verifier/test-stdout.txt
