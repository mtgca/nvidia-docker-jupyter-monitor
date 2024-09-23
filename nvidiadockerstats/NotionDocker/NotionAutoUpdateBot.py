import requests
from datetime import datetime, timezone, timedelta
import json
from pprint import pprint
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
        try:
            NameC = props["Docker container"]["title"][0]["text"]["content"]
        except:
            NameC = "No name"
        port = props["Port Number"]["number"]
        try:
            tokenj = props["Token"]["rich_text"][0]["text"]["content"]
        except:
            tokenj = "No token"
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


def check_for_tokenUpdates(page_id, file, ContainerId, token, port, GpuUse):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            if item["container_id"] == ContainerId:
                if item["token"] == token and int(item["port"]) == port:
                    try:
                        cpuupdate = {
                            "CPU Usage": {
                                "number": float(item["cpu_usage"].replace("%", ""))
                            }
                        }
                        memupdate = {
                            "Memory Usage": {
                                "rich_text": [{"text": {"content": item["mem_usage"]}}]
                            }
                        }
                        mempercupdate = {
                            "Memory Usage Percent": {
                                "number": float(item["mem_perc"].replace("%", ""))
                            }
                        }
                        netioupdate = {
                            "Network I/O": {
                                "rich_text": [{"text": {"content": item["net_io"]}}]
                            }
                        }
                        blockioupdate = {
                            "Block I/O": {
                                "rich_text": [{"text": {"content": item["block_io"]}}]
                            }
                        }
                    except:
                        cpuupdate = {"CPU Usage": {"number": 0}}
                        memupdate = {
                            "Memory Usage": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                        mempercupdate = {"Memory Usage Percent": {"number": 0}}
                        netioupdate = {
                            "Network I/O": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                        blockioupdate = {
                            "Block I/O": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                    update_page(page_id, cpuupdate)
                    update_page(page_id, memupdate)
                    update_page(page_id, mempercupdate)
                    update_page(page_id, netioupdate)
                    update_page(page_id, blockioupdate)
                    for gpu in GpuUse:
                        if gpu["container_id"] == ContainerId:
                            gpuupdate = {
                                "GPU Usage": {
                                    "number": float(gpu["total_gpu_used_MiB"])
                                }
                            }
                            gpupercupdate = {
                                "GPU Percent": {
                                    "number": float(gpu["total_gpu_percent"])
                                }
                            }
                            update_page(page_id, gpuupdate)
                            update_page(page_id, gpupercupdate)
                    return True
                else:
                    nameupdate = {
                        "Docker container": {
                            "title": [{"text": {"content": item["container_name"]}}]
                        }
                    }
                    portupdate = {"Port Number": {"number": int(item["port"])}}
                    tokenupdate = {
                        "Token": {"rich_text": [{"text": {"content": item["token"]}}]}
                    }
                    Update_check = {"Portforwarding": {"checkbox": True}}
                    try:
                        cpuupdate = {
                            "CPU Usage": {
                                "number": float(item["cpu_usage"].replace("%", ""))
                            }
                        }
                        memupdate = {
                            "Memory Usage": {
                                "rich_text": [{"text": {"content": item["mem_usage"]}}]
                            }
                        }
                        mempercupdate = {
                            "Memory Usage Percent": {
                                "number": float(item["mem_perc"].replace("%", ""))
                            }
                        }
                        netioupdate = {
                            "Network I/O": {
                                "rich_text": [{"text": {"content": item["net_io"]}}]
                            }
                        }
                        blockioupdate = {
                            "Block I/O": {
                                "rich_text": [{"text": {"content": item["block_io"]}}]
                            }
                        }
                    except:
                        cpuupdate = {"CPU Usage": {"number": 0}}
                        memupdate = {
                            "Memory Usage": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                        mempercupdate = {"Memory Usage Percent": {"number": 0}}
                        netioupdate = {
                            "Network I/O": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                        blockioupdate = {
                            "Block I/O": {
                                "rich_text": [{"text": {"content": "unknown"}}]
                            }
                        }
                    update_page(page_id, nameupdate)
                    update_page(page_id, portupdate)
                    update_page(page_id, tokenupdate)
                    update_page(page_id, Update_check)
                    update_page(page_id, cpuupdate)
                    update_page(page_id, memupdate)
                    update_page(page_id, mempercupdate)
                    update_page(page_id, netioupdate)
                    update_page(page_id, blockioupdate)
                    for gpu in GpuUse:
                        if gpu["container_id"] == ContainerId:
                            gpuupdate = {
                                "GPU Usage": {
                                    "number": float(gpu["total_gpu_used_MiB"])
                                }
                            }
                            gpupercupdate = {
                                "GPU Percent": {
                                    "number": float(gpu["total_gpu_percent"])
                                }
                            }
                            update_page(page_id, gpuupdate)
                            update_page(page_id, gpupercupdate)
                    return True
            else:
                continue
    return False


def calcular_consumo_gpu_unico(file):
    with open(file) as f:
        data = json.load(f)
    resultados = []
    for contenedor in data:
        container_id = contenedor["container_id"]
        container_name = contenedor["container_name"]
        procesos_vistos = set()
        total_gpu_used_MiB = 0
        total_gpu_percent = 0.0
        for gpu in contenedor["gpu_info"]:
            pid = gpu["docker_container_running_gpu_pid"]
            gpu_memory_used = int(gpu["docker_container_total_gpu_used_MiB"])
            clave_unica = (pid, gpu_memory_used)
            if clave_unica not in procesos_vistos:
                procesos_vistos.add(clave_unica)
                total_gpu_used_MiB += gpu_memory_used
        for gpu in contenedor["gpu_info"]:
            pid = gpu["docker_container_running_gpu_pid"]
            gpu_percent_used = round(
                float(gpu["porcentaje_total_gpu_percent_ram_used"]), 4
            )
            clave_unica = (pid, gpu_memory_used)
            if clave_unica not in procesos_vistos:
                procesos_vistos.add(clave_unica)
                total_gpu_percent += gpu_percent_used
        resultados.append(
            {
                "container_id": container_id,
                "container_name": container_name,
                "total_gpu_used_MiB": total_gpu_used_MiB,
                "total_gpu_percent": total_gpu_percent,
            }
        )

    return resultados


def main():
    Datalist = Info_Database(Notion_Database_ID, "Notion")
    GpuUse = calcular_consumo_gpu_unico(file)
    for Data in Datalist:
        ContainerID = Data["Container_ID"]
        port = Data["Number"]
        token = Data["Token_J"]
        page_id = Data["page_id"]
        if check_for_tokenUpdates(page_id, file, ContainerID, token, port, GpuUse):
            print(f"Container {ContainerID} updated")
        else:
            print(f"Container {ContainerID} no need of update")
    os.remove(file)


if __name__ == "__main__":
    main()
    print(todayEc)
