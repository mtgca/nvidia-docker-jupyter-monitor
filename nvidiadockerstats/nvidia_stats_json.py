#!/usr/bin/env python3

import subprocess
import io
import csv
import collections
import json
import re
import requests


def get_jupyter_sessions(server_url, token):
    """
        Retrieve  the list of active Jupyter sessions.

        This function sends a request to the Jupyter server API to retrieve the list of active sessions.
        It prints the number of active sessions and details of each session, and returns the list of sessions.
    ß
        Parameters:
        server_url (str): The URL of the Jupyter server. Example: 'http://127.0.0.1:9000'
        token (str): The authentication token for accessing the Jupyter server API. Example: '030b6044cf39b694492a41dc3315a0725171a1c0d9354598'

        Returns:
        list: A list of dictionaries, each containing details of an active Jupyter session.
    """

    # Send a GET request to the Jupyter server to retrieve the list of sessions
    session_list = requests.get(
        f"{server_url}/api/sessions", headers={"Authorization": f"token {token}"}
    ).json()

    # Print the number of active sessions
    print("number of sessions: ", len(session_list))

    # Print details of each session
    for session in session_list:
        print(session)

    # Return the list of sessions
    return session_list


def commandexists(shellcommand):
    status, output = subprocess.getstatusoutput(shellcommand)
    exists = status == 0
    if not exists:
        print("Could not execute: {0}".format(shellcommand))
    return exists


def command(args):
    return subprocess.check_output(args).decode()


def csvtodictdict(csvdata, colnames, keycols, fmtcols={}):
    fmtcols = collections.defaultdict(lambda: lambda x: x, **fmtcols)
    d = {}
    rows = csv.reader(csvdata)
    for row in rows:
        drow = {colname: fmtcols[colname](val) for colname, val in zip(colnames, row)}
        if isinstance(keycols, str):
            key = drow.pop(keycols)
        else:
            key = tuple([drow.pop(keycol) for keycol in keycols])
        d[key] = drow
    return d


def csvheaderargs(fmtcol, cols):
    return ",".join([fmtcol.format(col) for col in cols])


def commandtodictdict(
    baseargs,
    cols,
    keycols=None,
    queryargfmt="{0}",
    colargfmt="{0}",
    outputfmt={},
    skipheader=False,
):
    queryarg = queryargfmt.format(csvheaderargs(colargfmt, cols))
    args = baseargs + [queryarg]
    csvoutput = io.StringIO(command(args))
    if skipheader:
        csvoutput.readline()
    if keycols is None:
        keycols = cols[0]
    return csvtodictdict(csvoutput, cols, keycols, fmtcols=outputfmt)


def renamekeys(d, names):
    for oldname, newname in names.items():
        d[newname] = d.pop(oldname)
    return d


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


def get_jupyter_token(container_name):
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


def get_container_stats(container_name):
    try:
        result = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}",
                container_name,
            ],
            capture_output=True,
            text=True,
        )
        stats = result.stdout.strip().split(",")
        if len(stats) == 6:
            cpu_usage = stats[0]
            mem_usage = stats[1]
            mem_perc = stats[2]
            net_io = stats[3]
            block_io = stats[4]
            pids = stats[5]
            return cpu_usage, mem_usage, mem_perc, net_io, block_io, pids
        else:
            return (
                "Unknown CPU",
                "Unknown MEM USAGE / LIMIT",
                "Unknown MEM %",
                "Unknown NET I/O",
                "Unknown BLOCK I/O",
                "Unknown PIDs",
            )
    except subprocess.CalledProcessError as e:
        print(f"Error getting stats for container {container_name}: {e}")
        return (
            "Unknown CPU",
            "Unknown MEM USAGE / LIMIT",
            "Unknown MEM %",
            "Unknown NET I/O",
            "Unknown BLOCK I/O",
            "Unknown PIDs",
        )


def get_process_name(pid):
    try:
        result = subprocess.run(
            ["ps", "-p", pid, "-o", "comm="], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving process name for PID {pid}: {e}")
        return "Unknown"


def map_pids_to_processes(pids):
    pid_process_mapping = {}
    for pid in pids:
        pid_process_mapping[pid] = get_process_name(pid)
    return pid_process_mapping


def main():
    prefix = ""
    containers = get_container_names(prefix)
    data = []

    unitstats = commandtodictdict(
        ["nvidia-smi", "--format=csv"],
        ["gpu_uuid", "utilization.gpu", "utilization.memory"],
        keycols="gpu_uuid",
        queryargfmt="--query-gpu={0}",
        outputfmt={"gpu_uuid": lambda s: s.lstrip()},
        skipheader=True,
    )
    unitprocstats = commandtodictdict(
        ["nvidia-smi", "--format=csv"],
        ["pid", "process_name", "gpu_uuid", "used_gpu_memory"],
        keycols=["pid", "gpu_uuid"],
        queryargfmt="--query-compute-apps={0}",
        outputfmt={"gpu_uuid": lambda s: s.lstrip()},
        skipheader=True,
    )

    shortunitids = {
        gpu_uuid: "{0}".format(shortid)
        for gpu_uuid, shortid in zip(unitstats.keys(), range(len(unitstats)))
    }
    colnames = {"utilization.gpu": "used_gpu"}
    unitstats = {
        shortunitids[gpu_uuid]: renamekeys(stats, colnames)
        for gpu_uuid, stats in unitstats.items()
    }
    unitprocstats = {
        (pid, shortunitids[gpu_uuid]): stats
        for (pid, gpu_uuid), stats in unitprocstats.items()
    }

    for container in containers:
        container_id = get_container_id(container)
        token = get_jupyter_token(container)
        port = get_container_ports(container)
        cpu_usage, mem_usage, mem_perc, net_io, block_io, pids = get_container_stats(
            container
        )
        try:
            jupyter_session = get_jupyter_sessions(f"http://127.0.0.1:{port}", token)
        except Exception as e:
            print(f"Error getting Jupyter sessions for container {container}: {e}")
            jupyter_session = []
        pids = command(["docker", "top", container, "-eo", "pid"]).split("\n")[1:-1]
        pid_to_process_mapping = map_pids_to_processes(pids)
        containerunitstatslist = [
            ((proc, unit), stats)
            for (proc, unit), stats in sorted(unitprocstats.items())
            if proc in pids
        ]
        containerunitstats = collections.OrderedDict(containerunitstatslist)

        if containerunitstats:
            container_data = {
                "id": container_id,
                "name": container,
                "port": port,
                "token": token,  # Almacenar el token como una cadena
                "Sessions": jupyter_session,
                "cpu_usage": cpu_usage,
                "mem_usage": mem_usage,
                "mem_perc": mem_perc,
                "net_io": net_io,
                "block_io": block_io,
                "pids": pids,
                "pid_to_process_mapping": pid_to_process_mapping,  # Mapeo PID a nombre de proceso
                "gpu_units": [
                    {**stats, **unitstats[unit], "pid": pid, "gpu_unit_number": unit}
                    for (pid, unit), stats in containerunitstats.items()
                ],
            }
            data.append(container_data)
        else:
            container_data = {
                "id": container_id,
                "name": container,
                "port": port,
                "token": token,
                "cpu_usage": cpu_usage,
                "mem_usage": mem_usage,
                "mem_perc": mem_perc,
                "net_io": net_io,
                "block_io": block_io,
                "pids": pids,
                "pid_to_process_mapping": pid_to_process_mapping,
            }
            data.append(container_data)

    with open("tokens_de_jupyter.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    if commandexists("docker") and commandexists("nvidia-smi"):
        main()
    else:
        print("Command(s) not found")
