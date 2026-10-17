"""
📷 محاكي الكاميرا - خادم Flask                          """                                                     import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))                                                        from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use("Agg")                                   import matplotlib.pyplot as plt                         import io
import base64                                           
from src.models import Reading
from src import analyzer, predictor                     from src.config import REPORTS_DIR                      
app = Flask(__name__)


# ==================== الصفحة الرئيسية ====================

@app.route("/")
def index():
    return render_template("camera.html")


# ==================== التحليل ====================

@app.route("/analyze_camera", methods=["POST"])
def analyze_camera():
    try:
        data = request.json
        readings_data = data["readings"]
        distance = float(data.get("distance", 10.0))
        dt = float(data.get("dt", 1.0))

        # تحويل لـ Reading
        readings = []
        for point in ["D1", "D2", "D3"]:
            r = readings_data[point]
            readings.append(Reading(
                point_name=point,
                angle=float(r["angle"]),
                time=float(r["time"]),
            ))

        # التحليل
        analysis = analyzer.analyze_readings(readings)

        # التنبؤ
        blocks = predictor.predict_journey(
            readings, analysis,
            distance=distance, dt=dt,
        )

        # الملخص
        summary = predictor.journey_summary(blocks, analysis)

        # الرسم
        chart_b64 = make_chart(readings, blocks, analysis, distance)

        return jsonify({
            "success": True,
            "analysis": {
                "f1": analysis.f1,
                "f2": analysis.f2,
                "avg_f": analysis.avg_f,
                "direction": analysis.direction,
            },
            "blocks": [
                {
                    "name": b.name,
                    "x1": b.x1, "x2": b.x2, "x3": b.x3,
                    "t1": b.t1, "t2": b.t2, "t3": b.t3,
                }
                for b in blocks
            ],
            "summary": summary,
            "chart_base64": chart_b64,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


# ==================== الرسم ====================

def make_chart(readings, blocks, analysis, distance):
    """رسم الرحلة كـ base64"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")
    ax.grid(True, alpha=0.3, linestyle="--")

    x_d1, x_d2, x_d3 = 0, distance / 2, distance

    # الأعمدة
    for x_pos, label in [(x_d1, "D1"), (x_d2, "D2"), (x_d3, "D3")]:
        ax.axvline(x_pos, color="#E53935", linewidth=3, zorder=2)
        ax.text(x_pos, 95, label, ha="center", va="bottom",
                fontsize=16, fontweight="bold", color="#E53935")

    # الرحلة
    colors = ["#E53935", "#43A047", "#8E24AA",
              "#F57C00", "#1E88E5", "#00ACC1", "#D81B60"]

    for i, block in enumerate(blocks):
        color = colors[i % len(colors)]
        xs = [x_d1, x_d2, x_d3]
        ys = [block.x1, block.x2, block.x3]

        ax.plot(xs, ys, "o-",
                color=color, linewidth=2.5,
                markersize=14,
                markeredgecolor="white", markeredgewidth=2,
                label=f"{block.name} @ {block.t1:.1f}ث",
                zorder=5 + i, alpha=0.85)

    # خطوط
    ax.axhline(0, color="#000", linewidth=2, alpha=0.5)
    ax.axhline(90, color="#000", linewidth=2, alpha=0.5)

    # المحاور
    ax.set_title("🎯 رحلة A الكاملة", fontsize=18, fontweight="bold", pad=20)
    ax.set_xlabel("الموضع (D1 ← D3)", fontsize=13, fontweight="bold")
    ax.set_ylabel("الدرجة (°)", fontsize=13, fontweight="bold")
    ax.set_xlim(-1, distance + 1)
    ax.set_ylim(-5, 100)
    ax.set_xticks([x_d1, x_d2, x_d3])
    ax.set_xticklabels(["D1", "D2", "D3"], fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)

    # تحويل
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")


# ==================== التشغيل ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  📷 محاكي الكاميرا")
    print("=" * 60)
    print("\n  📱 افتح المتصفح على:")
    print("     http://localhost:5001")
    print("\n  ⛔ للإيقاف: Ctrl+C")
    print("=" * 60 + "\n")

    app.run(host="0.0.0.0", port=5001, debug=False)
.../0/motion_analyzer $ ls
REPORT.md       data                        static
app_camera.py   flask.log                   templates
app_flask.py    generate_three_examples.py  ts.text
app_web.py      main_journey.py
buildozer.spec  src
.../0/motion_analyzer $ cat main_journey.py
"""
🚀 المشروع الرئيسي - رحلة A الكاملة
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models import Reading
from src import analyzer, predictor, visualizer
from src.config import DEFAULT_DISTANCE


def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def get_input():
    """إدخال البيانات"""
    print_header("📝 إدخال البيانات")

    print("\n💡 أدخل القيم: (الدرجة + الزمن) عند كل نقطة\n")

    readings = []
    for i, name in enumerate(["D1", "D2", "D3"]):
        print(f"📍 {name}:")

        try:
            angle = float(input(f"   📐 الدرجة (0-90): ").strip())
            if angle < 0 or angle > 90:
                print("   ⚠️ الدرجة يجب أن تكون بين 0 و 90")
                return None
        except ValueError:
            print("   ❌ قيمة غير صحيحة")
            return None

        default_t = str(i * 1.0)
        try:
            t = float(input(f"   ⏱️  الزمن [{default_t}]: ").strip() or default_t)
        except ValueError:
            t = i * 1.0

        readings.append(Reading(point_name=name, angle=angle, time=t))

    # المسافة
    print("\n📊 إعدادات الرحلة:")
    try:
        distance = float(input(f"   📏 المسافة بين D1 و D3 [{DEFAULT_DISTANCE}]: ").strip()
                       or str(DEFAULT_DISTANCE))
    except ValueError:
        distance = DEFAULT_DISTANCE

    return readings, distance


def main():
    print("\n" + "=" * 65)
    print(f"{'🚀 رحلة A - تلقائي حتى 0° أو 90°':^65}")
    print("=" * 65)

    # ==================== الإدخال ====================
    result = get_input()
    if not result:
        return
    readings, distance = result

    # ==================== التحليل ====================
    print_header("📊 التحليل")
    analysis = analyzer.analyze_readings(readings)
    print(analysis.summary())

    # ==================== التنبؤ ====================
    print_header("🔮 بناء الرحلة الكاملة (تلقائي)")
    print("\n⏳ سيتم البناء حتى الوصول إلى 0° أو 90°...\n")

    blocks = predictor.predict_journey(
        readings, analysis,
        distance=distance,
        dt=1.0,
        num_blocks=None,  # تلقائي
    )

    print(f"✅ تم بناء {len(blocks)} مربع:\n")

    # عرض مختصر
    print(f"{'المربع':<6} {'x1':>8} {'x2':>8} {'x3':>8} {'الزمن':>8}")
    print("-" * 45)
    for block in blocks:
        print(f"{block.name:<6} {block.x1:>7.2f}° {block.x2:>7.2f}° "
              f"{block.x3:>7.2f}° {block.t1:>6.2f}ث")

    # ==================== ملخص ====================
    print_header("📊 ملخص الرحلة")
    summary = predictor.journey_summary(blocks, analysis)

    for key, value in summary.items():
        print(f"  {key}: {value}")

    # ==================== الرسم ====================
    print_header("🎨 توليد الرسوم")

    path1 = visualizer.plot_journey(readings, blocks, analysis, distance)
    print(f"   📁 {path1.name}")

    path2 = visualizer.plot_summary(blocks)
    print(f"   📁 {path2.name}")

    print("\n" + "=" * 65)
    print(f"  ✅ اكتمل!")
    print(f"  📂 {path1.parent}")
    print("=" * 65)


if __name__ == "__main__":
    main()
