from board import Board


class Minesweeper:
    MODES = {
        "easy": (6, 6, 6),
        "medium": (9, 9, 15),
        "hard": (12, 12, 30)
    }

    def __init__(self):
        self.board = None

    def choose_mode(self):
        while True:
            mode = input("Choose mode (easy/medium/hard): ").strip().lower()

            if mode in self.MODES:
                rows, cols, mines = self.MODES[mode]
                self.board = Board(rows, cols, mines)
                return

            print("Invalid mode.")

    def display(self, reveal_mines=False):
        b = self.board
        print("\n   " + " ".join(str(c + 1) for c in range(b.cols)))

        for r in range(b.rows):
            cells = []

            for c in range(b.cols):
                pos = (r, c)

                if reveal_mines and pos in b.mines:
                    ch = "*"
                elif pos in b.flags:
                    ch = "F"
                elif pos not in b.revealed:
                    ch = "#"
                elif pos in b.mines:
                    ch = "*"
                else:
                    ch = str(b.adjacent_mines(r, c))

                cells.append(ch)

            print(f"{r + 1:2} " + " ".join(cells))

    def run(self):
        print("Minesweeper")
        self.choose_mode()
        print("Commands: r row col | f row col | q")

        while True:
            self.display()

            raw = input("> ").strip().lower()

            if raw == "q":
                print("Game ended.")
                return

            parts = raw.split()

            if len(parts) != 3 or parts[0] not in {"r", "f"}:
                print("Use r row col or f row col.")
                continue

            try:
                r, c = int(parts[1]) - 1, int(parts[2]) - 1
            except ValueError:
                print("Coordinates must be numbers.")
                continue

            if not self.board.in_bounds(r, c):
                print("Outside the board.")
                continue

            if parts[0] == "f":
                self.board.toggle_flag((r, c))
                print(f"Flag toggled at ({r + 1}, {c + 1}).")
                continue

            hit_mine = self.board.reveal((r, c))

            if hit_mine:
                self.display(reveal_mines=True)
                print(f"Reveal ({r + 1}, {c + 1}): mine hit.")
                print("BOOM! You hit a mine.")
                return

            print(f"Reveal ({r + 1}, {c + 1}): successful.")

            if self.board.won():
                self.display()
                print("You cleared the board!")
                return