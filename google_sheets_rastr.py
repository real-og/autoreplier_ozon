import csv
import io
import requests
import config_io


import csv
import io
import requests
import config_io


def fetch_google_sheet_rows() -> list[list[str]]:

    url = config_io.get_value('SHEET_LINK').strip()
    if not url:
        return []
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        r.encoding = "utf-8"

        f = io.StringIO(r.text)
        rows = list(csv.reader(f))

        if not rows:
            return []

        return rows

    except requests.exceptions.RequestException as e:
        print(f"[fetch_google_sheet_rows] HTTP error: {e}")
        return []

    except Exception as e:
        print(f"[fetch_google_sheet_rows] Unexpected error: {e}")
        return []


def get_recommendations(article):
    data = fetch_google_sheet_rows()
    recommendations = []
    for row in data:
        if (len(row) > 0) and str(row[0]) == str(article):
            for item in row[1:]:
                if item:
                    recommendations.append(item)
            break
    return recommendations
