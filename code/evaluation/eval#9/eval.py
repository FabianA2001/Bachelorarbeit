import os
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dc_triangulation import Node, load_nodes_from_json

TITEL_FONT_SIZE = 35
LABEL_FONT_SIZE = 26
ACHSEN_FONT_SIZE = 20


def analyze_degree_distribution():
    """Analysiert die Gradverteilung für alle Instanztypen."""
    path = os.path.join(os.path.dirname(__file__), "instances")

    # Dictionary um Daten für jeden Instanztyp zu sammeln
    instance_data = defaultdict(list)

    # Lade alle Instanzen und sammle Graddaten
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name)
        if not os.path.isdir(dir_path):
            continue

        print(f"Processing {dir_name}...")

        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            try:
                nodes: list[Node] = load_nodes_from_json(file_path)

                # Extrahiere Grade (ignoriere -1 Werte)
                degrees = [node.degree for node in nodes if node.degree != -1]
                instance_data[dir_name].extend(degrees)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    return instance_data


def create_degree_distribution_plots(instance_data, max_x: int, max_y: float):
    """Erstellt 5 Diagramme für die Gradverteilung."""

    # Set up the plotting style
    plt.style.use("default")
    sns.set_palette(["slategray"])

    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    # fig.suptitle(
    #     "Gradverteilung der Knoten nach Instanztyp", fontsize=16, fontweight="bold"
    # )

    # Flatten axes for easier iteration
    axes_flat = axes.flatten()

    instance_types = list(instance_data.keys())

    for i, instance_type in enumerate(instance_types):
        ax = axes_flat[i]
        degrees = instance_data[instance_type]

        if not degrees:
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
        # Verwende mehr Bins für bessere Verteilung

        # bins = min(50, len(set(degrees)))  # Adaptiere Bin-Anzahl an einzigartige Werte
        # bins = len(set(degrees)) * 5  # Adaptiere Bin-Anzahl an einzigartige Werte
        sns.histplot(
            degrees,
            bins=range(0, max_x + 1),
            # kde=True,
            alpha=0.6,
            ax=ax,
            stat="percent",
            color="#696969",
        )

        # # Setze Achsengrenzen
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)

        # Statistiken berechnen
        mean_degree = sum(degrees) / len(degrees)
        max_degree = max(degrees)
        min_degree = min(degrees)

        # Titel und Labels
        # Titel und Labels
        ######################
        # HACK
        if instance_type == "delaunay_Flips":
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
        #     f"{instance_type.capitalize()}\nmin={min_degree}, max={max_degree}",
        #     fontweight="bold",
        #     fontsize=TITEL_FONT_SIZE,
        # )
        ax.set_xlabel("Grad der Knoten", fontsize=LABEL_FONT_SIZE)
        ax.set_ylabel("Häufigkeit (%)", fontsize=LABEL_FONT_SIZE)

        # Schriftgröße der Achsen-Zahlen anpassen
        ax.tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

        # # Vertikale Linie für Mittelwert
        # ax.axvline(
        #     mean_degree,
        #     color="red",
        #     linestyle="--",
        #     alpha=0.8,
        #     label=f"Mittelwert: {mean_degree:.1f}",
        # )
        # ax.legend()

        # Grid für bessere Lesbarkeit
        ax.grid(True, alpha=0.3)

    # Hide the last subplot if we have exactly 5 instance types
    if len(instance_types) == 5:
        axes_flat[5].set_visible(False)

    plt.tight_layout()

    # Save the plot
    output_path = os.path.join(os.path.dirname(__file__), "gradverteilung.pdf")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Diagramme gespeichert unter: {output_path}")

    plt.show()


def create_comparison_plot(instance_data):
    """Erstellt ein Vergleichsdiagramm aller Instanztypen."""

    plt.figure(figsize=(14, 8))

    # Prepare data for box plot
    data_for_plot = []
    labels = []

    for instance_type, degrees in instance_data.items():
        if degrees:
            data_for_plot.append(degrees)
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

    plt.title("Gradverteilung Vergleich (Boxplot)", fontweight="bold")
    plt.xlabel("Instanztyp")
    plt.ylabel("Grad der Knoten")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    # Create violin plot
    plt.subplot(1, 2, 2)

    # Prepare data for seaborn
    plot_data = []
    for instance_type, degrees in instance_data.items():
        for degree in degrees:
            plot_data.append(
                {"Instance Type": instance_type.capitalize(), "Degree": degree}
            )

    df = pd.DataFrame(plot_data)

    if not df.empty:
        sns.violinplot(data=df, x="Instance Type", y="Degree", palette="husl")
        plt.title("Gradverteilung Vergleich (Violinplot)", fontweight="bold")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save comparison plot
    output_path = os.path.join(
        os.path.dirname(__file__), "degree_distribution_comparison.pdf"
    )
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Vergleichsdiagramm gespeichert unter: {output_path}")

    plt.show()


def print_statistics(instance_data):
    """Druckt Statistiken für alle Instanztypen."""
    print("\n" + "=" * 60)
    print("GRADVERTEILUNGSSTATISTIKEN")
    print("=" * 60)

    for instance_type, degrees in instance_data.items():
        if not degrees:
            continue

        print(f"\n{instance_type.upper()}:")
        print(f"  Anzahl Knoten: {len(degrees)}")
        print(f"  Mittelwert: {sum(degrees) / len(degrees):.2f}")
        print(f"  Minimum: {min(degrees)}")
        print(f"  Maximum: {max(degrees)}")
        print(
            f"  Standardabweichung: {(sum((x - sum(degrees) / len(degrees)) ** 2 for x in degrees) / len(degrees)) ** 0.5:.2f}"
        )

        # Häufigste Grade
        degree_counts = Counter(degrees)
        most_common = degree_counts.most_common(3)
        print(f"  Häufigste Grade: {most_common}")


if __name__ == "__main__":
    print("Analysiere Gradverteilungen...")

    # Analysiere die Daten
    instance_data = analyze_degree_distribution()

    # Erstelle Diagramme
    create_degree_distribution_plots(instance_data, 25, 35)

    # Erstelle Vergleichsdiagramm
    # create_comparison_plot(instance_data)

    # Drucke Statistiken
    print_statistics(instance_data)
