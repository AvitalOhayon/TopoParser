import os
import re
import threading
import time
import json
from collections import defaultdict, deque
from threading import Lock


class TopologyParser:
    """ Parsing topology file and storing as graph, considering multiple HCA connections."""

    def __init__(self):
        self.topology = defaultdict(lambda: { 'type': None, 'connections': defaultdict(list)})

        self.caguid_map = defaultdict(str)
        self.switchguid_map = defaultdict(str)
        self.file_name = None
        self.lock = threading.Lock()
        self.progress = 0
        self.total_lines = 0
        self.parsing_complete = False

        self.patterns = {
            'host': re.compile(r'Ca\s+\d+\s+"(H-[\w\d]+)"'),
            'switch': re.compile(r'Switch\s+\d+\s+"(S-[\w\d]+)"'),
            'guid': re.compile(r'sysimgguid=([\w\d]+)'),
            'switch_connection': re.compile(r'\[([\d]+)\]\s+"(S|H)-([\w\d]+)"\[\d+\]'),
            'host_connection': re.compile(r'\[\d+\]\([\w\d]+\)\s+"(S|H)-([\w\d]+)"\[(\d+)\]'),
            'caguid': re.compile(r'caguid=([\w\d]+)'),  # תבנית ל-caguid
            'switchguid': re.compile(r'switchguid=([\w\d]+)')  # תבנית ל-switchguid
        }

    def parse_topology_file(self, file_path: str) -> None:
        """
        Parse topology file from a given file path and construct a graph and a dictionary.
        :param file_path: Path to the topology file to be parsed
        :return:
        """
        self.file_name = os.path.basename(file_path)
        try:
            with open(file_path, 'r') as file:
                file_content = file.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

        self.total_lines = len(file_content)
        current_sysimgguid = None
        current_type = None
        current_caguid = None
        current_switchguid = None

        for i, line in enumerate(file_content):
            with self.lock:
                self.progress = i + 1

            guid_match = self.patterns['guid'].search(line)
            if guid_match:
                current_sysimgguid = guid_match.group(1)
                continue

            caguid_match = self.patterns['caguid'].search(line)
            if caguid_match:
                current_caguid = caguid_match.group(1)
                current_type = "Host"
                self.topology[current_sysimgguid]['type'] = current_type
                continue

            switchguid_match = self.patterns['switchguid'].search(line)
            if switchguid_match:
                current_switchguid = switchguid_match.group(1)
                current_type = "Switch"
                self.topology[current_sysimgguid]['type'] = current_type
                continue

            for device_type in ['host', 'switch']:
                match = self.patterns[device_type].search(line)
                if match:
                    current_device = match.group(1)
                    if current_device[0] == 'S':
                        self.switchguid_map[current_device] = current_sysimgguid
                    else:
                        self.caguid_map[current_device] = current_sysimgguid
                    break

            if current_type and current_sysimgguid:
                if current_type == "Switch":

                    connection_match = self.patterns['switch_connection'].search(line)
                    if connection_match:
                        port, device_type, connected_id = connection_match.groups()
                        connected_device = f"{device_type}-{connected_id}"
                        self.__add_connection(current_sysimgguid, current_switchguid, port, connected_device)
                elif current_type == "Host":
                    connection_match = self.patterns['host_connection'].search(line)
                    if connection_match:
                        device_type, connected_id, port = connection_match.groups()
                        connected_device = f"{device_type}-{connected_id}"
                        self.__add_connection(current_sysimgguid, current_caguid, port, connected_device)

        self.parsing_complete = True

    def __add_connection(self, sysimgguid: str, guid: str, port: str, connected_device: str) -> None:
        """
        Add connection between devices and update topology, considering unique HCA-based connections.
        :param sysimgguid: The sysimgguid of the current device (host or switch).
        :param caguid: The caguid of the HCA or device.
        :param port: The port through which the connection occurs.
        :param connected_device: The connected device (host or switch).
        :return:
        """
        if (port, connected_device) not in self.topology[sysimgguid]['connections'][guid]:
            self.topology[sysimgguid]['connections'][guid].append((port, connected_device))


    def __bfs_topology_order(self):
        """Perform BFS to print devices in order of connectivity.
            The scan starts with the first available host; if none is found, it starts from the first switch.
        """
        visited = set()
        queue = deque()

        for device, details in self.topology.items():
            if details['type'] == 'Host':
                queue.append(device)
                visited.add(device)
                break

        if not queue:
            for device, details in self.topology.items():
                if details['type'] == 'Switch':
                    queue.append(device)
                    visited.add(device)
                    break

        result = []
        while queue:
            device = queue.popleft()
            result.append(device)
            for guid, connections in self.topology[device]['connections'].items():
                for port, connected_device in connections:
                    if connected_device[0] == 'S':
                        connected_device = self.switchguid_map[connected_device]
                    else:
                        connected_device = self.caguid_map[connected_device]
                    if connected_device not in visited:
                        visited.add(connected_device)
                        queue.append(connected_device)

        return result

    def __print_device(self, sysimgguid, details):
        device_type = details['type']
        print(f"{device_type}:")
        print(f"  sysimgguid={sysimgguid}")
        for guid, connections in details['connections'].items():
            if device_type == "Switch":
                print(f"  switchuid={guid}")
            else:
                print(f"  caguid={guid}")
            for port, connection in connections:
                if 'H' in connection:
                    print(f"  Connected to host: {connection}({self.caguid_map[connection]}), port={port}")
                else:
                    print(f"  Connected to switch: {connection}({self.switchguid_map[connection]}), port={port}")
        print()

    def print_topology(self) -> None:
        """Print topology considering multiple HCA connections."""

        if self.file_name:
            print(f"Topology from file: {self.file_name}\n")
        bfs_order = self.__bfs_topology_order()

        for device in bfs_order:
            details = self.topology[device]
            self.__print_device(device, details)


    def save_topology_to_file(self, filename="last_topology.json"):
        """Save the current topology to a file and ensure no old content remains."""
        lock = Lock()
        if lock.acquire(timeout=5):
            try:
                with open(filename, 'w') as file:
                    json.dump({
                        'topology': {k: dict(v) for k, v in self.topology.items()},
                        'caguid_map': {k: v for k, v in self.caguid_map.items()},
                        'switchguid_map': {k: v for k, v in self.switchguid_map.items()},
                        'file_name': self.file_name
                    }, file)
            except Exception as e:
                print(f"Failed to save topology: {e}")
            lock.release()
            print(f"Topology saved to {filename}")
        else:
            print("Failed to acquire lock.")


    def load_topology_from_file(self, filename="last_topology.json"):
        """Load the topology from a file."""

        if not os.path.exists(filename):
            print(f"There is no existing topology file at {filename}.")

        lock = Lock()
        if lock.acquire(timeout=5):
            try:
                with open(filename, 'r') as file:
                    data = json.load(file)
                    self.topology = defaultdict(lambda: {
                        'type': None,
                        'connections': defaultdict(list)
                    }, data.get('topology', {}))
                    self.caguid_map = data.get('caguid_map', {})
                    self.switchguid_map = data.get('switchguid_map', {})
                    self.file_name = data.get('file_name', None)
            except Exception as e:
                print(f"Failed to load topology: {e}")
            lock.release()
            print(f"Topology loaded from {filename}")
        else:
            print("Failed to acquire lock.")


    def get_progress(self):
        """Return the current progress and total lines for the progress bar."""
        with self.lock:
            return self.progress, self.total_lines