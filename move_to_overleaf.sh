#!/bin/bash

# Quell- und Zielordner definieren
QUELLE="/Users/fabian/uni/Bachelorarbeit/tex/bachelorarbeit-fabian-alich/tex"
ZIEL="/Users/fabian/uni/Bachelorarbeit/682487b555c0d63c84fc8118"

cp "$QUELLE/thesis.tex" $ZIEL
cp "$QUELLE/chapters"/*.tex "$ZIEL/chapters"
cp -r "$QUELLE/figures"/* "$ZIEL/figures"
cp "$QUELLE/bibliography.bib" "$ZIEL/bibliography.bib"

echo "Alle .tex-Dateien wurden von $QUELLE nach $ZIEL kopiert."

cd $ZIEL
git pull
git add .
git commit -m "Update Overleaf project with new files"
git push

echo "Änderungen wurden in das Overleaf-Projekt übertragen."
