import os
from graph_utils import graph_const


def get_instances() -> dict[str, dict[str, str]]:
    """Lädt alle Ordner aus dem graph_const.INSTANCES_DIR Verzeichnis."""
    instances_dir = graph_const.PREFIX_INSTANCE
    instances = {}
    inst_names = [
        folder
        for folder in os.listdir(instances_dir)
        if os.path.isdir(os.path.join(instances_dir, folder))
    ]
    for inst_name in inst_names:
        inst_dir = os.path.join(instances_dir, inst_name)
        instances[inst_name] = {
            file.replace(".json", ""): os.path.join(inst_dir, file)
            for file in os.listdir(inst_dir)
            if file.endswith(".json")
        }
    return instances
