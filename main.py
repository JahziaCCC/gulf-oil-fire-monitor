from fire_detector import get_fires
from smoke_path import estimate_smoke_path
from air_quality import get_air_quality
from reporter import send_report


def build_report():

    fires = get_fires()
    air = get_air_quality()

    report = []
    report.append("🔥 رصد الحرائق النفطية في دول الخليج")
    report.append("")
    report.append("════════════════════")
    report.append(f"🔥 عدد الحرائق المرصودة: {len(fires)}")
    report.append("")

    # لا يوجد حريق
    if len(fires) == 0:

        report.append("📌 الحالة:")
        report.append("لا توجد حرائق نفطية مرصودة حاليًا داخل نطاق الخليج.")
        report.append("")

        report.append("════════════════════")
        report.append("🌫️ مسار الدخان")
        report.append("لا يوجد مسار دخان نشط لعدم وجود حريق مرصود.")
        report.append("")

        report.append("════════════════════")
        report.append("🌍 جودة الهواء")
        report.append("يتم عرض جودة الهواء العامة فقط دون ربطها بحريق نفطي.")
        report.append("")

        if not air:
            report.append("لا توجد بيانات جودة هواء حقيقية متاحة حاليًا.")

        return "\n".join(report)

    # يوجد حريق

    smoke = estimate_smoke_path()

    report.append("📌 الحالة:")
    report.append("تم رصد نشاط حراري داخل نطاق الخليج ويجري التحقق من طبيعته.")
    report.append("")

    report.append("════════════════════")
    report.append("🌫️ مسار الدخان")

    report.append(f"الاتجاه: {smoke['direction']}")

    if smoke["impact"]:

        report.append("")
        report.append("المناطق المحتملة:")

        for area in smoke["impact"]:
            report.append(f"• {area}")

    report.append("")

    report.append("════════════════════")
    report.append("🌍 جودة الهواء")
    report.append("المؤشرات للمتابعة العامة:")
    report.append("")

    if not air:

        report.append("لا توجد بيانات جودة هواء حقيقية متاحة حاليًا.")

    else:

        for city, val in air.items():
            report.append(f"{city}: AQI {val}")

    return "\n".join(report)


if __name__ == "__main__":

    report = build_report()

    send_report(report)
