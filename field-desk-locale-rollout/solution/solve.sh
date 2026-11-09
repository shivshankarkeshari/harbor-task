#!/bin/sh
set -eu
cd /app
git apply /solution/fix.patch
mkdir -p /app/output
printf '%s\n' '{"status":"complete","known_issues":[]}' > /app/output/completion.json
