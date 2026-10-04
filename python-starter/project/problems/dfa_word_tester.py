from project.problem import Problem
import argparse


class DFAWordTester(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument(
            '--check',
            help='Tests the DFA. Comma-separated list of words.',
            type=str
        )

    def is_chosen_problem(self, args):
        """
        Check if the DFA problem is chosen
        """
        return args.check is not None

    def run(self, args):
        """
        Run the DFA word tester
        """
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r') as f:
            lines = f.read().splitlines()

        # 1. sor: állapotok (nem használjuk külön)
        # 2. sor: ábécé (nem használjuk külön)
        # 3. sor: kezdő állapot
        # 4. sor: elfogadó állapotok (space-el elválasztva)
        # további sorok: átmenetek: "honnan jel hova"

        start_node = lines[2].strip()
        end_nodes = lines[3].strip().split()

        graph = {}
        for line in lines[4:]:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) == 3:
                from_state, symbol, to_state = tokens
                graph.setdefault(from_state, {})[symbol] = to_state
            else:
                raise ValueError(f"Invalid transition line: {line}")

        words = args.check.split(',')

        results = []
        for word in words:
            current = start_node
            ok = True
            for ch in word:
                if current in graph and ch in graph[current]:
                    current = graph[current][ch]
                else:
                    ok = False
                    break

            if ok and current in end_nodes:
                results.append("IGEN")
            else:
                results.append("NEM")

        with open(output_file, 'w') as f:
            f.write("\n".join(results) + "\n")