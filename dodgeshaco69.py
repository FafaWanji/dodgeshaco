import json
import os
from plyer import notification
from lcu_driver import Connector

connector = Connector()

# List of champions to dodge
dodge_list = [35, 84]  # Shaco, Akali

# List of champions and their counters
counter_map = {
     55: "Yasuo",           # Katarina
    517: "Heimerdinger",    # Sylas
    245: "Kassadin",        # Ekko
    122: "Yorick"           # Darius 
}

os.chdir("D:\Scripts\dodgeshaco")  # Replace "D:.." with the actual path where your script is located

your_summoner_id = 0
last_game_id = 0

# This function gets called when the LCU API is ready to be used
@connector.ready
async def connect(connection):
    summoner = await connection.request("get", "/lol-summoner/v1/current-summoner")
    if summoner.status != 200:
        print("failed at summoner data request")
        return

    result = json.loads(await summoner.read())

    global your_summoner_id
    your_summoner_id = result["summonerId"]

    notification.notify(
        title="dodgeshaco", 
        message=f"Hey {result['displayName']}. The script is ready.", 
        timeout=5
    )

# This function gets called when the LCU client has been closed
@connector.close
async def disconnect(_):
    print("The client has been closed!")

# This function gets called when the session state has changed
@connector.ws.register("/lol-champ-select/v1/session", event_types=("UPDATE",))
async def champ_select(connection, _):
    data = await connection.request("get", "/lol-champ-select/v1/session")
    if data.status != 200:
        print("failed at champ select request")
        return

    result = json.loads(await data.read())

    global last_game_id
    if result["gameId"] != last_game_id:
        last_game_id = result["gameId"]
        searchBanByPosition(result)

    global your_summoner_id

    if result["actions"] is not None:
        a = result["actions"]
        for b in a:
            for c in b:
                if (
                    c["type"] == "pick"
                    and not c["isAllyAction"]
                    and not c["isInProgress"]
                ):
                    champId = c["championId"]

                    if champId in dodge_list:
                        notification.notify(
                            title="ALARM!", 
                            message="Dodge!", 
                            timeout=30
                        )

                    if counter_map.get(champId, None) is not None:
                        notification.notify(
                            title="Pick "+counter_map[champId], 
                            message="or dodge", 
                            timeout=30
                        )

# This function gets called to check the ban by position
def searchBanByPosition(result):
    for ich in result["myTeam"]:
        if ich["summonerId"] == your_summoner_id:
            if ich["assignedPosition"] == "middle":
                notification.notify(
                    title="Bann Akali", 
                    message="Bann Akali", 
                    timeout=5
                )
            elif ich["assignedPosition"] == "top":
                notification.notify(
                    title="Bann Darius", 
                    message="Bann Darius", 
                    timeout=5
                )
            elif ich["assignedPosition"] == "jungle":
                notification.notify(
                    title="Bann Shaco", 
                    message="Bann Shaco", 
                    timeout=5
                )
            else:
                notification.notify(
                    title="Bann Kaisa", 
                    message="Bann Kaisa", 
                    timeout=5
                )



connector.start()

