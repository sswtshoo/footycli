import http.client
from datetime import datetime
import json

class Data():
    def __init__(self, headers: dict[str, str], conn: http.client.HTTPSConnection):
        self.headers = headers
        self.conn = conn

    def __make_request(self, endpoint: str):
        self.conn.request("GET", endpoint, headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        decoded_data = data.decode('utf-8')
        parsed_data = json.loads(decoded_data)
        return parsed_data
    
    def get_fixtures(self):
        date = datetime.now().strftime("%Y-%m-%d")
        data = self.__make_request(f"/fixtures?date={date}")
        fixtures = data["response"]
        if not fixtures:
            return 0, "No fixtures for today"
        return 1, fixtures
    
    def get_live_matches(self):
        data = self.__make_request("/fixtures?live=all")
        live_matches = data["response"]
        if not live_matches:
            return 0, "No matches being played at this moment."
        return 1, live_matches
    
    def get_live_stats(self, id):
        data = self.__make_request(f"/fixtures?id={id}")
        if data.get("response"):
            return 1, data["response"][0]
        return 0, "Fixture details not found."
    
    def get_lineup_data(self, id):
        data = self.__make_request(f"/fixtures/lineups?fixture={id}")
        if data.get("response"):
            return 1, data["response"]
        return 0, "No lineup data available for this match."
        # return 1, data