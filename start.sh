#!/bin/bash
set -e

python3 /app/restreamer.py &
python3 /app/dashboard/backend.py &
exec supervisord -c /etc/supervisord.conf