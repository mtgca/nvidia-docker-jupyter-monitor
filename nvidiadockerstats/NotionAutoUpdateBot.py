import requests
from datetime import datetime, timezone, timedelta
import json
from pprint import pprint
from pprint import pformat
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv(".env")
Notion_Token: str = os.getenv("Notion_Token")
Notion_Database_ID: str = os.getenv("Database_ID")
file = "tokens_de_jupyter.json"


headers = {
    "Authorization": "Bearer " + Notion_Token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

Nclient = Client(auth=Notion_Token)
today = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
today_utc = datetime.now(timezone.utc)
ec_hrs = -5
ec_h = timedelta(hours=ec_hrs)
current_time_ec = today_utc + ec_h
todayEc = current_time_ec.strftime("%Y-%m-%d %H:%M")


def get_pages(Notion_Database_ID, num_pages=None):
    url = f"https://api.notion.com/v1/databases/{Notion_Database_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, headers=headers, json=payload)

    data = response.json()

    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]

    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results.extend(data["results"])
    os.remove("db.json")
    return results


def Info_Database(Notion_Database_ID, Selected):
    print(f"Recolectando info de la database de {Selected}")
    pages = get_pages(Notion_Database_ID)

    Info_db = []
    for page in pages:
        page_id = page["id"]
        props = page["properties"]
        ContainerId = props["Container ID"]["rich_text"][0]["text"]["content"]
        NameC = props["Docker container"]["title"][0]["text"]["content"]
        port = props["Port Number"]["number"]
        tokenj = props["Token"]["rich_text"][0]["text"]["content"]
        Info_db.append(
            {
                "page_id": page_id,
                "Container_ID": ContainerId,
                "Name_Container": NameC,
                "Number": port,
                "Token_J": tokenj,
            }
        )
    pprint(Info_db)
    return Info_db


def update_page(page_id: str, data: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": data}
    response = requests.patch(url, headers=headers, json=payload)
    print(response.status_code)
    return response


def check_for_tokenUpdates(page_id, file, ContainerId, token, port):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            if item["Container_ID"] == ContainerId:
                if item["token"] == token or item["port"] == port:
                    return False
                else:
                    portupdate = {"Port Number": {"number": f"{item['port']}"}}
                    tokenupdate = {
                        "Token": {
                            "rich_text": [{"text": {"content": f"{item['token'][0]}"}}]
                        }
                    }
                    cpuupdate = {"CPU Usage": {"number": f"{item['cpu_usage']}"}}
                    memupdate = {
                        "Memory Usage": {"text": {"content": f"{item['mem_usage']}"}}
                    }
                    mempercupdate = {
                        "Memory Usage Percent": {"number": f"{item['mem_perc']}"}
                    }
                    netioupdate = {
                        "Network I/O": {"text": {"content": f"{item['net_io']}"}}
                    }
                    blockioupdate = {
                        "Block I/O": {"text": {"content": f"{item['block_io']}"}}
                    }
                    pidsupdate = {"PIDs": {"number": f"{item['pids']}"}}
                    update_page(page_id, portupdate)
                    update_page(page_id, tokenupdate)
                    update_page(page_id, cpuupdate)
                    update_page(page_id, memupdate)
                    update_page(page_id, mempercupdate)
                    update_page(page_id, netioupdate)
                    update_page(page_id, blockioupdate)
                    update_page(page_id, pidsupdate)
                    return True
            else:
                return False


def main():
    Datalist = Info_Database(Notion_Database_ID, "Notion")
    for Data in Datalist:
        ContainerID = Data["Container_ID"]
        port = Data["Number"]
        token = Data["Token_J"]
        page_id = Data["page_id"]
        if check_for_tokenUpdates(page_id, file, ContainerID, token, port):
            print(f"Container {ContainerID} updated")
        else:
            print(f"Container {ContainerID} no need of update")
    os.remove(file)


if __name__ == "__main__":
    main()
    print(todayEc)
