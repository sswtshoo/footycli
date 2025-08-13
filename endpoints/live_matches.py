import json

def live_matches(headers, conn, lines_available):

    conn.request("GET", "/football-current-live", headers=headers)
    res = conn.getresponse()
    data = res.read()

    decoded_data = data.decode('utf-8')
    parsed_data = json.loads(decoded_data)
    all_live_matches = parsed_data["response"]["live"]

    if len(all_live_matches) < lines_available:
        all_live_matches = all_live_matches[:lines_available - 3]

    if not all_live_matches:
        return (0, "No matches being played at this moment.")
    
    else:
        return (1, all_live_matches)