def classify_event(fire_data, smoke_data, air_data):
    raw_count = fire_data.get("raw_count", 0)
    suspected_count = fire_data.get("suspected_count", 0)
    clusters = fire_data.get("clusters", [])

    smoke_detected = smoke_data.get("smoke_detected", False)
    smoke_direction = smoke_data.get("direction", "لا يوجد")
    has_air_data = bool(air_data)

    top_count = 0
    if clusters:
        top_count = clusters[0].get("count", 0)

    # درجة أولية من 100
    score = 0

    if raw_count > 0:
        score += 5

    if suspected_count > 0:
        score += 20

    if suspected_count >= 2:
        score += 10

    if top_count >= 6:
        score += 10

    if top_count >= 10:
        score += 10

    if smoke_detected:
        score += 20

    if smoke_direction not in ["لا يوجد", "قيد التطوير", "غير معروف"]:
        score += 10

    if has_air_data:
        score += 15

    if score > 100:
        score = 100

    # التصنيف
    if suspected_count == 0:
        level = "🟢 طبيعي"
        label = "طبيعي"
        explanation = "لا توجد مواقع غير معتادة حاليًا بعد الفلترة."
    elif suspected_count > 0 and not smoke_detected and not has_air_data:
        if top_count >= 10:
            level = "🟠 اشتباه"
            label = "اشتباه"
            explanation = "توجد مواقع حرارية غير معتادة، لكنها غير مدعومة بالدخان أو جودة الهواء بعد."
        else:
            level = "🟡 مراقبة"
            label = "مراقبة"
            explanation = "توجد إشارات حرارية غير معتادة تستحق المتابعة."
    elif suspected_count > 0 and smoke_detected and not has_air_data:
        level = "🟠 حدث مرجح"
        label = "حدث مرجح"
        explanation = "تم رصد حرارة غير معتادة مع مؤشرات دخان، ما يرفع احتمال وجود حدث فعلي."
    elif suspected_count > 0 and smoke_detected and has_air_data:
        level = "🔴 حدث مؤكد"
        label = "حدث مؤكد"
        explanation = "الحدث مدعوم بحرارة غير معتادة ودخان وبيانات جودة هواء."
    else:
        level = "🟡 مراقبة"
        label = "مراقبة"
        explanation = "المعطيات الحالية تحتاج متابعة إضافية."

    return {
        "score": score,
        "level": level,
        "label": label,
        "explanation": explanation
    }
