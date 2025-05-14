#!/bin/bash

# Quell- und Zielordner definieren
QUELLE="../682487b555c0d63c84fc8118"
ZIEL="tex"

cd $QUELLE
git pull
cd ..

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
