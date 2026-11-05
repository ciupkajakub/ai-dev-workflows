#!/bin/bash
status=0
python3 -B -m unittest discover -s tests || status=1
python3 -B scripts/check_export.py || status=1
echo "check.sh finished"
exit $status
