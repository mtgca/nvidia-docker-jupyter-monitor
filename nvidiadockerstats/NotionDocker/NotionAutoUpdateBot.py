from datetime import datetime, timezone, timedelta
import json
from pprint import pprint
import os
from notion_client import Client
from dotenv import load_dotenv
from model import Container_info

load_dotenv(".env")
Notion_Token: str = os.getenv("Notion_Token")
Notion_Database_ID: str = os.getenv("Database_ID")
file = "tokens_de_jupyter.json"

if Notion_Token == None:
    print("Notion Token not found")
    exit(1)  # Termina el programa con código de error

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


def get_pages():
    
    data = Nclient.databases.query(Notion_Database_ID)

    results = data["results"]

    with open("db.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    return results


def Info_Database(Selected):
    print(f"Recolectando info de la database de {Selected}")
    pages = get_pages(Nclient)

    Info_db = []
    for page in pages:
        page_id = page["id"]
        props = page["properties"]
        ContainerId = props["Container ID"]["rich_text"][0]["text"]["content"]
        Host = props["Host"]["select"]["name"]
        port = props["Port Number"]["number"]
        try:
            NameC = props["Docker container"]["title"][0]["text"]["content"]
        except:
            NameC = "No name"
        try:
            tokenj = props["Token"]["rich_text"][0]["text"]["content"]
        except:
            tokenj = "No token"
        Info_db.append(
            {
                "page_id": page_id,
                "Container_ID": ContainerId,
                "Name_Container": NameC,
                "Port": port,
                "Token_J": tokenj,
                "Host": Host,
            }
        )
    pprint(Info_db)
    return Info_db

def update_page(page_id: str, data: dict):
    response = Nclient.pages.update(page_id=page_id, properties=data)
    return response

def token_update(token, page_id):
    tokenupdate = {
        "Token": {"rich_text": [{"text": {"content":token}}]}
    }
    update_page(page_id, tokenupdate)

def port_update(port: int, page_id):
    portUpdate = {
        "Port Number": {"number": port}
    }
    update_page(page_id, portUpdate)

def delete_page(page_id):
    return Nclient.pages.update(page_id=page_id, archived=True)

def search_page(container_name, Host):
    payload = {
        "and": [
            {
                "property": "Docker container",  # Asegúrate que el nombre coincide con tu base de datos
                "title": {
                    "contains": container_name
                }
            },
            {
                "property": "Host",
                "select": {
                    "equals": Host
                }
            }
        ]
    }
    page = Nclient.databases.query(database_id=Notion_Database_ID, filter=payload)
    results = page.get("results", [])
    if results:
        return results[0]["id"]
    else:
        return []

def create_page(data: Container_info):
    parent = {
        "database_id": Notion_Database_ID
    }
    properties = {
        "Container ID": {
            "rich_text": [
                {
                    "text": {
                        "content": data.Container_ID
                    }
                }
            ]
        },
        "Host": {
            "select": {
                "name": data.Host
            }
        },
        "Port Number": {
            "number": data.Port
        },
        "Token": {
            "rich_text": [
                {
                    "text": {
                        "content": data.Token_J
                    }
                }
            ]
        },
        "Docker container": {
            "title": [
                {
                    "text": {
                        "content": data.Name_Container
                    }
                }
            ]
        }
    }
    return Nclient.pages.create(parent=parent, properties=properties)


def main():
    id = search_page("updated", "DGX")
    port_update(727, id)


if __name__ == "__main__":
    main()
    print(todayEc)