/**
 * محاكي الكاميرا - التفاعل
 */

// ==================== الحالة ====================

const state = {
    readings: {
        D1: null,
        D2: null,
        D3: null,
    },
    startTime: Date.now(),
    currentPoint: 'D1',
};

const POINTS = ['D1', 'D2', 'D3'];
const POINT_POSITIONS = {
    D1: 0.20,  // 20% من اليسار
    D2: 0.50,  // 50% من اليسار
    D3: 0.80,  // 80% من اليسار
};


// ==================== الرسم ====================

function drawGrid() {
    const canvas = document.getElementById('gridCanvas');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // خلفية
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, w, h);

    // الخطوط الأفقية (الدرجات)
    ctx.strokeStyle = '#2a2a3e';
    ctx.lineWidth = 1;

    for (let angle = 0; angle <= 90; angle += 10) {
        const y = h - (angle / 100) * h;

        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();

        // تسمية
        ctx.fillStyle = '#a8a8b3';
        ctx.font = '20px monospace';
        ctx.textAlign = 'right';
        ctx.fillText(`${angle}°`, w - 10, y - 5);
    }

    // خط 90° (القمة)
    ctx.strokeStyle = '#2ecc71';
    ctx.lineWidth = 3;
    const y90 = h - (90 / 100) * h;
    ctx.beginPath();
    ctx.moveTo(0, y90);
    ctx.lineTo(w, y90);
    ctx.stroke();

    // خط 0° (الأرض)
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, h);
    ctx.lineTo(w, h);
    ctx.stroke();
}


// ==================== الأعمدة ====================

function setupColumns() {
    const overlay = document.getElementById('columnsOverlay');
    overlay.innerHTML = '';

    POINTS.forEach((point, i) => {
        const pos = POINT_POSITIONS[point] * 100;

        // الخط
        const line = document.createElement('div');
        line.className = `column-line ${point.toLowerCase()}`;
        line.style.left = `${pos}%`;
        overlay.appendChild(line);

        // التسمية
        const label = document.createElement('div');
        label.className = 'column-label';
        label.style.left = `${pos}%`;
        label.textContent = point;
        overlay.appendChild(label);
    });
}


// ==================== النقر ====================

document.getElementById('cameraView').addEventListener('click', (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const relX = x / rect.width;
    const relY = 1 - (y / rect.height);  // 0 = أسفل، 1 = أعلى

    // تحديد العمود الأقرب
    let closestPoint = null;
    let minDist = 0.15;  // 15% من العرض

    POINTS.forEach(point => {
        const pointX = POINT_POSITIONS[point];
        const dist = Math.abs(relX - pointX);

        if (dist < minDist) {
            minDist = dist;
            closestPoint = point;
        }
    });

    if (!closestPoint) {
        showStatus('⚠️ انقر بالقرب من أحد الأعمدة (D1, D2, D3)', 'warning');
        return;
    }

    // التحقق من التسلسل
    const expectedPoint = getNextPoint();
    if (closestPoint !== expectedPoint && state.readings[closestPoint] !== null) {
        showStatus(`⚠️ يجب النقر على ${expectedPoint} أولاً`, 'warning');
        return;
    }

    // حساب الدرجة
    const angle = Math.round(relY * 100);
    const clampedAngle = Math.max(0, Math.min(90, angle));

    // حساب الزمن
    const time = (Date.now() - state.startTime) / 1000;

    // حفظ
    state.readings[closestPoint] = {
        angle: clampedAngle,
        time: parseFloat(time.toFixed(2)),
    };

    // رسم علامة
    addMarker(closestPoint, clampedAngle);

    // تحديث الحالة
    updateReadings();
    updateStatus();
});


function addMarker(point, angle) {
    const overlay = document.getElementById('columnsOverlay');
    const pos = POINT_POSITIONS[point] * 100;
    const yPos = 100 - angle;

    // إزالة علامة سابقة
    const oldMarker = overlay.querySelector(`[data-marker="${point}"]`);
    if (oldMarker) oldMarker.remove();

    const marker = document.createElement('div');
    marker.className = 'marker';
    marker.dataset.marker = point;
    marker.style.left = `${pos}%`;
    marker.style.top = `${yPos}%`;
    marker.title = `${point}: ${angle}°`;
    overlay.appendChild(marker);
}


function getNextPoint() {
    if (state.readings.D1 === null) return 'D1';
    if (state.readings.D2 === null) return 'D2';
    if (state.readings.D3 === null) return 'D3';
    return null;
}


// ==================== التحديث ====================

function updateReadings() {
    POINTS.forEach(point => {
        const row = document.querySelector(`[data-point="${point}"]`);
        const angleEl = row.querySelector('.angle-display');
        const timeEl = row.querySelector('.time-display');

        const reading = state.readings[point];
        if (reading) {
            angleEl.textContent = `${reading.angle}°`;
            timeEl.textContent = `${reading.time.toFixed(2)} ث`;
        } else {
            angleEl.textContent = '—';
            timeEl.textContent = '—';
        }
    });

    // تفعيل زر التحليل
    const allSet = POINTS.every(p => state.readings[p] !== null);
    document.getElementById('analyzeBtn').disabled = !allSet;
}


function updateStatus() {
    const next = getNextPoint();

    if (next) {
        const colors = { D1: '#3498db', D2: '#2ecc71', D3: '#e74c3c' };
        showStatus(`📍 التالي: انقر على ${next}`, 'info');
    } else {
        showStatus('✅ جميع القراءات مسجلة — جاهز للتحليل!', 'success');
    }
}


function showStatus(message, type = 'info') {
    const el = document.getElementById('statusMessage');
    el.textContent = message;
    el.className = `status-message ${type}`;
}


function clearReading(point) {
    state.readings[point] = null;

    // إزالة العلامة
    const overlay = document.getElementById('columnsOverlay');
    const marker = overlay.querySelector(`[data-marker="${point}"]`);
    if (marker) marker.remove();

    // إعادة تعيين الوقت
    state.startTime = Date.now();

    updateReadings();
    updateStatus();
}


function resetAll() {
    state.readings = { D1: null, D2: null, D3: null };
    state.startTime = Date.now();

    // مسح العلامات
    document.querySelectorAll('.marker').forEach(m => m.remove());

    updateReadings();
    updateStatus();
}


function loadExample() {
    state.readings = {
        D1: { angle: 85, time: 0.0 },
        D2: { angle: 65, time: 1.0 },
        D3: { angle: 45, time: 2.0 },
    };
    state.startTime = Date.now() - 2000;

    // مسح ثم رسم العلامات
    document.querySelectorAll('.marker').forEach(m => m.remove());
    POINTS.forEach(p => {
        addMarker(p, state.readings[p].angle);
    });

    updateReadings();
    updateStatus();
}


// ==================== التحليل ====================

async function analyzeJourney() {
    const distance = parseFloat(document.getElementById('distance').value);
    const dt = parseFloat(document.getElementById('dt').value);

    showStatus('⏳ جاري التحليل...', 'info');

    try {
        const response = await fetch('/analyze_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                readings: state.readings,
                distance: distance,
                dt: dt,
            }),
        });

        const data = await response.json();

        if (data.success) {
            showResults(data);
            showStatus('✅ اكتمل التحليل!', 'success');
        } else {
            showStatus(`❌ ${data.error}`, 'warning');
        }
    } catch (error) {
        showStatus(`❌ خطأ: ${error.message}`, 'warning');
    }
}


function showResults(data) {
    const content = document.getElementById('resultsContent');

    // بناء الجدول
    let tableHtml = `
        <div class="results-section">
            <h3>📊 التحليل</h3>
            <p>
                <strong>F1</strong> = <code>${data.analysis.f1.toFixed(2)}°</code><br>
                <strong>F2</strong> = <code>${data.analysis.f2.toFixed(2)}°</code><br>
                <strong>متوسط</strong> = <code>${data.analysis.avg_f.toFixed(2)}°</code><br>
                <strong>الاتجاه</strong> = ${data.analysis.direction}
            </p>
        </div>
    `;

    // جدول الرحلة
    tableHtml += `
        <div class="results-section">
            <h3>🎯 الرحلة (${data.blocks.length} مربعات)</h3>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>المربع</th>
                        <th>x1</th>
                        <th>x2</th>
                        <th>x3</th>
                        <th>الزمن</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.blocks.forEach(block => {
        tableHtml += `
            <tr>
                <td><strong>${block.name}</strong></td>
                <td>${block.x1.toFixed(1)}°</td>
                <td>${block.x2.toFixed(1)}°</td>
                <td>${block.x3.toFixed(1)}°</td>
                <td>${block.t1.toFixed(2)} ث</td>
            </tr>
        `;
    });

    tableHtml += `</tbody></table></div>`;

    // الصورة
    if (data.chart_base64) {
        tableHtml += `
            <div class="results-section">
                <h3>📈 الرسم</h3>
                <img src="data:image/png;base64,${data.chart_base64}"
                     class="results-image" alt="الرحلة">
            </div>
        `;
    }

    // الملخص
    if (data.summary) {
        let summaryHtml = '<div class="results-section"><h3>📋 ملخص الرحلة</h3><p>';
        for (const [key, value] of Object.entries(data.summary)) {
            summaryHtml += `<strong>${key}:</strong> <code>${value}</code><br>`;
        }
        summaryHtml += '</p></div>';
        tableHtml += summaryHtml;
    }

    content.innerHTML = tableHtml;
    document.getElementById('resultsModal').classList.add('active');
}


function closeModal() {
    document.getElementById('resultsModal').classList.remove('active');
}


// ==================== التهيئة ====================

window.addEventListener('load', () => {
    setupColumns();

    // تأخير صغير لضمان تحميل الـ canvas
    setTimeout(drawGrid, 100);

    updateStatus();
});

window.addEventListener('resize', () => {
    setTimeout(drawGrid, 100);
});
