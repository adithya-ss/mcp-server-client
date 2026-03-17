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
    data = response.json()
    standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    standings_list = standings_lists[0].get("DriverStandings", []) if standings_lists else []

    result_lines = []
    for entry in standings_list:
        position    = entry.get("position", "NA")
        driver      = entry.get("Driver", {}).get("familyName", "")
        points      = entry.get("points", "0")
        constructor = entry.get("Constructors", [{}])[0].get("name", "Unregistered")
        result_lines.append(f"P{position}  {driver}  {points} pts  ({constructor})")

    return json.dumps(result_lines, indent=2)

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
    data = response.json()
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])

    result_lines = []
    for race in races:
        round_num    = race.get("round", "NA")
        race_name    = race.get("raceName", "NA")
        circuit_name = race.get("Circuit", {}).get("circuitName", "NA")
        date         = race.get("date", "NA")
        result_lines.append(f"R{round_num} : {race_name}  —  {circuit_name}  ({date})")

    return json.dumps(result_lines, indent=2)

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
    data = response.json()
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    race_data = races[0] if races else {}
    results   = race_data.get("Results", [])

    race_name = race_data.get("raceName", "NA")
    race_date = race_data.get("date", "NA")
    result_lines = [f"{race_name} {race_date}", "-" * 40]
    for entry in results:
        position       = entry.get("position", "NA")
        driver         = entry.get("Driver", {}).get("familyName", "")
        constructor    = entry.get("Constructor", {}).get("name", "Unregistered")
        time_or_status = entry.get("Time", {}).get("time", "NA") or entry.get("status", "NA")
        result_lines.append(f"P{position}  {driver}  {constructor}  {time_or_status}")

    return json.dumps(result_lines, indent=2)

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
    data = response.json()
    standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    standings = standings_lists[0].get("ConstructorStandings", []) if standings_lists else []

    result_lines = []
    for entry in standings:
        position    = entry.get("position", "NA")
        constructor = entry.get("Constructor", {}).get("name", "Unregistered")
        points      = entry.get("points", "0")
        result_lines.append(f"P{position}  {constructor}  {points} pts")
    
    return json.dumps(result_lines, indent=2)


@mcp.resource("f1://drivers/current")
def get_current_drivers() -> str:
    """
    Returns the list of current F1 drivers, including their names and nationalities.
    """
    url = f"{BASE_URL}/current/drivers.json"
    response = http_client.get(url)
    response.raise_for_status()

    data = response.json()
    drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])

    result_lines = []
    for driver in drivers:
        driver_code      = driver.get("code", "NA")
        given_name       = driver.get("givenName", "")
        family_name      = driver.get("familyName", "")
        name             = f"{given_name} {family_name}".strip()
        nationality      = driver.get("nationality", "NA")
        permanent_number = driver.get("permanentNumber", "--")
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
