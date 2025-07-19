import os

from dc_triangulation import load_nodes_from_json

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "instances")
    for dir in os.listdir(path):
        dir_path = os.path.join(path, dir)
        if not os.path.isdir(dir_path):
            continue
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            nodes = load_nodes_from_json(file_path)
