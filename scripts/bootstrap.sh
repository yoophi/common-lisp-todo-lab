#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v sbcl >/dev/null || { echo 'Install SBCL first: brew install sbcl openssl@3 sqlite' >&2; exit 1; }
if [ ! -x .tools/qlot/bin/qlot ]; then
  mkdir -p .tools
  curl -fL --retry 3 https://github.com/fukamachi/qlot/releases/download/1.8.4/qlot-1.8.4.tar.gz -o .tools/qlot.tar.gz
  printf '%s  %s\n' '1b97df7d7ac3b32f6350d0519a048792f2c4da497d43e6346bbe47e488b50ff4' '.tools/qlot.tar.gz' | shasum -a 256 -c -
  tar xzf .tools/qlot.tar.gz -C .tools
fi
.tools/qlot/scripts/setup.sh
.tools/qlot/bin/qlot install
