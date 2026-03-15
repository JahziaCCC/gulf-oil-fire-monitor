from fire_detector import get_fires
from smoke_path import estimate_smoke_path
from air_quality import get_air_quality
from reporter import send_report

fires = get_fires()
smoke = estimate_smoke_path()
air = get_air_quality()

report = f"""
🔥 رصد الحرائق النفطية في دول الخليج

════════════════════
🔥 عدد الحرائق المرصودة: {len(fires)}

🌫️ مسار الدخان
الاتجاه: {smoke['direction']}

المناطق المحتملة:
{', '.join(smoke['impact'])}

════════════════════
🌍 جودة الهواء

"""

for city,val in air.items():
    report += f"{city}: AQI {val}\n"

send_report(report)
