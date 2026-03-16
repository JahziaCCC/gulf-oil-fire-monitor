def estimate_smoke_path(has_fire=False):
    if not has_fire:
        return {
            "direction": "لا يوجد",
            "impact": []
        }

    return {
        "direction": "قيد التطوير",
        "impact": []
    }
