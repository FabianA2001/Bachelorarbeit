cd ./run_dct/eval_instance

find . -type f -name '*130*' -exec sh -c '
  for f; do
    target="../../evaluation/eval#15/instances/${f#./}"  # relative Pfad ohne ./ 
    mkdir -p "$(dirname "$target")"                      # Zielordner erstellen
    cp "$f" "$target"
  done
' sh {} +
