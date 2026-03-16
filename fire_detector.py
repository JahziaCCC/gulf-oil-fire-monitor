import requests

def get_fires():

    try:
        url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6.1/csv/MODIS_C6_1_Global_24h.csv"
        r = requests.get(url, timeout=20)

        lines = r.text.split("\n")

        fires = []

        for line in lines[1:]:

            parts = line.split(",")

            if len(parts) < 5:
                continue

            lat = float(parts[0])
            lon = float(parts[1])

            # نطاق الخليج
            if 22 <= lat <= 31 and 47 <= lon <= 57:

                fires.append({
                    "lat": lat,
                    "lon": lon
                })

        return fires

    except Exception as e:
        print("fire error:", e)
        return []
