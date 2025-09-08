#!/bin/bash

# Quell- und Zielordner definieren
QUELLE="/Users/fabian/uni/Bachelorarbeit/682487b555c0d63c84fc8118"
ZIEL="/Users/fabian/uni/Bachelorarbeit/bachelorarbeit-fabian-alich/tex"

git -C "$QUELLE/." pull

cp "$QUELLE/beamer.tex" $ZIEL
cp "$QUELLE/thesis.tex" $ZIEL
cp -r "$QUELLE/beamer_chapters"/*.tex "$ZIEL/beamer_chapters"
cp -r "$QUELLE/chapters"/*.tex "$ZIEL/chapters"
cp -r "$QUELLE/figures"/* "$ZIEL/figures"
cp "$QUELLE/bibliography.bib" "$ZIEL/bibliography.bib"

echo "Alle .tex-Dateien wurden von $QUELLE nach $ZIEL kopiert."
