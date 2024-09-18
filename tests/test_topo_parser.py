import unittest
import os
import sys
from io import StringIO
from topology_parser_lib import TopologyParser
import difflib


class TestTopologyParser(unittest.TestCase):
    def setUp(self):
        self.parser = TopologyParser()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_file_path = os.path.join(current_dir, '..', 'data', 'small_topo_file')
        self.expected_output_path = os.path.join(current_dir, '..', 'data', 'expected_small_topo_output')

    def test_topology_parser_output(self):
        """Verifies that the topology parser's output matches the expected output for a sample input file."""

        self.assertTrue(os.path.exists(self.sample_file_path),
                        f"Topology file not found at {self.sample_file_path}")
        self.assertTrue(os.path.exists(self.expected_output_path),
                        f"Expected output file not found at {self.expected_output_path}")

        self.parser.parse_topology_file(self.sample_file_path)

        captured_output = StringIO()
        sys.stdout = captured_output
        self.parser.print_topology()
        sys.stdout = sys.__stdout__

        with open(self.expected_output_path, 'r') as file:
            expected_output = file.read()

        captured_output_value = captured_output.getvalue()

        if not captured_output_value.startswith("Topology from file:"):
            captured_output_value = f"Topology from file: {os.path.basename(self.sample_file_path)}\n\n" + captured_output_value

        if captured_output_value.strip() != expected_output.strip():
            diff = list(difflib.unified_diff(
                expected_output.strip().splitlines(),
                captured_output_value.strip().splitlines(),
                fromfile='Expected',
                tofile='Actual',
                lineterm=''
            ))

            diff_message = "\n".join(diff)
            self.assertEqual(captured_output_value.strip(), expected_output.strip(),
                             f"The parser output does not match the expected output. Differences:\n{diff_message}")


if __name__ == '__main__':
    unittest.main()
