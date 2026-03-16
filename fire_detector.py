import requests
from baseline import BASELINE_LOCATIONS

MIN_LAT = 22
MAX_LAT = 31
MIN_LON = 47
MAX_LON = 57

ROUND_DECIMALS = 2
ANOMALY_THRESHOLD = 6


def in_gulf(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def near(lat1, lon1, lat2, lon2, th=0.12):
    return abs(lat1 - lat2) <= th and abs(lon1 - lon2) <= th


def is_baseline(lat, lon):
    for bl in BASELINE_LOCATIONS:
        if near(lat, lon, bl[0], bl[1]):
            return True
    return False


def get_fires():
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/snpp/csv/SUOMI_VIIRS_C2_Global_24h.csv"

    raw_points = []

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        lines = r.text.splitlines()
        if len(lines) < 2:
            return {
                "raw_count": 0,
                "cluster_count": 0,
                "suspected_count": 0,
                "clusters": [],
            }

        header = lines[0].split(",")
        lat_idx = header.index("latitude")
        lon_idx = header.index("longitude")

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
                raw_points.append((lat, lon))

    except Exception as e:
        print("fire error:", e)

    clusters = {}

    for lat, lon in raw_points:
        key = (round(lat, ROUND_DECIMALS), round(lon, ROUND_DECIMALS))
        clusters.setdefault(key, 0)
        clusters[key] += 1

    anomaly_clusters = []

    for (lat, lon), count in clusters.items():
        if is_baseline(lat, lon):
            continue

        if count >= ANOMALY_THRESHOLD:
            anomaly_clusters.append({
                "lat": lat,
                "lon": lon,
                "count": count
            })

    anomaly_clusters.sort(key=lambda x: x["count"], reverse=True)

    return {
        "raw_count": len(raw_points),
        "cluster_count": len(clusters),
        "suspected_count": len(anomaly_clusters),
        "clusters": anomaly_clusters[:6],
    }
