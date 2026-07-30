#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

python3 -m pip install --upgrade flet
flet build ipa \
  --product "Gerador de Senhas - RBS" \
  --org "br.com.rbs" \
  --project "gerador_senhas_rbs"

echo "Concluído. Verifique a pasta build/ipa."
