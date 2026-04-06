#!/bin/sh
set -eu

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${NVIDIA_API_KEY:?Set NVIDIA_API_KEY in your environment or .env file}"

python3 scripts/nvidia_chat_example.py
