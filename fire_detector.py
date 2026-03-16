import requests

MIN_LAT = 22
MAX_LAT = 31
MIN_LON = 47
MAX_LON = 57

ROUND_DECIMALS = 2
MIN_COUNT_FOR_SUSPECT = 4

# مواقع حرارية ثابتة/مشاعل معروفة تقريبياً
KNOWN_FLARES = [
    (27.72, 52.18),
    (27.71, 52.19),
    (27.50, 52.64),
    (27.51, 52.63),
    (27.51, 52.62),
    (25.64, 49.39),
    (25.34, 50.20),
    (25.34, 50.21),
    (27.02, 49.58),
    (25.93, 49.70),
    (25.48, 50.13),
    (24.95, 51.59),
    (23.31, 54.18),
    (30.39, 49.86),
    (30.72, 49.82),
]

# مواقع يمكن اعتبارها حساسة/قريبة من نشاط نفطي أو صناعي
PRIORITY_ZONES = [
    {"name": "المنطقة الشرقية", "lat": 25.0, "lon": 49.5, "radius": 1.3},
    {"name": "شمال الخليج", "lat": 29.8, "lon": 48.5, "radius": 1.5},
    {"name": "الساحل القطري", "lat": 25.5, "lon": 51.3, "radius": 1.0},
    {"name": "الساحل الإماراتي الغربي", "lat": 24.3, "lon": 53.5, "radius": 1.2},
]


def in_gulf(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def is_near(lat1, lon1, lat2, lon2, threshold=0.12):
    return abs(lat1 - lat2) <= threshold and abs(lon1 - lon2) <= threshold


def is_known_flare(lat, lon):
    for fl_lat, fl_lon in KNOWN_FLARES:
        if is_near(lat, lon, fl_lat, fl_lon, threshold=0.12):
            return True
    return False


def near_priority_zone(lat, lon):
    for zone in PRIORITY_ZONES:
        if abs(lat - zone["lat"]) <= zone["radius"] and abs(lon - zone["lon"]) <= zone["radius"]:
            return zone["name"]
    return None


def fetch_csv_rows(url):
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200 or not r.text.strip():
            return []

        lines = r.text.splitlines()
        if len(lines) < 2:
            return []

        header = [h.strip() for h in lines[0].split(",")]
        lat_idx = header.index("latitude")
        lon_idx = header.index("longitude")

        rows = []
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) <= max(lat_idx, lon_idx):
                continue
            try:
                lat = float(parts[lat_idx])
                lon = float(parts[lon_idx])
            except Exception:
                continue

            if in_gulf(lat, lon):
                rows.append({"lat": lat, "lon": lon})

        return rows

    except Exception as e:
        print("fetch error:", url, e)
        return []


def get_fires():
    urls = [
        "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/snpp/csv/SUOMI_VIIRS_C2_Global_24h.csv",
        "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/noaa20/csv/J1_VIIRS_C2_Global_24h.csv",
    ]

    raw_points = []
    for url in urls:
        raw_points.extend(fetch_csv_rows(url))

    if not raw_points:
        return {
            "raw_count": 0,
            "cluster_count": 0,
            "suspected_count": 0,
            "clusters": [],
        }

    clustered = {}
    for p in raw_points:
        key = (round(p["lat"], ROUND_DECIMALS), round(p["lon"], ROUND_DECIMALS))
        clustered.setdefault(key, 0)
        clustered[key] += 1

    all_clusters = []
    for (lat, lon), count in clustered.items():
        zone_name = near_priority_zone(lat, lon)

        # استبعاد المشاعل الثابتة
        if is_known_flare(lat, lon):
            continue

        # عتبة الاشتباه الأساسية
        if count < MIN_COUNT_FOR_SUSPECT:
            continue

        # تعزيز فقط للمواقع الأقرب للمناطق ذات الأهمية
        if not zone_name and count < 6:
            continue

        all_clusters.append({
            "lat": lat,
            "lon": lon,
            "count": count,
            "zone": zone_name if zone_name else "منطقة عامة",
        })

    all_clusters.sort(key=lambda x: x["count"], reverse=True)

    return {
        "raw_count": len(raw_points),
        "cluster_count": len(clustered),
        "suspected_count": len(all_clusters),
        "clusters": all_clusters[:8],
    }
