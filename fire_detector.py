import requests

GULF_BBOX = [22,47,31,57]  # الخليج

def get_fires():

    url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

    try:
        r = requests.get(url)
        data = r.text

        fires = []

        for line in data.split("\n")[1:]:
            parts = line.split(",")

            if len(parts) < 10:
                continue

            lat = float(parts[0])
            lon = float(parts[1])
            confidence = parts[9]

            if 22 < lat < 31 and 47 < lon < 57:

                fires.append({
                    "lat": lat,
                    "lon": lon,
                    "confidence": confidence
                })

        return fires

    except:
        return []
