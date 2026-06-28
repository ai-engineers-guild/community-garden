from __future__ import annotations

from pathlib import Path


def write_radar_chart(garden_health: dict, path: Path) -> Path:
    import math

    import matplotlib.pyplot as plt

    radar = garden_health.get("radar", {})
    labels = list(radar.keys())
    values = [radar[k].get("score") if radar[k].get("score") is not None else 0 for k in labels]
    if not labels:
        labels = ["no_data"]
        values = [0]
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    values += values[:1]
    angles += angles[:1]
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values, linewidth=1)
    ax.fill(angles, values, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_title("Garden Health Radar")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
