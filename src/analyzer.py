"""
محلل الفروق - يحدد الاتجاه
"""
from typing import List
from .models import Reading, DifferenceAnalysis


def analyze_readings(readings: List[Reading]) -> DifferenceAnalysis:
    """
    التحليل الأساسي:
    F1 = x2 - x1
    F2 = x3 - x2
    """
    if len(readings) < 3:
        raise ValueError("نحتاج 3 قراءات على الأقل")

    sorted_r = sorted(readings, key=lambda r: r.time)
    d1, d2, d3 = sorted_r[0], sorted_r[1], sorted_r[2]

    # الفروق
    f1 = d2.angle - d1.angle
    f2 = d3.angle - d2.angle
    avg_f = (f1 + f2) / 2

    # الاتجاه
    if avg_f > 0.5:
        direction = "📈 ارتفاع"
    elif avg_f < -0.5:
        direction = "📉 انخفاض"
    else:
        direction = "➡️ ثابت"

    return DifferenceAnalysis(
        f1=f1,
        f2=f2,
        direction=direction,
        avg_f=avg_f,
    )
