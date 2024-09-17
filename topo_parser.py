import argparse
import threading
import time
from tqdm import tqdm
from topology_parser_lib import TopologyParser


def parse_worker(parser, file_path: str) -> None:
    """
    Worker function to parse the topology file and save the results.

    :param parser: TopologyParser object
    :param file_path: Path to the topology file
    :return: None
    """
    parser.parse_topology_file(file_path)
    parser.save_topology_to_file()

def progress_reporter(parser: TopologyParser) -> None:
    """
    Thread function to report parsing progress using a progress bar.

    :param parser: TopologyParser object
    :return: None
    """
    print("Accepting and opening the file.")
    while parser.total_lines == 0:
        time.sleep(0.05)

    with tqdm(total=parser.total_lines, desc="Parsing progress", unit="lines") as pbar:
        last_progress = 0
        while not parser.parsing_complete:
            progress, _ = parser.get_progress()
            if progress > last_progress:
                pbar.update(progress - last_progress)
                last_progress = progress
            time.sleep(0.1)

        if last_progress < pbar.total:
            pbar.update(pbar.total - last_progress)

        pbar.refresh()
        pbar.close()


def main() -> None:
    """
    Main function to handle command line arguments and initiate parsing or printing topology.

    :return: None
    """
    arg_parser = argparse.ArgumentParser(description='Parse and print Infiniband topology.')
    arg_parser.add_argument('-f', '--file', type=str, help='New topology file to parse.')
    arg_parser.add_argument('-p', '--print', action='store_true', help='Print the existing topology.')

    args = arg_parser.parse_args()

    if args.file:
        topo_parser = TopologyParser()

        parse_thread = threading.Thread(target=parse_worker, args=(topo_parser, args.file))
        progress_thread = threading.Thread(target=progress_reporter, args=(topo_parser,))

        parse_thread.start()
        progress_thread.start()

        print(f"Parsing new file: {args.file}")
        print("\nYou can use 'topo_parser -p' in another terminal to print the existing topology.")

        parse_thread.join()
        progress_thread.join()

        print("\nParsing complete. New topology saved.")
    elif args.print:
        topo_parser_2 = TopologyParser()
        topo_parser_2.load_topology_from_file()
        topo_parser_2.print_topology()
    else:
        arg_parser.print_help()


if __name__ == "__main__":
    main()







