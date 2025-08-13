from dotenv import load_dotenv
import os
import http.client
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Static, TabbedContent, TabPane
from textual.screen import Screen
from textual.containers import HorizontalGroup
from textual.widgets.option_list import Option
from footydata import Data



load_dotenv()
api_key = os.environ.get("API_KEY")
conn = http.client.HTTPSConnection("v3.football.api-sports.io")
headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': api_key
    }

footydata = Data(headers, conn)
live_data = footydata.get_live_matches()
fixtures_data = footydata.get_fixtures()

class LiveMatches(OptionList):
    can_focus = True

    def on_mount(self) -> None:
        self.next_match()
        self.set_interval(60, self.next_match)

    def next_match(self) -> None:
        global live_data
        live_data = footydata.get_live_matches()
        self.clear_options()
        if live_data[0] == 0:
            self.add_option(Option(live_data[1], id="none"))
        else:
            matches = live_data[1]
            for match in matches:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
                home_score = match["goals"]["home"]
                away_score = match["goals"]["away"]
                match_id = match["fixture"]["id"]
                match_text = f"{home} {home_score}-{away_score} {away}"
                self.add_option(Option(match_text, id=int(match_id)))


class LiveMatchLineups(Static):

    def on_mount(self) -> None:
        pass

    def center_line(self, players):
        if not players:
            return ""
        line = "        ".join(players)

        from shutil import get_terminal_size
        term_width = get_terminal_size((80, 20)).columns
        return line.center(term_width)

    def update_lineups(self, match_id) -> None:
        success, data = footydata.get_lineup_data(match_id)
        if not success:
            self.update(data)
            return

        output = ""
        for lineup in data:
            team_name = lineup["team"]["name"]
            formation = lineup.get("formation", "")
            output += f"[b]{team_name}[/b] ({formation})\n\n"


            players_by_pos = {"G": [], "D": [], "M": [], "F": []}
            for player in lineup["startXI"]:
                pos = player["player"]["pos"]
                name = player["player"]["name"]
                players_by_pos[pos].append(name)


            if formation:
                try:
                    shape = list(map(int, formation.split("-")))
                except ValueError:
                    shape = [len(players_by_pos["D"]), len(players_by_pos["M"]), len(players_by_pos["F"])]
            else:
                shape = [len(players_by_pos["D"]), len(players_by_pos["M"]), len(players_by_pos["F"])]


            lines = [
                self.center_line(players_by_pos["F"]),
                self.center_line(players_by_pos["M"]),
                self.center_line(players_by_pos["D"]),
                self.center_line(players_by_pos["G"])
            ]

            output += "\n\n".join(line for line in lines if line)
            output += "\n\n"

        self.update(output)

class LiveMatchStats(Static):
    def on_mount(self) -> None:
        self.set_interval(60, self.refresh_stats)

    def refresh_stats(self) -> None:
        self.update_stats(self.match_id)

    def update_stats(self, match_id: str) -> None:
        self.match_id = match_id
        success, fixture_data = footydata.get_live_stats(match_id)
        if not success or "statistics" not in fixture_data or not fixture_data["statistics"]:
            self.update("Stats not available for this match.")
            return

        stats_output = ""
        for team_stats in fixture_data["statistics"]:
            stats_output += f"[b]{team_stats['team']['name']}[/b]\n"
            for stat in team_stats["statistics"]:
                stats_output += f"- {stat['type']}: {stat['value']}\n"
            stats_output += "\n"
        self.update(stats_output)

class LiveMatchStatsScreen(Screen):

    def __init__(self, match_id: str):
        super().__init__()
        self.match_id = match_id

    def compose(self) -> ComposeResult:
        with TabbedContent("Stats", "Lineups"):
            with TabPane("Stats", id="tab_stats"):
                yield LiveMatchStats()
            with TabPane("Lineups", id="tab_lineups"):
                yield LiveMatchLineups()

    def on_mount(self) -> None:
        stats_widget = self.query_one(LiveMatchStats)
        stats_widget.update_stats(self.match_id)
        lineups_widget = self.query_one(LiveMatchLineups)
        lineups_widget.update_lineups(self.match_id)

class Fixtures(OptionList):
    can_focus = True
    def on_mount(self) -> None:
        self.next_fixture()

    def next_fixture(self) -> None:
        if fixtures_data[0] == 0:
            self.add_option(Option(fixtures_data[1], id="none"))
        else:
            fixture_list = fixtures_data[1]
            for fixture in fixture_list:
                home = fixture["teams"]["home"]["name"]
                away = fixture["teams"]["away"]["name"]
                self.add_option(Option(f"{home} - {away}", id=fixture["fixture"]["id"]))

class FootyCli(App):
    BINDINGS = [("q", "quit", "Quit"), ("escape", "dismiss", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield HorizontalGroup(LiveMatches(), Fixtures())
    
    def action_quit_app(self) -> None:
        self.action_quit()
    
    def on_option_list_option_selected(self, event):
        self.bell()
        if isinstance(event.option_list, LiveMatches):
            match_id = event.option.id
            self.push_screen(LiveMatchStatsScreen(match_id))
            
        elif isinstance(event.option_list, Fixtures):
            self.notify("Fixture selected!")
    
    def action_dismiss(self) -> None:
        self.app.pop_screen()

if __name__ == "__main__":
    app = FootyCli()
    app.run()
