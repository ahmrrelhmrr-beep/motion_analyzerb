"""
الفئات الأساسية للمشروع
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Reading:
    """قراءة واحدة عند نقطة قياس"""
    point_name: str          # D1, D2, D3
    angle: float             # الدرجة (0-90)
    time: float              # الزمن

    def __str__(self):
        return f"{self.point_name}: {self.angle:.1f}° @ {self.time:.2f}ث"


@dataclass
class DifferenceAnalysis:
    """تحليل الفروق"""
    f1: float                # الفرق الأول (x2 - x1)
    f2: float                # الفرق الثاني (x3 - x2)
    direction: str           # "انخفاض" أو "ارتفاع" أو "ثابت"
    avg_f: float             # متوسط الفرقين

    def summary(self) -> str:
        return (
            f"📊 تحليل الفروق\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"F1 = {self.f1:+.2f}°\n"
            f"F2 = {self.f2:+.2f}°\n"
            f"متوسط = {self.avg_f:+.2f}°\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"الاتجاه: {self.direction}"
        )


@dataclass
class Block:
    """مربع واحد من رحلة A"""
    name: str                          # B1, B2, B3...
    x1: float                          # درجة عند D1
    x2: float                          # درجة عند D2
    x3: float                          # درجة عند D3
    t1: float                          # زمن عند D1
    t2: float                          # زمن عند D2
    t3: float                          # زمن عند D3
    distance: float                    # المسافة بين D1 و D3

    def summary(self) -> str:
        return (
            f"📦 {self.name}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"D1: {self.x1:6.1f}° @ {self.t1:.2f}ث\n"
            f"D2: {self.x2:6.1f}° @ {self.t2:.2f}ث\n"
            f"D3: {self.x3:6.1f}° @ {self.t3:.2f}ث\n"
            f"المسافة: {self.distance:.1f}م"
        )

    @property
    def is_below_zero(self) -> bool:
        """هل وصلنا إلى ما دون 0°؟"""
        return self.x3 <= 0

    @property
    def is_above_ninety(self) -> bool:
        """هل وصلنا إلى ما فوق 90°؟"""
        return self.x1 >= 90
