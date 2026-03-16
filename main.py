from fire_detector import get_fires
from smoke_path import estimate_smoke_path
from air_quality import get_air_quality
from reporter import send_report


def build_report():
    fire_data = get_fires()
    air = get_air_quality()

    raw_count = fire_data["raw_count"]
    cluster_count = fire_data["cluster_count"]
    suspected_count = fire_data["suspected_count"]
    clusters = fire_data["clusters"]

    has_suspected_fire = suspected_count > 0
    smoke = estimate_smoke_path(has_fire=has_suspected_fire)

    report = []
    report.append("🔥 رصد الحرائق النفطية في دول الخليج")
    report.append("")
    report.append("════════════════════")
    report.append(f"🔥 النقاط الحرارية الخام: {raw_count}")
    report.append(f"📍 المواقع الحرارية المجمعة: {cluster_count}")
    report.append(f"🛢️ المواقع النفطية المشتبه بها بعد الفلترة: {suspected_count}")
    report.append("")

    if not has_suspected_fire:
        report.append("📌 الحالة:")
        report.append("لا توجد حاليًا مواقع مشتبه بها بشكل كافٍ بعد تطبيق الفلترة الذكية.")
        report.append("")
        report.append("🧾 ملاحظة:")
        report.append("تم استبعاد جزء من الإشارات الثابتة والمشاعل المعروفة لتقليل الضجيج.")
        report.append("")
    else:
        report.append("📌 الحالة:")
        report.append("تم رصد مواقع حرارية تستحق المراجعة بعد تطبيق الفلترة الذكية.")
        report.append("")
        report.append("════════════════════")
        report.append("📍 أبرز المواقع المشتبه بها")

        for c in clusters:
            report.append(
                f"• {c['lat']}, {c['lon']} | عدد النقاط: {c['count']} | النطاق: {c['zone']}"
            )

        report.append("")

    report.append("════════════════════")
    report.append("🌫️ مسار الدخان")

    if not has_suspected_fire:
        report.append("لا يوجد مسار دخان نشط لعدم وجود موقع مشتبه به بشكل كافٍ.")
    else:
        report.append(f"الاتجاه: {smoke['direction']}")
        if smoke["impact"]:
            report.append("المناطق المحتملة:")
            for area in smoke["impact"]:
                report.append(f"• {area}")
        else:
            report.append("لا توجد مناطق تأثير محددة حاليًا.")

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

    report.append("")
    report.append("════════════════════")
    report.append("🧭 التفسير التشغيلي")

    if not has_suspected_fire:
        report.append("• تمت تصفية المشاعل والمواقع الحرارية الثابتة قدر الإمكان.")
        report.append("• عدم وجود مواقع مشتبه بها لا يعني انعدام النشاط الحراري الخام، بل يعني انخفاض الإشارات الشاذة.")
    else:
        report.append("• هذه المواقع اجتازت الفلترة الأولية وتستحق التحقق الإضافي.")
        report.append("• يلزم ربطها بالدخان والانبعاثات والرياح لتأكيد الحدث.")
        report.append("• ما زالت بعض الإشارات قد تمثل نشاطًا صناعيًا ثابتًا غير حادثي.")

    return "\n".join(report)


if __name__ == "__main__":
    send_report(build_report())
