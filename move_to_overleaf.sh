#!/bin/bash

# Quell- und Zielordner definieren
QUELLE="tex"
ZIEL="../682487b555c0d63c84fc8118"

# .tex-Dateien rekursiv mit Ordnerstruktur kopieren
rsync -av \
  --include='*/' \
  --include='*.tex' \
  --include='*.png' \
  --include='*.jpg' \
  --include='*.pdf' \
  --include='*.bib' \
  --exclude='*' \
  --exclude='thesis.pdf' \
  "$QUELLE"/ "$ZIEL"

echo "Alle .tex-Dateien wurden von $QUELLE nach $ZIEL kopiert."

cd $ZIEL
git pull
git add .
git commit -m "Update Overleaf project with new files"
git push
