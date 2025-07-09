import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Seaborn Style setzen
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)


def create_cactus_plot():
    """
    Erstellt einen Cactus Plot zur Visualisierung von Algorithm Performance.
    In einem Cactus Plot wird die Zeit (y-Achse) gegen die Anzahl der gelösten
    Instanzen (x-Achse) dargestellt, sortiert nach Laufzeit.
    """

    # Beispieldaten für verschiedene Algorithmen generieren
    np.random.seed(42)

    # Simuliere Laufzeiten für drei verschiedene Algorithmen
    n_instances = 100

    # Algorithm 1: Schnell für einfache Instanzen, langsamer für schwere
    alg1_times = np.concatenate(
        [
            np.random.exponential(0.5, 60),  # Schnelle Instanzen
            np.random.exponential(2.0, 30),  # Mittlere Instanzen
            np.random.exponential(10.0, 10),  # Schwere Instanzen
        ]
    )

    # Algorithm 2: Konstantere Performance
    alg2_times = np.random.exponential(1.5, n_instances)

    # Algorithm 3: Sehr schnell für die meisten, aber einige Ausreißer
    alg3_times = np.concatenate(
        [
            np.random.exponential(0.3, 80),  # Sehr schnelle Instanzen
            np.random.exponential(15.0, 20),  # Einige sehr langsame
        ]
    )

    # Daten sortieren (wichtig für Cactus Plot)
    alg1_sorted = np.sort(alg1_times)
    alg2_sorted = np.sort(alg2_times)
    alg3_sorted = np.sort(alg3_times)

    # X-Achse: Anzahl der gelösten Instanzen
    x_values = np.arange(1, n_instances + 1)

    # Plot erstellen
    plt.figure(figsize=(12, 8))

    # Drei Algorithmen plotten
    plt.plot(
        x_values,
        alg1_sorted,
        "o-",
        label="Algorithmus 1",
        linewidth=2,
        markersize=4,
        alpha=0.8,
    )
    plt.plot(
        x_values,
        alg2_sorted,
        "s-",
        label="Algorithmus 2",
        linewidth=2,
        markersize=4,
        alpha=0.8,
    )
    plt.plot(
        x_values,
        alg3_sorted,
        "^-",
        label="Algorithmus 3",
        linewidth=2,
        markersize=4,
        alpha=0.8,
    )

    # Timeout-Linie hinzufügen (z.B. bei 20 Sekunden)
    timeout = 20
    plt.axhline(
        y=timeout, color="red", linestyle="--", label=f"Timeout ({timeout}s)", alpha=0.7
    )

    # Styling
    plt.xlabel("Anzahl gelöste Instanzen", fontsize=12)
    plt.ylabel("Laufzeit (Sekunden)", fontsize=12)
    plt.title(
        "Cactus Plot - Algorithmus Performance Vergleich",
        fontsize=14,
        fontweight="bold",
    )
    plt.legend(loc="upper left", fontsize=11)
    plt.grid(True, alpha=0.3)

    # Y-Achse logarithmisch skalieren (oft nützlich bei Cactus Plots)
    plt.yscale("log")

    # Layout optimieren
    plt.tight_layout()

    return plt.gcf()


# Beispiel für die Verwendung
if __name__ == "__main__":
    # Einfacher Cactus Plot
    print("Erstelle einfachen Cactus Plot...")
    fig1 = create_cactus_plot()
    plt.show()

    # Optional: Plots speichern
    # fig1.savefig('cactus_plot_basic.png', dpi=300, bbox_inches='tight')
    # fig2.savefig('cactus_plot_advanced.png', dpi=300, bbox_inches='tight')
    # fig3.savefig('cactus_plot_percentiles.png', dpi=300, bbox_inches='tight')
