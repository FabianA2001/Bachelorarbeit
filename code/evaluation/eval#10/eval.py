import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import asdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dc_triangulation import (
    SAT,
    Graph_Wrapper,
    Node,
    SAT_Parameter,
    load_nodes_from_json,
)

TITEL_FONT_SIZE = 35
LABEL_FONT_SIZE = 26
ACHSEN_FONT_SIZE = 20


def sat_algorithm(nodes):
    graph = Graph_Wrapper(nodes)
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_atleast=True,
        fix_hull=True,
        all_edges=True,
        # exclude_edges=True,
        solver_name="Gluecard4",
        degree_encoding=9,
    )
    solution = solver.solve({"timeout": 1200, "args": asdict(para)})
    assert solution["success"], "SAT solver did not find a solution"
    edges = graph.get_all_active_edges()
    # Berechne Kantenlängen
    return [
        calculate_edge_length(
            graph.get_pos_from_node(edge[0]), graph.get_pos_from_node(edge[1])
        )
        for edge in edges
    ]


def calculate_edge_length(point1: tuple[int, int], point2: tuple[int, int]):
    """Berechnet die Länge einer Kante zwischen zwei Knoten."""

    # Berechne euklidische Distanz
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx * dx + dy * dy)


def analyze_edge_distribution():
    """Analysiert die Kantenlängenverteilung für alle Instanztypen."""
    path = os.path.join(os.path.dirname(__file__), "instances")
    cache_file = os.path.join(os.path.dirname(__file__), "edge_lengths_cache.json")

    # Lade existierenden Cache falls vorhanden
    cached_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            print(f"Cache geladen mit {len(cached_data)} Einträgen")
        except Exception as e:
            print(f"Fehler beim Laden des Caches: {e}")
            cached_data = {}

    # Dictionary um Daten für jeden Instanztyp zu sammeln
    instance_data = defaultdict(list)
    new_calculations = 0

    # Lade alle Instanzen und sammle Kantenlängen
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name)
        if not os.path.isdir(dir_path):
            continue

        print(f"Processing {dir_name}...")

        for file in sorted(os.listdir(dir_path)):
            file_path = os.path.join(dir_path, file)
            cache_key = f"{dir_name}/{file}"

            try:
                # Prüfe ob bereits im Cache vorhanden
                if cache_key in cached_data:
                    print(f"  Verwende gecachte Daten für {file}")
                    edge_lengths = cached_data[cache_key]
                else:
                    print(f"  Berechne neue Daten für {file}")
                    nodes: list[Node] = load_nodes_from_json(file_path)
                    edge_lengths = sat_algorithm(nodes)

                    # Speichere im Cache
                    cached_data[cache_key] = edge_lengths
                    new_calculations += 1

                    # Speichere Cache nach jedem SAT-Lauf
                    try:
                        with open(cache_file, "w") as f:
                            json.dump(cached_data, f, indent=2)
                        print(f"  Cache aktualisiert für {file}")
                    except Exception as e:
                        print(f"  Fehler beim Speichern des Caches für {file}: {e}")

                instance_data[dir_name].extend(edge_lengths)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    if new_calculations > 0:
        print(f"Insgesamt {new_calculations} neue Berechnungen durchgeführt")

    return instance_data


def create_edge_length_distribution_plots(instance_data, max_x: int, max_y: int):
    """Erstellt 5 Diagramme für die Kantenlängenverteilung."""

    # Set up the plotting style
    plt.style.use("default")
    sns.set_palette(["slategray"])

    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    # fig.suptitle(
    #     "Kantenlängenverteilung nach Instanztyp", fontsize=16, fontweight="bold"
    # )

    # Flatten axes for easier iteration
    axes_flat = axes.flatten()

    instance_types = list(instance_data.keys())

    for i, instance_type in enumerate(instance_types):
        ax = axes_flat[i]
        edge_lengths = instance_data[instance_type]

        if not edge_lengths:
            ax.text(
                0.5,
                0.5,
                f"Keine Daten für\n{instance_type}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(f"{instance_type.capitalize()}")
            continue

        # Erstelle Histogramm mit Kurve
        # bins = range(0, max_x + 1, 0.1)  # Adaptiere Bin-Anzahl an einzigartige Werte
        # bins = range(50)
        bins = np.arange(0, 1.04, 0.04)
        sns.histplot(
            edge_lengths,
            bins=bins,
            # kde=True,
            alpha=0.6,
            ax=ax,
            stat="percent",
            color="#696969",
        )

        # Setze Achsengrenzen
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)

        # Statistiken berechnen
        mean_length = sum(edge_lengths) / len(edge_lengths)
        max_length = max(edge_lengths)
        min_length = min(edge_lengths)

        # Titel und Labels
        ######################
        # HACK
        if instance_type == "d_flips":
            instance_type = "Delaunay-Flips"
        else:
            instance_type = instance_type.capitalize()
        ######################
        ax.set_title(
            f"{instance_type}",
            fontweight="bold",
            fontsize=TITEL_FONT_SIZE,
        )
        # ax.set_title(
        #     f"{instance_type.capitalize()}\nmin={min_length:.2f}, max={max_length:.2f}",
        #     fontweight="bold",
        #     fontsize=TITEL_FONT_SIZE,
        # )
        ax.set_xlabel("Kantenlänge", fontsize=LABEL_FONT_SIZE)
        ax.set_ylabel("Häufigkeit(%)", fontsize=LABEL_FONT_SIZE)

        # Schriftgröße der Achsen-Zahlen anpassen
        ax.tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

        # Grid für bessere Lesbarkeit
        ax.grid(True, alpha=0.3)

    # Hide the last subplot if we have exactly 5 instance types
    if len(instance_types) == 5:
        axes_flat[5].set_visible(False)

    plt.tight_layout()

    # Save the plot
    output_path = os.path.join(
        os.path.dirname(__file__), "edge_length_distribution_plots.pdf"
    )
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Diagramme gespeichert unter: {output_path}")

    plt.show()


def create_comparison_plot(instance_data):
    """Erstellt ein Vergleichsdiagramm aller Instanztypen."""

    plt.figure(figsize=(14, 8))

    # Prepare data for box plot
    data_for_plot = []
    labels = []

    for instance_type, edge_lengths in instance_data.items():
        if edge_lengths:
            data_for_plot.append(edge_lengths)
            labels.append(instance_type.capitalize())

    # Create box plot
    plt.subplot(1, 2, 1)
    box_plot = plt.boxplot(data_for_plot, patch_artist=True)

    # Set labels manually
    plt.xticks(range(1, len(labels) + 1), labels)

    # Color the boxes
    colors = sns.color_palette("husl", len(data_for_plot))
    for patch, color in zip(box_plot["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    plt.title("Kantenlängenverteilung Vergleich (Boxplot)", fontweight="bold")
    plt.xlabel("Instanztyp")
    plt.ylabel("Kantenlänge")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    # Create violin plot
    plt.subplot(1, 2, 2)

    # Prepare data for seaborn
    plot_data = []
    for instance_type, edge_lengths in instance_data.items():
        for length in edge_lengths:
            plot_data.append(
                {"Instance Type": instance_type.capitalize(), "Edge Length": length}
            )

    df = pd.DataFrame(plot_data)

    if not df.empty:
        sns.violinplot(data=df, x="Instance Type", y="Edge Length", palette="husl")
        plt.title("Kantenlängenverteilung Vergleich (Violinplot)", fontweight="bold")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save comparison plot
    output_path = os.path.join(
        os.path.dirname(__file__), "edge_length_distribution_comparison.pdf"
    )
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Vergleichsdiagramm gespeichert unter: {output_path}")

    plt.show()


def print_statistics(instance_data):
    """Druckt Statistiken für alle Instanztypen."""
    print("\n" + "=" * 60)
    print("KANTENLÄNGENVERTEILUNGSSTATISTIKEN")
    print("=" * 60)

    for instance_type, edge_lengths in instance_data.items():
        if not edge_lengths:
            continue

        print(f"\n{instance_type.upper()}:")
        print(f"  Anzahl Kanten: {len(edge_lengths)}")
        print(f"  Mittelwert: {sum(edge_lengths) / len(edge_lengths):.2f}")
        print(f"  Minimum: {min(edge_lengths):.2f}")
        print(f"  Maximum: {max(edge_lengths):.2f}")
        print(
            f"  Standardabweichung: {(sum((x - sum(edge_lengths) / len(edge_lengths)) ** 2 for x in edge_lengths) / len(edge_lengths)) ** 0.5:.2f}"
        )

        # Häufigste Kantenlängenbereiche (gerundet auf 1 Dezimalstelle)
        rounded_lengths = [round(length, 1) for length in edge_lengths]
        length_counts = Counter(rounded_lengths)
        most_common = length_counts.most_common(3)
        print(f"  Häufigste Kantenlängen (gerundet): {most_common}")


def mean_data(instance_data_old):
    instance_data = defaultdict(list)
    for instance_type, edge_lengths in instance_data_old.items():
        max_length = max(edge_lengths)
        for edge_length in edge_lengths:
            # Normalisiere Kantenlängen auf 0-1 Skala
            assert max_length > 0, "Maximale Kantenlänge darf nicht 0 sein"
            normalized_length = edge_length / max_length
            instance_data[instance_type].append(normalized_length)
    return instance_data


if __name__ == "__main__":
    print("Analysiere Kantenlängenverteilungen...")

    # Analysiere die Daten
    instance_data = analyze_edge_distribution()

    instance_data = mean_data(instance_data)

    # Erstelle Diagramme
    create_edge_length_distribution_plots(instance_data, 1, 20)

    # # Erstelle Vergleichsdiagramm
    # create_comparison_plot(instance_data)

    # # Drucke Statistiken
    # print_statistics(instance_data)
