import requests

# نطاق الخليج
MIN_LAT = 22
MAX_LAT = 31
MIN_LON = 47
MAX_LON = 57

# تقريب الإحداثيات لتجميع النقاط المتقاربة
ROUND_DECIMALS = 2


def in_gulf(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def classify_point(lat, lon):
    """
    تصنيف أولي مبسط جدًا.
    سنطوره لاحقًا بربطه بمواقع منشآت ومشاعل معروفة.
    """
    return "نشاط حراري محتمل"


def get_fires():
    urls = [
        # جرّب VIIRS أولاً
        "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/snpp/csv/SUOMI_VIIRS_C2_Global_24h.csv",
        "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/noaa20/csv/J1_VIIRS_C2_Global_24h.csv",
        # بديل MODIS
        "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6.1/csv/MODIS_C6_1_Global_24h.csv",
    ]

    raw_points = []

    for url in urls:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200 or not r.text.strip():
                continue

            lines = r.text.splitlines()
            if len(lines) < 2:
                continue

            header = [h.strip() for h in lines[0].split(",")]

            try:
                lat_idx = header.index("latitude")
                lon_idx = header.index("longitude")
            except ValueError:
                continue

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
                    raw_points.append({
                        "lat": lat,
                        "lon": lon
                    })

        except Exception as e:
            print("fire source error:", url, e)

    if not raw_points:
        return {
            "raw_count": 0,
            "cluster_count": 0,
            "suspected_count": 0,
            "clusters": []
        }

    # تجميع النقاط المتقاربة
    clustered = {}
    for p in raw_points:
        key = (round(p["lat"], ROUND_DECIMALS), round(p["lon"], ROUND_DECIMALS))
        clustered.setdefault(key, 0)
        clustered[key] += 1

    clusters = []
    for (lat, lon), count in clustered.items():
        # قاعدة مبدئية:
        # الموقع الذي يظهر فيه أكثر من نقطة في نفس النطاق قد يكون أهم من نقطة مفردة
        suspected = count >= 2

        clusters.append({
            "lat": lat,
            "lon": lon,
            "count": count,
            "classification": classify_point(lat, lon),
            "suspected": suspected
        })

    # ترتيب تنازلي
    clusters.sort(key=lambda x: x["count"], reverse=True)

    suspected_clusters = [c for c in clusters if c["suspected"]]

    return {
        "raw_count": len(raw_points),
        "cluster_count": len(clusters),
        "suspected_count": len(suspected_clusters),
        "clusters": clusters[:10],  # أعلى 10 مواقع فقط
    }
