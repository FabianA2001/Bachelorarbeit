#!/bin/bash

# Quell- und Zielordner definieren
QUELLE="/Users/fabian/uni/Bachelorarbeit/682487b555c0d63c84fc8118"
ZIEL="/Users/fabian/uni/Bachelorarbeit/tex/bachelorarbeit-fabian-alich/tex"

git -C "$QUELLE/." pull

cp "$QUELLE/thesis.tex" $ZIEL
cp "$QUELLE/chapters"/*.tex "$ZIEL/chapters"
cp "$QUELLE/figures"/* "$ZIEL/figures"
cp "$QUELLE/bibliography.bib" "$ZIEL/bibliography.bib"

echo "Alle .tex-Dateien wurden von $QUELLE nach $ZIEL kopiert."
