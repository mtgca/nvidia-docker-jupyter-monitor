import json
import os
import subprocess
import time
from prettytable import PrettyTable


def create_json_file():
    try:
        subprocess.run(["python", "logic.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script original: {e}")


def load_container_data(json_file):
    if not os.path.exists(json_file):
        print(f"Actualizando datos espere...")
        create_json_file()

    try:
        with open(json_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo {json_file} no se encuentra.")
        return []
    except json.JSONDecodeError:
        print(f"Error: No se pudo decodificar el JSON en {json_file}.")
        return []


def display_stats(data):
    table = PrettyTable()
    table.field_names = [
        "Container Name",
        "Port",
        "Jupyter Token",
        "CPU Usage",
        "Memory Usage",
        "Memory %",
        "Net I/O",
        "Block I/O",
        "Notebook Name",
        "PID",
        "GPU ID",
        "GPU Memory Used (MiB)",
        "Total GPUs Used (MiB)",
        "Total GPU % Used",
    ]

    for container in data:
        container_name = container["container_name"]
        port = container["port"]
        token = container["token"]
        cpu_usage = container["cpu_usage"]
        mem_usage = container["mem_usage"]
        mem_perc = container["mem_perc"]
        net_io = container["net_io"]
        block_io = container["block_io"]

        jupyter_sessions = container.get("jupyter_sessions", [])
        gpu_info = container.get("gpu_info", [])

        # Si hay notebooks en el contenedor
        if jupyter_sessions:
            for session in jupyter_sessions:

                notebook_name = session.get("notebook_name", "")[:20]

                row = [
                    container_name,
                    port,
                    token,
                    cpu_usage,
                    mem_usage,
                    mem_perc,
                    net_io,
                    block_io,
                    notebook_name,
                    session.get("pid", ""),
                    "",  # GPU ID
                    "",  # GPU Memory Used
                    "",  # Total GPUs Used
                    "",  # Total GPU %
                ]

                # Agregar información de GPU si está disponible
                for gpu in gpu_info:
                    if gpu["docker_container_running_gpu_pid"] == session["pid"]:
                        row[10] = gpu["docker_container_used_gpu_id"]
                        row[11] = gpu["docker_container_gpu_memory_used_MiB"]
                        row[12] = gpu["docker_container_total_gpu_used_MiB"]
                        row[13] = gpu["porcentaje_total_gpu_percent_ram_used"]

                table.add_row(row)

        # Si no hay notebooks en el contenedor, solo mostrar información de GPU
        elif gpu_info:
            row = [
                container_name,
                port,
                token,
                cpu_usage,
                mem_usage,
                mem_perc,
                net_io,
                block_io,
                "",  # Notebook Name
                "",  # PID
                gpu_info[0]["docker_container_used_gpu_id"],  # GPU ID
                gpu_info[0]["docker_container_gpu_memory_used_MiB"],  # GPU Memory Used
                gpu_info[0]["docker_container_total_gpu_used_MiB"],  # Total GPUs Used
                gpu_info[0]["porcentaje_total_gpu_percent_ram_used"],  # Total GPU %
            ]
            table.add_row(row)

        # Si no hay ni notebooks ni GPUs, solo mostramos la información básica del contenedor
        else:
            row = [
                container_name,
                port,
                token,
                cpu_usage,
                mem_usage,
                mem_perc,
                net_io,
                block_io,
                "-",  # No hay notebooks
                "-",  # No hay PID
                "-",  # No hay GPU ID
                "-",  # No hay GPU Memory Used
                "-",  # No hay Total GPUs Used
                "-",  # No hay GPU % Used
            ]
            table.add_row(row)

    print(table)


def main():
    try:
        os.remove("data.json")
    except OSError:
        pass
    try:
        os.system("clear")
    except:
        os.system("cls")
    json_file = "data.json"
    create_json_file()
    while True:
        data = load_container_data(json_file)
        display_stats(data)
        time.sleep(65)
        os.remove("data.json")


if __name__ == "__main__":
    main()