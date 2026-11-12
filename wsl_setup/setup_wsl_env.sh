#!/usr/bin/env bash
# A executer DANS Ubuntu (WSL), depuis ce dossier :
#   cd /mnt/c/Users/FlavieHIEN/Documents/memoire_master/Dossier_de_travail/wsl_setup
#   bash setup_wsl_env.sh
set -e

echo "== 1/4 : dependances systeme (Tesseract OCR + francais) =="
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-fra build-essential

echo "== 2/4 : installation de Miniconda (si absent) =="
if [ ! -d "$HOME/miniconda3" ]; then
  curl -fsSL -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash /tmp/miniconda.sh -b -p "$HOME/miniconda3"
  rm /tmp/miniconda.sh
fi
source "$HOME/miniconda3/etc/profile.d/conda.sh"

echo "== 3/4 : creation de l'environnement conda memoire_env =="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
conda env create -f "$SCRIPT_DIR/environment.yml" || conda env update -f "$SCRIPT_DIR/environment.yml"
conda activate memoire_env

echo "== 4/4 : modele spaCy francais + kernel Jupyter =="
python -m spacy download fr_core_news_sm
python -m ipykernel install --user --name memoire_env --display-name "Python (memoire_env - WSL)"

echo ""
echo "Termine. Dans VS Code : ouvrez test.ipynb, cliquez sur le selecteur de kernel"
echo "en haut a droite, choisissez 'Python (memoire_env - WSL)'."
echo "(Il faut l'extension 'WSL' et 'Jupyter' installees dans VS Code.)"
