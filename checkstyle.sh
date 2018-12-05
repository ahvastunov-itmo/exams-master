#!/bin/bash

flake8 --ignore F401,E402 \
       --exclude .git,__pycache__,venv \
       --max-complexity=10
