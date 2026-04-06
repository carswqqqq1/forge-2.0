#!/bin/zsh
set -e

cd "/Users/carsonweso/Documents/Forge 2.0"

./dev.sh up -d --remove-orphans
open http://localhost:5173
