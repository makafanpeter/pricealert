#!/bin/bash
gunicorn app:app --daemon
python worker.py
python cron.py
