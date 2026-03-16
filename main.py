from fire_detector import get_fires
from smoke_path import estimate_smoke_path
from air_quality import get_air_quality
from classifier import classify_event
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

    classification = classify_event(fire_data, smoke, air)

    report = []
    report.append("🔥 رصد الحرائق النفطية في دول الخليج")
    report.append("")
    report.append("════════════════════")
    report.append("📊 التقييم التنفيذي")
    report.append(f"📌 مستوى الحدث: {classification['level']}")
    report.append(f"📊 مؤشر الحدث: {classification['score']}/100")
    report.append(f"🧾 التفسير السريع: {classification['explanation']}")
    report.append("")

    report.append("════════════════════")
    report.append("🔥 الرصد الحراري")
    report.append(f"• النقاط الحرارية الخام: {raw_count}")
    report.append(f"• المواقع الحرارية المجمعة: {cluster_count}")
    report.append(f"• المواقع غير المعتادة: {suspected_count}")
    report.append("")

    if suspected_count > 0:
        report.append("📍 أبرز المواقع غير المعتادة")
        for c in clusters:
            report.append(f"• {c['lat']}, {c['lon']} | عدد النقاط: {c['count']}")
        report.append("")
    else:
        report.append("• لا توجد مواقع غير معتادة حاليًا.")
        report.append("")

    report.append("════════════════════")
    report.append("🌫️ مسار الدخان")
    if not has_suspected_fire:
        report.append("• لا يوجد مسار دخان نشط لعدم وجود موقع مشتبه به بشكل كافٍ.")
    else:
        report.append(f"• الاتجاه: {smoke['direction']}")
        if smoke["impact"]:
            report.append("• المناطق المحتملة:")
            for area in smoke["impact"]:
                report.append(f"  - {area}")
        else:
            report.append("• لا توجد مناطق تأثير محددة حاليًا.")
    report.append("")

    report.append("════════════════════")
    report.append("🌍 جودة الهواء")
    if not air:
        report.append("• لا توجد بيانات جودة هواء حقيقية متاحة حاليًا.")
    else:
        for city, val in air.items():
            report.append(f"• {city}: AQI {val}")
    report.append("")

    report.append("════════════════════")
    report.append("🧭 التوصية التشغيلية")

    if classification["label"] == "طبيعي":
        report.append("• الاستمرار في المراقبة الدورية فقط.")
        report.append("• لا حاجة إلى تصعيد حاليًا.")
    elif classification["label"] == "مراقبة":
        report.append("• متابعة التحديث القادم.")
        report.append("• لا يتم التصعيد إلا عند ظهور دلائل إضافية.")
    elif classification["label"] == "اشتباه":
        report.append("• مراجعة المواقع غير المعتادة يدويًا.")
        report.append("• انتظار طبقات الدخان والانبعاثات لتأكيد الحدث.")
    elif classification["label"] == "حدث مرجح":
        report.append("• رفع مستوى المراقبة.")
        report.append("• متابعة الدخان واتجاه الرياح بشكل أقرب.")
    elif classification["label"] == "حدث مؤكد":
        report.append("• تصعيد فوري.")
        report.append("• متابعة جودة الهواء والمناطق المتأثرة.")
    else:
        report.append("• متابعة عامة.")

    return "\n".join(report)


if __name__ == "__main__":
    send_report(build_report())
