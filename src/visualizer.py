"""
رسم المسار والرحلة الكاملة
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from .config import REPORTS_DIR
from .models import Reading, DifferenceAnalysis, Block


def _save(fig, name):
    path = REPORTS_DIR / f"{name}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"   ✅ {path.name}")
    return path


def plot_journey(
    readings: list,
    blocks: list,
    analysis: DifferenceAnalysis,
    distance: float = 10.0,
    title: str = "🎯 رحلة A الكاملة",
) -> Path:
    """
    رسم رحلة A كاملة مع الأعمدة
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")
    ax.grid(True, alpha=0.3, linestyle="--")

    # ==================== الأعمدة D1, D2, D3 ====================
    # مواقع الأعمدة
    x_d1 = 0
    x_d2 = distance / 2
    x_d3 = distance

    # أعمدة حمراء
    for x_pos, label in [(x_d1, "D1"), (x_d2, "D2"), (x_d3, "D3")]:
        ax.axvline(x_pos, color="#E53935", linewidth=3, zorder=2)

        # سلم الدرجات
        for angle in range(0, 100, 10):
            ax.plot([x_pos - 0.15, x_pos + 0.15], [angle, angle],
                    color="#333", linewidth=1.5, zorder=3)

        # العنوان
        ax.text(x_pos, 95, label, ha="center", va="bottom",
                fontsize=16, fontweight="bold", color="#E53935")

        # 0° و 90°
        ax.text(x_pos, -2, "0°", ha="center", va="top",
                fontsize=11, fontweight="bold", color="#333")
        ax.text(x_pos, 92, "90°", ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#333")

    # ==================== الرحلة ====================
    colors = ["#E53935", "#43A047", "#8E24AA",
              "#F57C00", "#1E88E5", "#00ACC1", "#D81B60"]

    # نقاط القراءة الحقيقية
    sorted_r = sorted(readings, key=lambda r: r.time)
    ax.scatter(
        [x_d1, x_d2, x_d3],
        [r.angle for r in sorted_r],
        color="#E53935", s=200,
        edgecolors="white", linewidths=3,
        zorder=10, label="B1 (قراءات أصلية)"
    )

    # كل مربع B
    for i, block in enumerate(blocks):
        color = colors[i % len(colors)]

        # نقاط المربع
        xs = [x_d1, x_d2, x_d3]
        ys = [block.x1, block.x2, block.x3]

        # خط المسار
        ax.plot(xs, ys, "o-",
                color=color, linewidth=2.5,
                markersize=14,
                markeredgecolor="white", markeredgewidth=2,
                label=f"{block.name} @ t={block.t1:.1f}ث",
                zorder=5 + i, alpha=0.85)

        # تسمية
        ax.annotate(
            f"{block.name}\n{block.x1:.0f}°→{block.x2:.0f}°→{block.x3:.0f}°",
            (x_d3 + 0.3, block.x3),
            fontsize=10, fontweight="bold",
            color=color, va="center",
            bbox=dict(boxstyle="round,pad=0.3",
                     facecolor="white", edgecolor=color,
                     linewidth=2, alpha=0.95),
            zorder=15
        )

    # ==================== خط 0° و 90° ====================
    ax.axhline(0, color="#000", linewidth=2, alpha=0.5, zorder=1)
    ax.axhline(90, color="#000", linewidth=2, alpha=0.5, zorder=1)

    # ==================== العنوان والمحاور ====================
    ax.set_title(title, fontsize=18, fontweight="bold", pad=20)
    ax.set_xlabel("الموضع (D1 ← D3)", fontsize=13, fontweight="bold")
    ax.set_ylabel("الدرجة (°)", fontsize=13, fontweight="bold")
    ax.set_xlim(-1, distance + 3)
    ax.set_ylim(-5, 100)
    ax.set_xticks([x_d1, x_d2, x_d3])
    ax.set_xticklabels(["D1", "D2", "D3"], fontsize=12, fontweight="bold")

    # ==================== Legend ====================
    ax.legend(loc="upper right", fontsize=10,
              framealpha=0.95, edgecolor="#BDBDBD", ncol=1)

    # ==================== معلومات التحليل ====================
    info = (
        f"📊 التحليل\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"F1 = {analysis.f1:+.1f}°\n"
        f"F2 = {analysis.f2:+.1f}°\n"
        f"متوسط = {analysis.avg_f:+.1f}°\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{analysis.direction}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"عدد المربعات: {len(blocks)}"
    )

    ax.text(0.02, 0.98, info,
            transform=ax.transAxes,
            fontsize=10, va="top", ha="left",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.6",
                     facecolor="#ECF0F1",
                     edgecolor="#1976D2", linewidth=2),
            zorder=20)

    plt.tight_layout()
    return _save(fig, "journey_plot")


def plot_summary(blocks: list) -> Path:
    """
    رسم ملخص رقمي لكل المربعات
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("white")
    ax.axis("off")

    # عنوان
    ax.text(0.5, 0.97, "🎯 ملخص الرحلة",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=20, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.6",
                     facecolor="#1976D2", edgecolor="none"),
            color="white")

    # جدول
    y = 0.85
    ax.text(0.05, y, "المربع    x1       x2       x3       الزمن",
            transform=ax.transAxes,
            fontsize=13, fontweight="bold",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.3",
                     facecolor="#E3F2FD",
                     edgecolor="#1976D2"),
            va="top")

    y -= 0.06

    for i, block in enumerate(blocks):
        text = (
            f"{block.name:6}  "
            f"{block.x1:7.2f}°  "
            f"{block.x2:7.2f}°  "
            f"{block.x3:7.2f}°  "
            f"{block.t1:5.2f}ث"
        )

        color = "#FAFAFA" if i % 2 == 0 else "#F5F5F5"

        ax.text(0.05, y, text,
                transform=ax.transAxes,
                fontsize=12,
                family="monospace",
                bbox=dict(boxstyle="round,pad=0.3",
                         facecolor=color,
                         edgecolor="#BDBDBD"),
                va="top")
        y -= 0.06

    return _save(fig, "journey_summary")
