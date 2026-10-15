from project.problem import Problem
import argparse
from collections import deque


class DFADeterminizer(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--det',
            help='Determinize the given automaton.',
            action='store_true'
        )

    def is_chosen_problem(self, args):
        return bool(args.det)

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f]

        states = lines[0].strip().split()
        alphabet = lines[1].strip().split()
        start_state = lines[2].strip()
        accept_states = lines[3].strip().split()

        if start_state not in states:
            raise ValueError(f"Invalid start state: {start_state}")

        for s in accept_states:
            if s not in states:
                raise ValueError(f"Invalid accept state: {s}")

        transitions = {}
        for line in lines[4:]:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) != 3:
                raise ValueError(f"Invalid transition line: {line}")

            from_state, symbol, to_state = tokens

            if from_state not in states:
                raise ValueError(f"Invalid state in transition: {from_state}")
            if to_state not in states:
                raise ValueError(f"Invalid state in transition: {to_state}")
            if symbol not in alphabet:
                raise ValueError(f"Invalid symbol in transition: {symbol}")

            transitions.setdefault(from_state, {}).setdefault(symbol, set()).add(to_state)

        # Subset construction: each DFA state is a frozenset of NFA states,
        # discovered via BFS so that state names s0, s1, ... follow discovery order.
        start_set = frozenset([start_state])

        ordered_sets = []
        set_to_index = {}

        queue = deque([start_set])
        set_to_index[start_set] = 0
        ordered_sets.append(start_set)

        dfa_transitions = {}

        while queue:
            current_set = queue.popleft()
            current_idx = set_to_index[current_set]

            for symbol in alphabet:
                next_set = set()
                for state in current_set:
                    if state in transitions and symbol in transitions[state]:
                        next_set.update(transitions[state][symbol])

                if not next_set:
                    continue

                next_set = frozenset(next_set)

                if next_set not in set_to_index:
                    set_to_index[next_set] = len(ordered_sets)
                    ordered_sets.append(next_set)
                    queue.append(next_set)

                dfa_transitions[(current_idx, symbol)] = set_to_index[next_set]

        name_of = {}
        for i, s in enumerate(ordered_sets):
            name_of[s] = f"s{i}"

        dfa_start_idx = set_to_index[start_set]
        dfa_start = name_of[ordered_sets[dfa_start_idx]]

        dfa_accept = []
        for i, s in enumerate(ordered_sets):
            if any(st in accept_states for st in s):
                dfa_accept.append(name_of[s])

        out_lines = []

        out_lines.append(" ".join(name_of[s] for s in ordered_sets))
        out_lines.append(" ".join(alphabet))
        out_lines.append(dfa_start)
        out_lines.append(" ".join(dfa_accept))

        # Sort edges by source state index, then alphabet order of symbol, then target index.
        symbol_order = {sym: i for i, sym in enumerate(alphabet)}

        sorted_edges = sorted(
            dfa_transitions.items(),
            key=lambda item: (item[0][0], symbol_order[item[0][1]], item[1])
        )

        for (from_idx, symbol), to_idx in sorted_edges:
            out_lines.append(
                f"{name_of[ordered_sets[from_idx]]} {symbol} {name_of[ordered_sets[to_idx]]}"
            )

        with open(output_file, 'w') as f:
            f.write("\n".join(out_lines) + "\n")
            
        #python -m project --input project/input1.txt --output project/output1.txt --det