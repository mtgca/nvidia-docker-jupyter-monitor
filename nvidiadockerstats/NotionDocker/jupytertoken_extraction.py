import json
import subprocess
import re


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
            cpu_usage = stats[0]
            mem_usage = stats[1]
            mem_perc = stats[2]
            net_io = stats[3]
            block_io = stats[4]
            return cpu_usage, mem_usage, mem_perc, net_io, block_io
        else:
            return (
                "Unknown CPU",
                "Unknown MEM USAGE / LIMIT",
                "Unknown MEM %",
                "Unknown NET I/O",
                "Unknown BLOCK I/O",
            )
    except subprocess.CalledProcessError as e:
        print(f"Error getting stats for container {container_name}: {e}")
        return (
            "Unknown CPU",
            "Unknown MEM USAGE / LIMIT",
            "Unknown MEM %",
            "Unknown NET I/O",
            "Unknown BLOCK I/O",
        )


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
                    return match.group(1)  # Devolver solo el token sin corchetes
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

        # Extracción del puerto
        ports = []
        for line in port_mapping.splitlines():
            parts = line.split(":")
            if len(parts) == 2:
                ports.append(parts[1])

        # Tomar el primer puerto si hay múltiples
        if ports:
            return ports[0]
        else:
            return "Unknown port"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving ports from container {container_name}: {e}")
        return "Unknown port"


def build_jupyter_url(port, token):
    return f"http://127.0.0.1:{port}/lab?token={token}"


def main():
    prefix = "colab_"
    containers = get_container_names(prefix)
    data = []
    for container in containers:
        container_id = get_container_id(container)
        tokens = get_jupyter_tokens(container)
        port = get_container_ports(container)
        cpu_usage, mem_usage, mem_perc, net_io, block_io = get_container_stats(
            container
        )
        container_data = {
            "id": container_id,
            "name": container,
            "port": port,
            "token": tokens,
            "cpu_usage": cpu_usage,
            "mem_usage": mem_usage,
            "mem_perc": mem_perc,
            "net_io": net_io,
            "block_io": block_io,
        }
        data.append(container_data)
    with open("tokens_de_jupyter.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
