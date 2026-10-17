"""
التطبيق التفاعلي - محلل حركة A
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Reading
from src import analyzer, predictor, visualizer, storage
from src.config import READINGS_FILE


def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_menu():
    print("\n" + "=" * 65)
    print(f"{'🚀 محلل حركة A':^65}")
    print("=" * 65)
    print("  1. ➕ إدخال قيم D1, D2, D3")
    print("  2. 📊 عرض التحليل")
    print("  3. 🎯 التنبؤ بالمسار")
    print("  4. 🎨 توليد الرسوم")
    print("  5. 💾 حفظ القراءات")
    print("  6. 📂 تحميل القراءات")
    print("  0. 🚪 خروج")
    print("=" * 65)


current_readings = []


def input_readings():
    global current_readings
    print_header("➕ إدخال قيم D1, D2, D3")

    print("\n💡 أدخل قيم القياس عند كل نقطة\n")

    readings = []
    for i, name in enumerate(["D1", "D2", "D3"]):
        print(f"📍 النقطة {name}:")

        default_t = str(i * 1.0)
        t_input = input(f"   ⏱️  الزمن [{default_t}]: ").strip() or default_t
        try:
            t = float(t_input)
        except ValueError:
            print("   ❌ زمن غير صحيح")
            return

        v_input = input(f"   📊 القيمة: ").strip()
        if not v_input:
            print("   ❌ يجب إدخال قيمة")
            return
        try:
            v = float(v_input)
        except ValueError:
            print("   ❌ قيمة غير صحيحة")
            return

        readings.append(Reading(point_name=name, time=t, value=v))

    current_readings = readings
    print(f"\n✅ تم إدخال {len(readings)} قراءات")


def show_analysis():
    if len(current_readings) < 3:
        print("\n❌ يجب إدخال 3 قراءات أولاً")
        return None

    print_header("📊 تحليل الفروق")

    try:
        analysis = analyzer.analyze_readings(current_readings)
        print()
        print(analysis.summary())
        return analysis
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None


def predict_path():
    if len(current_readings) < 3:
        print("\n❌ يجب إدخال 3 قراءات أولاً")
        return None

    print_header("🎯 التنبؤ بالمسار")

    try:
        analysis = analyzer.analyze_readings(current_readings)
        prediction = predictor.predict(current_readings, analysis)

        # النقاط التوقعية
        print("\n💡 اختر القيم المستهدفة (مفصولة بفواصل)")
        sorted_r = sorted(current_readings, key=lambda r: r.time)
        last_value = sorted_r[2].value

        # اقترح قيماً
        suggested = [round(last_value * 0.75, 1),
                     round(last_value * 0.50, 1),
                     round(last_value * 0.25, 1)]

        print(f"   الاقتراح: {suggested}")
        user_input = input("   أو أدخل قيمك: ").strip()

        if user_input:
            try:
                targets = [float(x.strip()) for x in user_input.split(",")]
            except ValueError:
                targets = suggested
        else:
            targets = suggested

        key_points = predictor.predict_key_points(
            current_readings, analysis, targets
        )

        # عرض النتائج
        print()
        print(prediction.summary())

        print("\n" + "=" * 65)
        print("  🎯 الزمن المتوقع لقيم محددة")
        print("=" * 65)
        for i, kp in enumerate(key_points, 1):
            if kp.get("exists"):
                print(f"\n  نقطة {i}: عند قيمة {kp['value']:.2f}")
                print(f"    ⏰ الزمن = {kp['time']:.3f} ث")
                print(f"    📏 بعد {kp['dt_from_last']:.3f} ث من آخر قياس")
            else:
                print(f"\n  نقطة {i}: عند قيمة {kp['value']:.2f}")
                print(f"    ❌ لا يمكن الوصول إليها")

        return analysis, prediction, key_points
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_charts():
    if len(current_readings) < 3:
        print("\n❌ يجب إدخال 3 قراءات أولاً")
        return

    print_header("🎨 توليد الرسوم")

    try:
        analysis = analyzer.analyze_readings(current_readings)
        prediction = predictor.predict(current_readings, analysis)

        # اقترح قيماً للنقاط التوقعية
        sorted_r = sorted(current_readings, key=lambda r: r.time)
        last_value = sorted_r[2].value
        targets = [
            round(last_value * 0.75, 1),
            round(last_value * 0.50, 1),
            round(last_value * 0.25, 1),
        ]
        key_points = predictor.predict_key_points(
            current_readings, analysis, targets
        )

        charts = visualizer.generate_all(
            current_readings, analysis, prediction, key_points
        )

        print(f"\n✅ {len(charts)} رسم")
        print(f"📁 افتح: data/reports/")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


def save_readings():
    if not current_readings:
        print("\n❌ لا توجد قراءات")
        return

    data = [{"point_name": r.point_name, "time": r.time, "value": r.value}
            for r in current_readings]
    storage.save(data, READINGS_FILE)
    print(f"\n💾 تم حفظ {len(data)} قراءات")


def load_readings():
    global current_readings
    data = storage.load(READINGS_FILE)
    if not data:
        print("\n❌ لا توجد قراءات محفوظة")
        return

    current_readings = [Reading(**d) for d in data]
    print(f"\n✅ تم تحميل {len(current_readings)} قراءات")
    for r in current_readings:
        print(f"   • {r}")


def main():
    print("\n" + "=" * 65)
    print(f"{'🚀 مشروع تحليل حركة A':^65}")
    print("=" * 65)

    while True:
        print_menu()
        choice = input("\nاختر: ").strip()

        try:
            if choice == "1":
                input_readings()
            elif choice == "2":
                show_analysis()
            elif choice == "3":
                predict_path()
            elif choice == "4":
                generate_charts()
            elif choice == "5":
                save_readings()
            elif choice == "6":
                load_readings()
            elif choice == "0":
                print("\n👋 مع السلامة!")
                break
            else:
                print("❌ اختيار غير صحيح")
        except KeyboardInterrupt:
            print("\n⚠️ تم الإلغاء")
        except Exception as e:
            print(f"\n❌ خطأ: {e}")

        input("\n↵ Enter للمتابعة...")


if __name__ == "__main__":
    main()
