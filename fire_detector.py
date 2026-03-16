import requests

MIN_LAT = 22
MAX_LAT = 31
MIN_LON = 47
MAX_LON = 57

ROUND_DECIMALS = 2

# مواقع مشاعل معروفة تقريبياً (يمكن تطويرها لاحقاً)
KNOWN_FLARES = [
    (27.72, 52.18),
    (27.71, 52.19),
    (27.50, 52.64),
    (27.51, 52.63),
    (27.51, 52.62),
]


def in_gulf(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON


def is_flare(lat, lon):

    for f in KNOWN_FLARES:
        if abs(lat - f[0]) < 0.1 and abs(lon - f[1]) < 0.1:
            return True

    return False


def get_fires():

    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/snpp/csv/SUOMI_VIIRS_C2_Global_24h.csv"

    raw_points = []

    try:

        r = requests.get(url, timeout=30)
        lines = r.text.splitlines()

        header = lines[0].split(",")

        lat_idx = header.index("latitude")
        lon_idx = header.index("longitude")

        for line in lines[1:]:

            parts = line.split(",")

            if len(parts) <= max(lat_idx, lon_idx):
                continue

            lat = float(parts[lat_idx])
            lon = float(parts[lon_idx])

            if in_gulf(lat, lon):

                if not is_flare(lat, lon):

                    raw_points.append({
                        "lat": lat,
                        "lon": lon
                    })

    except Exception as e:
        print(e)

    clustered = {}

    for p in raw_points:

        key = (round(p["lat"], ROUND_DECIMALS), round(p["lon"], ROUND_DECIMALS))

        clustered.setdefault(key, 0)
        clustered[key] += 1

    clusters = []

    for (lat, lon), count in clustered.items():

        if count >= 3:

            clusters.append({
                "lat": lat,
                "lon": lon,
                "count": count
            })

    clusters.sort(key=lambda x: x["count"], reverse=True)

    return {
        "raw_count": len(raw_points),
        "cluster_count": len(clustered),
        "suspected_count": len(clusters),
        "clusters": clusters[:10],
    }
