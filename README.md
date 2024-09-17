# Topology Parser

This project is designed to parse Infiniband topology files and output the results in a clear, structured format. 
## Features

- Parses Infiniband topology files containing hosts and switches.
- Generates a topology graph based on the file input.
- Progress bar to monitor parsing progress.
- Loads and displays previously saved topology.
- Prints the topology in the order of connections (BFS).
- Accesses the latest topology while a new file is still being parsed.


## Installation

Before running the project, you need to install the required dependencies. You can do this easily by using the `requirements.txt` file.

To install the requirements, run the following command:

```bash
pip install -r requirements.txt
```
This will install all the necessary libraries, such as tqdm and pytest.

## How to Use


### 1. Display Help

To see usage instructions and available options:

```bash
python topo_parser.py -h
```

This will print the usage information and exit.

### 2. Parse a Topology File

To parse a topology file, use the following command:

```
python topo_parser.py -f <path_to_topology_file>
```

This will parse the topology file and display the progress.

### 3. Display the Parsed Topology

To display a previously saved topology, use:

```bash
python topo_parser.py -p
```

This will load the last saved topology and print it.

### 4. Access Topology While Parsing

While parsing a new file, you can access the most recently saved topology using the print command (`-p`), which will show the topology saved from the last run even while the new file is being processed.

## Example Usage

1. Display help and usage information:
```bash
python topo_parser.py -h
```

2. Parse a topology file:
```bash
python topo_parser.py -f data/small_topo_file
```

3. Display the saved topology:
```bash
python topo_parser.py -p
```

## Example Output

When you parse a topology file, the output will look similar to this:

```
Topology from file: small_topo_file

Host: 
  sysimgguid=guid1
  Connected to switch: S-1, port=1

Switch: 
  sysimgguid=guid2
  Connected to host: H-1, port=1
  Connected to switch: S-2, port=2

Switch: 
  sysimgguid=guid3
  Connected to switch: S-1, port=1
  Connected to host: H-2, port=2
```

This output shows the connections between hosts and switches, including the system image GUIDs and port numbers.

### How the Topology is Parsed
The parser reads the topology file line by line, building a graph of devices (nodes) and connections (edges with port info). 
It also creates a dictionary to store device details, such as sysimgguid and connections. 

The topology is then printed in BFS order to show the network structure.

## Project Structure

<pre><code>.
├── data/
│   ├── small_topo_file              # Sample topology file for testing (small size)
│   ├── large_topo_file              # Sample topology file for testing (large size)
│   └── expected_small_topo_output   # Expected output file for small topology test
├── topo_parser.py                   # Main script to parse and display topologies
├── topology_parser_lib.py           # Library for topology parsing logic
├── tests/
│   └── test_topo_parser.py          # Unit tests for the topology parser
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
</code></pre>