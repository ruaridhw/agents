#!/bin/sh
# Development checks only; the renderer itself remains stdlib-only.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$HERE"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

python3 -m unittest discover -s tests -v
npm exec --yes --package prettier@3.8.1 -- prettier --check \
  '**/*.{css,html,js,json,md}' .htmlvalidate.json .stylelintrc.json
npm exec --yes --package stylelint@16.26.1 -- stylelint \
  --config .stylelintrc.json assets/triage.css
node --check assets/theme.js
for input in examples/*.json; do
  python3 scripts/render_triage.py "$input" "$TMP/$(basename "$input" .json).html"
done
npm exec --yes --package html-validate@10.9.0 -- html-validate \
  --config .htmlvalidate.json assets/page.html "$TMP"/*.html
npm exec --yes --package prettier@3.8.1 -- prettier --write "$TMP"/*.html
