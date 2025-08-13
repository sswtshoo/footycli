import json
from datetime import datetime


def todays_fixtures(headers, conn, lines_available):
    date = datetime.now().strftime("%Y%m%d")
    conn.request(
        "GET", f"/football-get-matches-by-date?date={date}", headers=headers
        )
    res = conn.getresponse()

    data = res.read()
    decoded_data = data.decode('utf-8')
    parsed_data = json.loads(decoded_data)
    fixtures = parsed_data["response"]["matches"]

    if not fixtures:
        return (0, "No fixtures for today")

    if len(fixtures) > lines_available:
        fixtures = fixtures[:lines_available - 1]

    return (1, fixtures)
