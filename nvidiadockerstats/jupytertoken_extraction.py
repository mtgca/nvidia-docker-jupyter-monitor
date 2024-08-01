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


def get_jupyter_tokens(container_name):
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "jupyter", "notebook", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        tokens = []
        token_pattern = re.compile(r"token=([a-zA-Z0-9]+)")
        for line in result.stdout.splitlines():
            if "http" in line:
                match = token_pattern.search(line)
                if match:
                    tokens.append(match.group(1))
        return tokens
    except subprocess.CalledProcessError as e:
        print(f"Error getting Jupyter tokens from {container_name}: {e}")
        return []


def get_container_ports(container_name):
    try:
        result = subprocess.run(
            ["docker", "port", container_name], capture_output=True, text=True
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


def build_jupyter_url(port, token):
    return f"http://127.0.0.1:{port}/lab?token={token}"


def main():
    prefix = "colab_"
    containers = get_container_names(prefix)
    data = []
    for container in containers:
        tokens = get_jupyter_tokens(container)
        port = get_container_ports(container)
        container_data = {"name": container, "port": port, "token": tokens}
        data.append(container_data)
    with open("tokens_de_jupyter.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
