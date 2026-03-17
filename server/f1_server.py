import httpx
import json
from mcp.server.fastmcp import FastMCP


BASE_URL = "https://api.jolpi.ca/ergast/f1"

# verify=False works around corporate proxy SSL certificate issues.
# The Jolpica API is a read-only public endpoint so there is no security risk here.
http_client = httpx.Client(verify="C:\\Users\\320262498\\Downloads\\ciscoumbrellaroot.pem")

mcp = FastMCP("f1-server")


@mcp.tool()
def get_driver_standings(season: int) -> str:
    """
    Returns the Formula 1 World Drivers Championship standings for the given
    season year. Use this when asked about championship points, rankings, or
    who won a specific season.

    Args:
        season: Four-digit year, e.g. 2024.
    """
    url = f"{BASE_URL}/{season}/driverStandings.json"
    response = http_client.get(url)
    response.raise_for_status()

    # The response structure is:
    #     ["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    # Each entry has keys: "position", "points", "Driver" (a dict with "familyName"), "Constructors"
    standings_list = response.json()["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

    result_lines = []
    for entry in standings_list:
        position   = entry["position"]
        driver     = entry["Driver"]["familyName"]
        points     = entry["points"]
        constructor = entry["Constructors"][0]["name"]
        result_lines.append(f"P{position}  {driver}  {points} pts  ({constructor})")

    return "\n".join(result_lines)

@mcp.tool()
def get_race_schedule(season: int) -> str:
    """
    Returns the full Formula 1 race calendar for the given season, including
    round numbers, race names, circuits, and dates. Use this when asked about
    upcoming races, the season calendar, or which round a race is.

    Args:
        season: Four-digit year, e.g. 2024.
    """
    url = f"{BASE_URL}/{season}.json"
    response = http_client.get(url)
    response.raise_for_status()

    # The response structure is:
    #     ["MRData"]["RaceTable"]["Races"]
    # Each race entry has: "round", "raceName", "Circuit" (dict with "circuitName"), "date", "time"
    races = response.json()["MRData"]["RaceTable"]["Races"]

    result_lines = []
    for race in races:
        round_num    = race["round"]
        race_name    = race["raceName"]
        circuit_name = race["Circuit"]["circuitName"]
        date         = race["date"]
        result_lines.append(f"R{round_num:02d} : {race_name}  —  {circuit_name}  ({date})")

    return "\n".join(result_lines)

@mcp.tool()
def get_race_result(season: int, round: int) -> str:
    """
    Returns the finishing order and fastest-lap times for a specific race
    identified by season and round number. Use this when asked about who won
    a particular Grand Prix or the finishing order of a specific race.

    Args:
        season: Four-digit year, e.g. 2024.
        round:  Round number within the season, e.g. 1 for the opening race.
    """
    url = f"{BASE_URL}/{season}/{round}/results.json"
    response = http_client.get(url)
    response.raise_for_status()

    # The response structure is:
    #     ["MRData"]["RaceTable"]["Races"][0]
    # The race dict has: "raceName", "date"
    # The results list is at: race["Results"]
    # Each result entry has: "position", "Driver" (dict), "Constructor" (dict), "Time" (dict with "time"), "status"
    race_data = response.json()["MRData"]["RaceTable"]["Races"][0]
    results   = race_data["Results"]

    result_lines = [f'{race_data["raceName"]} {race_data["date"]}', "-" * 40]
    for entry in results:
        position    = entry["position"]
        driver      = entry["Driver"]["familyName"]
        constructor = entry["Constructor"]["name"]
        time_or_status = entry.get("Time", {}).get("time") or entry["status"]
        result_lines.append(f"P{position}  {driver}  {constructor}  {time_or_status}")

    return "\n".join(result_lines)

@mcp.tool()
def get_constructor_standings(season: int) -> str:
    """
    Returns the constructor standings for a specific season, including
    positions, constructor names, and points. Use this when asked about
    the current or historical constructor standings.

    Args:
        season: Four-digit year, e.g. 2024.
    """
    url = f"{BASE_URL}/{season}/constructorStandings.json"
    response = http_client.get(url)
    response.raise_for_status()

    # The response structure is:
    #     ["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    # Each entry has keys: "position", "points", "Constructor" (dict with "name")
    standings = response.json()["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    result_lines = []
    for entry in standings:
        position    = entry["position"]
        constructor = entry["Constructor"]["name"]
        points      = entry["points"]
        result_lines.append(f"P{position}  {constructor}  {points} pts")
    
    return "\n".join(result_lines)


@mcp.resource("f1://drivers/current")
def get_current_drivers() -> str:
    """
    Returns the list of current F1 drivers, including their names and nationalities.
    """
    url = f"{BASE_URL}/current/drivers.json"
    response = http_client.get(url)
    response.raise_for_status()

    drivers = response.json()["MRData"]["DriverTable"]["Drivers"]
    result_lines = []
    for driver in drivers:
        driver_code = driver["code"]
        name = f"{driver['givenName']} {driver['familyName']}"
        nationality = driver["nationality"]
        permanent_number = driver.get("permanentNumber", "NA")
        result_lines.append(f"{driver_code} : {name} ({nationality}) | #{permanent_number}")

    return json.dumps(result_lines, indent=2)


@mcp.prompt()
def analyze_driver(driver_name: str) -> str:
    """
    Analyzes the career of a specific F1 driver, including their championship wins,
    race victories, podium finishes, and other notable achievements.

    Args:
        driver_name: The full name of the driver, e.g. "Leclerc".
    """
    return (
        f"Analyse the F1 career of {driver_name}. Cover: championship wins, race victories, "
        f"notable seasons, and current season performance. Structure the response with clear sections."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
