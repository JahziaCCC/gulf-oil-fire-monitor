import random

def estimate_smoke_path():

    directions = [
        "شمال",
        "جنوب",
        "شرق",
        "غرب",
        "جنوب شرق",
        "شمال شرق"
    ]

    direction = random.choice(directions)

    impact = {
        "جنوب شرق": ["الكويت","شرق السعودية"],
        "شرق": ["البحرين","قطر"],
        "جنوب": ["السعودية"],
        "شمال": ["العراق"],
        "شمال شرق": ["إيران"],
        "غرب": ["السعودية"]
    }

    return {
        "direction": direction,
        "impact": impact.get(direction, [])
    }
