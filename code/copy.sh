cd ./run_dct/eval_instance

find . -type f -name '*_80.json*' -exec sh -c '
  for f; do
    target="../../evaluation/eval#14/instances/${f#./}"  # relative Pfad ohne ./ 
    mkdir -p "$(dirname "$target")"                      # Zielordner erstellen
    cp "$f" "$target"
  done
' sh {} +
