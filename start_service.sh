#!/bin/bash
update-ipsets
python3 ./updateDatabase.py
cron
uvicorn server:server --host=0.0.0.0
