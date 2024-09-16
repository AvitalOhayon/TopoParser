# Topology Parser

This project is designed to parse Infiniband topology files and output the results in a clear, structured format. The parsed data is also saved as a JSON file for future reference.

## Features

- Parses Infiniband topology files containing hosts and switches.
- Generates a topology graph based on the file input.
- Progress bar to monitor parsing progress.
- Saves the parsed topology to a JSON file.
- Loads and displays previously saved topology.
- Prints the topology in the order of connections (BFS).
- Accesses the latest topology while a new file is still being parsed.

## How to Use

### 1. Parse a Topology File

To parse a topology file, use the following command:

```bash
python topo_parser.py -f <path_to_topology_file>
```

Example:

```bash
python topo_parser.py -f data/small_topo_file
```

This will parse the topology file, display the progress, and save the results to `last_topology.json`.

### 2. Display the Parsed Topology

To display a previously saved topology, use:

```bash
python topo_parser.py -p
```

This will load the last saved topology from the `last_topology.json` file and print it.

### 3. Access Topology While Parsing

While parsing a new file, you can access the most recently saved topology using the print command (`-p`), which will show the topology saved from the last run even while the new file is being processed.

## Progress Bar

The script provides a progress bar during parsing so you can see how far along the process is. This feature helps when working with large topology files.

## Example Usage

```bash
# Parse a topology file
python topo_parser.py -f data/small_topo_file

# Display the saved topology
python topo_parser.py -p
```

## BFS Printing

The topology is printed in BFS order, showing devices and their connections in the order they are linked in the network.


`   .
`   ├── data/
`   │   ├── small_topo_file         # Sample topology file for testing (small size)
`   │   └── large_topo_file         # Sample topology file for testing (large size)
`   ├── topo_parser.py              # Main script to parse and display topologies
`   ├── topology_parser_lib.py      # Library for topology parsing logic
`   ├── last_topology.json          # JSON file with the last parsed topology
`   ├── tests/
`   │   └── test_topo_parser.py     # Unit tests for the topology parser
`   ├── requirements.txt            # Project dependencies
`   └── README.md                   # Project documentation