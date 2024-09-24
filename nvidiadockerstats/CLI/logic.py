import json
import subprocess
import re
import requests
from concurrent.futures import ThreadPoolExecutor


def get_container_names(prefix):
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={prefix}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error getting container names: {e}")
        return []


def get_container_stats(container_name):
    try:
        result = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}",
                container_name,
            ],
            capture_output=True,
            text=True,
        )
        stats = result.stdout.strip().split(",")
        if len(stats) == 5:
            return stats
        else:
            return ["Unknown CPU", "Unknown MEM USAGE / LIMIT", "Unknown MEM %", "Unknown NET I/O", "Unknown BLOCK I/O"]
    except subprocess.CalledProcessError as e:
        print(f"Error getting stats for container {container_name}: {e}")
        return ["Unknown CPU", "Unknown MEM USAGE / LIMIT", "Unknown MEM %", "Unknown NET I/O", "Unknown BLOCK I/O"]


def get_container_id(container_name):
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.ID}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting container ID for {container_name}: {e}")
        return None


def get_jupyter_tokens(container_name):
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "jupyter", "notebook", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        token_pattern = re.compile(r"token=([a-f0-9]+)")
        for line in result.stdout.splitlines():
            if "http" in line:
                match = token_pattern.search(line)
                if match:
                    return match.group(1)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting Jupyter token from {container_name}: {e}")
        return None


def get_container_ports(container_name):
    try:
        result = subprocess.run(
            ["docker", "port", container_name],
            capture_output=True,
            text=True,
            check=True,
        )
        port_mapping = result.stdout.strip()

        ports = []
        for line in port_mapping.splitlines():
            parts = line.split(":")
            if len(parts) == 2:
                ports.append(parts[1])

        if ports:
            return ports[0]
        else:
            return "Unknown port"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving ports from container {container_name}: {e}")
        return "Unknown port"


def get_pid_for_kernel(kernel_id):
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if kernel_id in line:
                pid = line.split()[1]
                return pid
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving process list: {e}")
        return None


def get_jupyter_sessions(server_url, token):
    try:
        session_list = requests.get(
            f"{server_url}/api/sessions", headers={"Authorization": f"token {token}"}
        ).json()
        return session_list
    except Exception as e:
        print(f"Error retrieving Jupyter sessions: {e}")
        return []


def get_gpu_usage():
    try:
        result = subprocess.run(
            ["./p2g.sh"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing p2g.sh: {e}")
        return ""


def get_total_gpu_memory():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True,
        )
        memory_lines = result.stdout.strip().split("\n")
        total_memory = sum(int(memory) for memory in memory_lines)
        return total_memory
    except subprocess.CalledProcessError as e:
        print(f"Error getting total GPU memory: {e}")
        return None


def split_list(lst, chunk_size):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def parse_gpu_data(gpu_data, total_gpu_memory):
    containers = []
    container_info_blocks = gpu_data.strip().split("\n\n\n")

    for container_info in container_info_blocks:
        lines = container_info.splitlines()
        if len(lines) < 2 or "PID:" not in container_info:
            continue

        try:
            container_pid = lines[0].split(": ")[1].strip()
            container_name = lines[1].split(": ")[1].strip()

            gpu_util_line = next((line for line in lines if "GPU util" in line), None)
            gpu_usage_line = next((line for line in lines if "GPU usage" in line), None)

            gpu_util_parts = (
                gpu_util_line.split(": ")[1].split() if gpu_util_line else []
            )
            gpu_usage_parts = (
                gpu_usage_line.split(": ")[1].split() if gpu_usage_line else []
            )

            container_gpu_util = (
                split_list(gpu_util_parts, 4)
                if gpu_util_parts and len(gpu_util_parts) % 4 == 0
                else [gpu_util_parts]
            )
            container_gpu_usage = (
                split_list(gpu_usage_parts, 2)
                if gpu_usage_parts and len(gpu_usage_parts) % 2 == 0
                else [gpu_usage_parts]
            )

            total_gpu_memory_used = sum(
                int(usage[0])
                for usage in container_gpu_usage
                if usage and len(usage) > 0 and usage[0].isdigit()
            )
            percentage_memory_used = (
                (total_gpu_memory_used / total_gpu_memory) * 100
                if total_gpu_memory > 0
                else 0
            )

            for util, usage in zip(container_gpu_util, container_gpu_usage):
                gpu_id = util[0] if len(util) > 0 else "Unknown"
                gpu_pid = util[1] if len(util) > 1 else "Unknown"
                gpu_sm_util = util[2] if len(util) > 2 else "-"
                gpu_mem_util = util[3] if len(util) > 3 else "-"
                gpu_memory_used = usage[0] if len(usage) > 0 else "0"

                metrics_results = {
                    "docker_container_running_gpu_pid": container_pid,
                    "docker_container_name": container_name,
                    "docker_container_used_gpu_id": gpu_id,
                    "docker_container_utilization_gpu_percent_sm": gpu_sm_util,
                    "docker_container_gpu_memory_used_MiB": gpu_memory_used,
                    "docker_container_total_gpus_used": len(container_gpu_util),
                    "docker_container_total_gpu_used_MiB": total_gpu_memory_used,
                    "porcentaje_total_gpu_percent_ram_used": percentage_memory_used,
                }
                containers.append(metrics_results)

        except Exception as e:
            print(f"Error parsing GPU data for container: {container_info}")
            print(f"Exception: {e}")

    return containers


def main():
    prefix = "colab"  # Optional add here the Prefix of the container names to retrieve
    containers = get_container_names(prefix)
    total_gpu_memory = get_total_gpu_memory()
    gpu_data = parse_gpu_data(get_gpu_usage(), total_gpu_memory)

    data = []

    # Usamos ThreadPoolExecutor para paralelizar las llamadas de stats, IDs, tokens, puertos
    with ThreadPoolExecutor() as executor:
        futures = []
        for container in containers:
            futures.append(
                executor.submit(
                    process_container, container, gpu_data, total_gpu_memory
                )
            )

        for future in futures:
            container_data = future.result()
            data.append(container_data)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)


def process_container(container, gpu_data, total_gpu_memory):
    container_id = get_container_id(container)
    tokens = get_jupyter_tokens(container)
    port = get_container_ports(container)
    cpu_usage, mem_usage, mem_perc, net_io, block_io = get_container_stats(container)

    container_data = {
        "container_id": container_id,
        "container_name": container,
        "port": port,
        "token": tokens,
        "cpu_usage": cpu_usage,
        "mem_usage": mem_usage,
        "mem_perc": mem_perc,
        "net_io": net_io,
        "block_io": block_io,
        "jupyter_sessions": [],
        "gpu_info": [],
    }

    if tokens:
        server_url = f"http://127.0.0.1:{port}"
        jupyter_sessions = get_jupyter_sessions(server_url, tokens)
        for session in jupyter_sessions:
            kernel_id = session["kernel"]["id"]
            notebook_name = session["notebook"]["name"]
            pid = get_pid_for_kernel(kernel_id)

            session_data = {
                "notebook_name": notebook_name,
                "kernel_id": kernel_id,
                "pid": pid,
            }

            container_data["jupyter_sessions"].append(session_data)

            # Asignar la GPU correspondiente al PID del kernel
            for gpu_info in gpu_data:
                if gpu_info["docker_container_running_gpu_pid"] == pid:
                    container_data["gpu_info"].append(gpu_info)

    # Añadir la información de GPU aunque no haya notebooks mapeados
    if not container_data["gpu_info"]:
        for gpu_info in gpu_data:
            if gpu_info["docker_container_name"] == container:
                container_data["gpu_info"].append(gpu_info)

    return container_data


if __name__ == "_main_":
    main()