"""
التنبؤ بالمسار - بناء الرحلة الكاملة حتى 0° أو 90°
"""
from typing import List
from .models import Reading, DifferenceAnalysis, Block


# ==================== الحدود ====================

MIN_ANGLE = 0.0     # أدنى درجة
MAX_ANGLE = 90.0    # أقصى درجة
MAX_BLOCKS = 50     # حماية من اللانهاية


# ==================== بناء B1 ====================

def build_b1(readings: List[Reading], distance: float) -> Block:
    """بناء B1 من القراءات"""
    sorted_r = sorted(readings, key=lambda r: r.time)
    d1, d2, d3 = sorted_r[0], sorted_r[1], sorted_r[2]

    return Block(
        name="B1",
        x1=d1.angle, x2=d2.angle, x3=d3.angle,
        t1=d1.time, t2=d2.time, t3=d3.time,
        distance=distance,
    )


# ==================== بناء B التالي ====================

def build_next_block(prev: Block, f: float, dt: float,
                     direction: str, num: int) -> Block:
    """بناء B التالي من B السابق"""
    if direction == "down":
        sign = -1
    elif direction == "up":
        sign = +1
    else:
        sign = 0

    delta = sign * abs(f)

    return Block(
        name=f"B{num}",
        x1=prev.x1 + delta,
        x2=prev.x2 + delta,
        x3=prev.x3 + delta,
        t1=prev.t1 + dt,
        t2=prev.t2 + dt,
        t3=prev.t3 + dt,
        distance=prev.distance,
    )


# ==================== التحقق من نهاية الرحلة ====================

def is_journey_ended(block: Block, direction: str) -> tuple:
    """
    هل انتهت الرحلة؟

    Returns:
        (ended: bool, reason: str)
    """
    if direction == "down":
        # ننخفض → توقف عندما ينزل x3 تحت 0
        if block.x3 < MIN_ANGLE:
            return True, f"🔻 وصلنا إلى الأرض (x3 = {block.x3:.1f}°)"

    elif direction == "up":
        # نرتفع → توقف عندما يصعد x1 فوق 90
        if block.x1 > MAX_ANGLE:
            return True, f"🔺 وصلنا إلى القمة (x1 = {block.x1:.1f}°)"

    elif direction == "flat":
        # ثابت → لا نهاية، نتحكم بالعدد
        pass

    return False, ""


# ==================== بناء الرحلة الكاملة ====================

def predict_journey(
    readings: List[Reading],
    analysis: DifferenceAnalysis,
    distance: float = 10.0,
    dt: float = 1.0,
    num_blocks: int = None,
) -> List[Block]:
    """
    بناء رحلة A الكاملة
    """
    # تحديد الاتجاه
    if analysis.avg_f < -0.5:
        direction = "down"
    elif analysis.avg_f > 0.5:
        direction = "up"
    else:
        direction = "flat"

    f = analysis.avg_f

    # بناء B1
    blocks = [build_b1(readings, distance)]

    # ==================== الحالة 1: عدد محدد ====================
    if num_blocks is not None:
        for i in range(2, num_blocks + 1):
            prev = blocks[-1]
            ended, _ = is_journey_ended(prev, direction)
            if ended:
                break

            new_block = build_next_block(prev, f, dt, direction, i)
            blocks.append(new_block)

        return blocks

    # ==================== الحالة 2: تلقائي ====================
    # نتحقق من B1 أولاً
    ended_b1, _ = is_journey_ended(blocks[0], direction)

    if ended_b1:
        return blocks

    i = 2
    while i <= MAX_BLOCKS:
        prev = blocks[-1]

        # بناء B جديد
        new_block = build_next_block(prev, f, dt, direction, i)
        blocks.append(new_block)

        # هل انتهت الرحلة؟
        ended, reason = is_journey_ended(new_block, direction)
        if ended:
            break

        # حالة ثابت - 5 مربعات فقط
        if direction == "flat" and i >= 5:
            break

        i += 1

    return blocks


# ==================== ملخص الرحلة ====================

def journey_summary(blocks: List[Block], analysis: DifferenceAnalysis) -> dict:
    """ملخص الرحلة الكاملة"""
    if not blocks:
        return {}

    first = blocks[0]
    last = blocks[-1]

    # سبب التوقف
    if analysis.avg_f < -0.5:
        direction = "down"
    elif analysis.avg_f > 0.5:
        direction = "up"
    else:
        direction = "flat"

    ended, reason = is_journey_ended(last, direction)

    return {
        "عدد المربعات": len(blocks),
        "زمن البداية": f"{first.t1:.2f} ث",
        "زمن النهاية": f"{last.t1:.2f} ث",
        "المدة الكلية": f"{last.t1 - first.t1:.2f} ث",
        "درجة البداية": f"{first.x1:.1f}°",
        "درجة النهاية": f"{last.x3:.1f}°",
        "التغير الكلي": f"{last.x3 - first.x1:.1f}°",
        "سبب التوقف": reason if ended else "لم تصل للحد",
    }
