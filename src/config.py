"""إعدادات المشروع"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"

for d in [DATA_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

READINGS_FILE = DATA_DIR / "readings.pkl"

# إعدادات الرحلة
DEFAULT_DISTANCE = 10.0    # المسافة بين D1 و D3 (متر)
DEFAULT_DT = 1.0           # الفارق الزمني بين B (ثانية)
DEFAULT_NUM_BLOCKS = 5     # عدد المربعات

# الحدود
MIN_ANGLE = 0.0            # أدنى درجة
MAX_ANGLE = 90.0           # أقصى درجة
