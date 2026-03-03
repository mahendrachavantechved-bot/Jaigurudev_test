# gauges.py
"""
Gauge chart generators for DSCR and LTV.
Returns base64-encoded PNG strings suitable for flet ft.Image(src_base64=...).
"""
import io
import base64
import numpy as np
import matplotlib.pyplot as plt


def dscr_gauge(dscr: float) -> str:
    fig, ax = plt.subplots(figsize=(5, 3), subplot_kw={"polar": True})
    ax.set_theta_offset(1.5708)
    ax.set_theta_direction(-1)
    ax.barh(0, 2 * np.pi, height=0.6, color="lightgray", alpha=0.3)
    green  = min(dscr, 1.5) * (np.pi / 1.5)
    yellow = min(dscr, 2.0) * (np.pi / 2.0)
    ax.barh(0, green,           height=0.6, color="green",  alpha=0.8)
    ax.barh(0, yellow - green,  left=green,  height=0.6, color="orange", alpha=0.8)
    ax.barh(0, 2 * np.pi - yellow, left=yellow, height=0.6, color="red", alpha=0.7)
    angle = min(dscr / 3.0, 1) * 2 * np.pi
    ax.plot([0, angle], [0, 1], color="black", lw=5)
    ax.plot(0, 0, marker="o", ms=15, color="black")
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.text(
        0, -0.35, f"DSCR {dscr:.2f}",
        ha="center", va="center", fontsize=20, fontweight="bold",
        transform=ax.transData
    )
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode("utf-8")


def ltv_gauge(ltv: float) -> str:
    fig, ax = plt.subplots(figsize=(5, 3), subplot_kw={"polar": True})
    ax.set_theta_offset(1.5708)
    ax.set_theta_direction(-1)
    ax.barh(0, 2 * np.pi, height=0.6, color="lightgray", alpha=0.3)
    green  = min(ltv, 65) * (np.pi / 100) * 2
    yellow = min(ltv, 80) * (np.pi / 100) * 2
    ax.barh(0, green,           height=0.6, color="green",  alpha=0.8)
    ax.barh(0, yellow - green,  left=green,  height=0.6, color="orange", alpha=0.8)
    ax.barh(0, 2 * np.pi - yellow, left=yellow, height=0.6, color="red", alpha=0.7)
    angle = (ltv / 100) * 2 * np.pi
    ax.plot([0, angle], [0, 1], color="black", lw=5)
    ax.plot(0, 0, marker="o", ms=15, color="black")
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.text(
        0, -0.35, f"LTV {ltv:.1f}%",
        ha="center", va="center", fontsize=20, fontweight="bold",
        transform=ax.transData
    )
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode("utf-8")
