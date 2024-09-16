import re
from collections import defaultdict, deque
import threading
import json
import os
import time


class TopologyParser:
    """ Parsing topology file and storing as graph, considering multiple HCA connections."""

    def __init__(self):
        self.devices = defaultdict(lambda: {'type': None, 'connections': [], 'sysimgguid': None})
        self.graph = defaultdict(list)
        self.edges = []
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
            'host_connection': re.compile(r'\[\d+\]\([\w\d]+\)\s+"(S|H)-([\w\d]+)"\[(\d+)\]')
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
        current_device = None
        last_guid = None

        for i, line in enumerate(file_content):
            with self.lock:
                self.progress = i + 1

            guid_match = self.patterns['guid'].search(line)
            if guid_match:
                last_guid = guid_match.group(1)
                continue

            for device_type in ['host', 'switch']:
                match = self.patterns[device_type].search(line)
                if match:
                    current_device = match.group(1)
                    self.devices[current_device]['type'] = device_type.capitalize()
                    self.devices[current_device]['sysimgguid'] = last_guid
                    break
            else:
                if current_device:
                    if self.devices[current_device]["type"] == "Switch":
                        connection_match = self.patterns['switch_connection'].search(line)
                        if connection_match:
                            port, device_type, connected_id = connection_match.groups()
                            connected_device = f"{device_type}-{connected_id}"
                            self.__add_connection(current_device, port, connected_device)
                    elif self.devices[current_device]["type"] == "Host":
                        connection_match = self.patterns['host_connection'].search(line)
                        if connection_match:
                            device_type, connected_id, port = connection_match.groups()
                            connected_device = f"{device_type}-{connected_id}"
                            self.__add_connection(current_device, port, connected_device)

        self.parsing_complete = True

    def __add_connection(self, device: str, port: str, connected_device: str) -> None:
        """
        Add connection between devices and update graph, considering unique HCA-based connections.
        :param device: The current device (host or switch).
        :param port: The port through which the connection occurs.
        :param connected_device: The connected device (host or switch).
        :return:
        """
        with self.lock:
            if (port, connected_device) not in self.devices[device]['connections']:
                self.devices[device]['connections'].append((port, connected_device))
                # Add edge with port information to edges list
                self.edges.append((device, connected_device, port))
                if connected_device not in self.graph[device]:
                    self.graph[device].append(connected_device)
                if device not in self.graph[connected_device]:
                    self.graph[connected_device].append(device)

    def __bfs_topology_order(self):
        """Perform BFS to print devices in order of connectivity.
            The scan starts with the first available host; if none is found, it starts from the first switch.
        """
        visited = set()
        queue = deque()

        for device, details in self.devices.items():
            if details['type'] == 'Host':
                queue.append(device)
                visited.add(device)
                break

        if not queue:
            for device, details in self.devices.items():
                if details['type'] == 'Switch':
                    queue.append(device)
                    visited.add(device)
                    break

        result = []
        while queue:
            device = queue.popleft()
            result.append(device)
            for neighbor in self.graph[device]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def __print_device(self, details):
        device_type = details['type']
        print(f"{device_type}:")
        print(f"  sysimgguid={details['sysimgguid']}")
        for connection in details['connections']:
            port, connected_device = connection
            if 'H' in connected_device:
                print(f"  Connected to host: {connected_device}, port={port}")
            else:
                print(f"  Connected to switch: {connected_device}, port={port}")
        print()

    def print_topology(self) -> None:
        """Print topology considering multiple HCA connections."""

        if self.file_name:
            print(f"Topology from file: {self.file_name}\n")
        bfs_order = self.__bfs_topology_order()

        for device in bfs_order:
            details = self.devices[device]
            self.__print_device(details)


    def save_topology_to_file(self, filename="last_topology.json"):
        """Save the current topology to a file and ensure no old content remains."""
        try:
            with open(filename, 'w') as file:
                json.dump({
                    'devices': {k: dict(v) for k, v in self.devices.items()},
                    'graph': dict(self.graph),
                    'edges': self.edges,
                    'file_name': self.file_name
                }, file)
            print(f"Topology saved to {filename}")
        except Exception as e:
            print(f"Failed to save topology: {e}")

    def load_topology_from_file(self, filename="last_topology.json"):
        """Load the topology from a file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    data = json.load(file)
                    self.devices = defaultdict(lambda: {'type': None, 'connections': [], 'sysimgguid': None}, data['devices'])
                    self.graph = defaultdict(list, data['graph'])
                    self.edges = data['edges']
                    self.file_name = data.get('file_name', None)
            else:
                print(f"There is no existing topology.")
        except Exception as e:
            print(f"Failed to load topology: {e}")

    def get_progress(self):
        """Return the current progress and total lines for the progress bar."""
        with self.lock:
            return self.progress, self.total_lines