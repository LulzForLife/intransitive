from __future__ import annotations

__author__ = "Kiran Lowe"

__email__ = "kiranmjlowe@gmail.com"

__version__ = "1.0.0"

from typing import TypeAlias, Self

import dataclasses
import re

Color: TypeAlias = bool
BLUE: Color = True
RED: Color = False
COLORS: list[Color] = [RED, BLUE]
COLOR_NAMES: list[str] = ["blue", "red"]

PieceType: TypeAlias = int
ROCK: PieceType = 0
PAPER: PieceType = 1
SCISSORS: PieceType = 2
PIECE_TYPES: list[PieceType] = [ROCK, PAPER, SCISSORS]
PIECE_SYMBOLS: list[str] = ["r", "p", "s"]
PIECE_NAMES: list[str] = ["rock", "paper", "scissors"]

CAPTURES = {
    ROCK: SCISSORS,
    PAPER: ROCK,
    SCISSORS: PAPER
}

Square: TypeAlias = int
A1: Square = 0
A2: Square = 1
A3: Square = 2
A4: Square = 3
A5: Square = 4
A6: Square = 5
A7: Square = 6
A8: Square = 7
A9: Square = 8
B1: Square = 9
B2: Square = 10
B3: Square = 11
B4: Square = 12
B5: Square = 13
B6: Square = 14
B7: Square = 15
B8: Square = 16
B9: Square = 17
C1: Square = 18
C2: Square = 19
C3: Square = 20
C4: Square = 21
C5: Square = 22
C6: Square = 23
C7: Square = 24
C8: Square = 25
C9: Square = 26
D1: Square = 27
D2: Square = 28
D3: Square = 29
D4: Square = 30
D5: Square = 31
D6: Square = 32
D7: Square = 33
D8: Square = 34
D9: Square = 35
E1: Square = 36
E2: Square = 37
E3: Square = 38
E4: Square = 39
E5: Square = 40
E6: Square = 41
E7: Square = 42
E8: Square = 43
E9: Square = 44
F1: Square = 45
F2: Square = 46
F3: Square = 47
F4: Square = 48
F5: Square = 49
F6: Square = 50
F7: Square = 51
F8: Square = 52
F9: Square = 53
G1: Square = 54
G2: Square = 55
G3: Square = 56
G4: Square = 57
G5: Square = 58
G6: Square = 59
G7: Square = 60
G8: Square = 61
G9: Square = 62
H1: Square = 63
H2: Square = 64
H3: Square = 65
H4: Square = 66
H5: Square = 67
H6: Square = 68
H7: Square = 69
H8: Square = 70
H9: Square = 71
I1: Square = 72
I2: Square = 73
I3: Square = 74
I4: Square = 75
I5: Square = 76
I6: Square = 77
I7: Square = 78
I8: Square = 79
I9: Square = 80

SQUARES = [A1, A2, A3, A4, A5, A6, A7, A8, A9, B1, B2, B3, B4, B5, B6, B7, B8, B9, C1, C2, C3, C4, C5, C6, C7, C8, C9, D1, D2, D3, D4, D5, D6, D7, D8, D9, E1, E2, E3, E4, E5, E6, E7, E8, E9, F1, F2, F3, F4, F5, F6, F7, F8, F9, G1, G2, G3, G4, G5, G6, G7, G8, G9, H1, H2, H3, H4, H5, H6, H7, H8, H9, I1, I2, I3, I4, I5, I6, I7, I8, I9]

FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

UCI_REGEX = r"^[a-z][1-9][a-z][1-9]$"
SAN_REGEX = r"^[rps][a-z][1-9][-|x][a-z][1-9]$"

STARTING_FEN = "9/4pr3/4spr2/5spr1/1PS3sp1/1RPS5/2RPS4/3RP4/9 b 0"
FEN_REGEX = r"^[a-zA-Z0-9]+(\/[a-zA-Z0-9]+){8}\s[br]\s\d+$"

BLUE_WIN_MASK = 1 << 80
RED_WIN_MASK = 1
FULL_BOARD = (1 << 81) - 1

@dataclasses.dataclass(slots=True)
class Move:
    from_sq: Square
    to_sq: Square
    capture: PieceType | None = None

    @classmethod
    def from_uci(cls: type[Self], uci: str, board: Board) -> Self:
        uci = uci.lower()
        match = re.fullmatch(UCI_REGEX, uci)
        if match is None:
            raise ValueError(
                f"Invalid uci: {uci}"
            )

        file1 = uci[0].lower()
        rank1 = uci[1]
        file2 = uci[2].lower()
        rank2 = uci[3]

        sq1 = FILE_NAMES.index(file1) * 9 + RANK_NAMES.index(rank1)
        sq2 = FILE_NAMES.index(file2) * 9 + RANK_NAMES.index(rank2)

        capture = None
        mask = 1 << sq2
        if board.rb_bb & mask:
            capture = ROCK
        elif board.pb_bb & mask:
            capture = PAPER
        elif board.sb_bb & mask:
            capture = SCISSORS
        elif board.rr_bb & mask:
            capture = ROCK
        elif board.pr_bb & mask:
            capture = PAPER
        elif board.sr_bb & mask:
            capture = SCISSORS

        return cls(sq1, sq2, capture)

    @classmethod
    def from_san(cls: type[Self], san: str, board: Board) -> Self:
        san = san.lower()
        match = re.fullmatch(SAN_REGEX, san)
        if match is None:
            raise ValueError(
                f"Invalid san: {san}"
            )

        file1 = san[1].lower()
        rank1 = san[2]
        file2 = san[4].lower()
        rank2 = san[5]

        sq1 = FILE_NAMES.index(file1) * 9 + RANK_NAMES.index(rank1)
        sq2 = FILE_NAMES.index(file2) * 9 + RANK_NAMES.index(rank2)

        n = cls(sq1, sq2)
        n.resolve_capture(board)
        return n

    def uci(self) -> str:
        file1, rank1 = divmod(self.from_sq, 9)
        file2, rank2 = divmod(self.to_sq, 9)

        sq1 = f"{FILE_NAMES[file1]}{RANK_NAMES[rank1]}"
        sq2 = f"{FILE_NAMES[file2]}{RANK_NAMES[rank2]}"

        return f"{sq1}{sq2}"

    def san(self, board: Board) -> str:
        file1, rank1 = divmod(self.from_sq, 9)
        file2, rank2 = divmod(self.to_sq, 9)

        sq1 = f"{FILE_NAMES[file1]}{RANK_NAMES[rank1]}"
        sq2 = f"{FILE_NAMES[file2]}{RANK_NAMES[rank2]}"

        piece = ROCK
        mask = 1 << self.from_sq
        if board.rb_bb & mask:
            piece = ROCK
        elif board.pb_bb & mask:
            piece = PAPER
        elif board.sb_bb & mask:
            piece = SCISSORS
        elif board.rr_bb & mask:
            piece = ROCK
        elif board.pr_bb & mask:
            piece = PAPER
        elif board.sr_bb & mask:
            piece = SCISSORS

        return f"{PIECE_SYMBOLS[piece]}{sq1}{'x' if self.is_capture() else '-'}{sq2}"

    def __str__(self) -> str:
        return self.uci()

    def is_capture(self) -> bool:
        return self.capture is not None

    is_zeroing = is_capture

    def resolve_capture(self, board: Board) -> PieceType | None:
        capture = None
        mask = 1 << self.to_sq
        if board.rb_bb & mask:
            capture = ROCK
        elif board.pb_bb & mask:
            capture = PAPER
        elif board.sb_bb & mask:
            capture = SCISSORS
        elif board.rr_bb & mask:
            capture = ROCK
        elif board.pr_bb & mask:
            capture = PAPER
        elif board.sr_bb & mask:
            capture = SCISSORS
        return capture

class Board:
    __slots__ = ("rb_bb", "pb_bb", "sb_bb", "rr_bb", "pr_bb", "sr_bb", "turn", "halfmove_clock", "move_stack", "halfmove_stack")

    def __init__(self, fen: str | None = STARTING_FEN) -> None:
        self.rb_bb = 0
        self.pb_bb = 0
        self.sb_bb = 0
        self.rr_bb = 0
        self.pr_bb = 0
        self.sr_bb = 0

        self.turn: Color = BLUE
        self.halfmove_clock = 0

        self.move_stack: list[Move] = []
        self.halfmove_stack: list[int] = []

        if fen is not None:
            self.set_fen(fen)

    def __hash__(self) -> int:
        raise NotImplementedError

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Board):
            return (
                self.rb_bb == value.rb_bb and
                self.pb_bb == value.pb_bb and
                self.sb_bb == value.sb_bb and
                self.rr_bb == value.rr_bb and
                self.pr_bb == value.pr_bb and
                self.sr_bb == value.sr_bb and
                self.turn == value.turn and
                self.halfmove_clock == value.halfmove_clock and
                self.move_stack == value.move_stack and
                self.halfmove_stack == value.halfmove_stack
            )

        return NotImplemented

    def set_fen(self, fen: str) -> None:
        match = re.fullmatch(FEN_REGEX, fen)
        if match is None:
            raise ValueError(
                f"Invalid fen: {fen}"
            )

        board_str, turn_str, halfmove_str = fen.split()
        turn = BLUE if turn_str.lower() == "b" else RED
        halfmove_clock = int(halfmove_str)
        rb_bb = 0
        pb_bb = 0
        sb_bb = 0
        rr_bb = 0
        pr_bb = 0
        sr_bb = 0
        
        for rank_idx, rank_str in enumerate(board_str.split("/")):
            rank = 8 - rank_idx
            file = 0
            for char in rank_str:
                if char.isnumeric():
                    file += int(char)
                else:
                    idx = file * 9 + rank
                    match char:
                        case "R": rb_bb |= 1 << idx
                        case "P": pb_bb |= 1 << idx
                        case "S": sb_bb |= 1 << idx
                        case "r": rr_bb |= 1 << idx
                        case "p": pr_bb |= 1 << idx
                        case "s": sr_bb |= 1 << idx
                    file += 1

        self.rb_bb = rb_bb
        self.pb_bb = pb_bb
        self.sb_bb = sb_bb
        self.rr_bb = rr_bb
        self.pr_bb = pr_bb
        self.sr_bb = sr_bb
        self.turn = turn
        self.halfmove_clock = halfmove_clock
        self.move_stack.clear()
        self.halfmove_stack.clear()

    def fen(self) -> str:
        fen = ""
        for rank in range(8, -1, -1):
            fen += "/"
            num = 0
            for file in range(9):
                idx = file * 9 + rank
                mask = 1 << idx
                piece = ""
                if self.rb_bb & mask:
                    piece = "R"
                elif self.pb_bb & mask:
                    piece = "P"
                elif self.sb_bb & mask:
                    piece = "S"
                elif self.rr_bb & mask:
                    piece = "r"
                elif self.pr_bb & mask:
                    piece = "p"
                elif self.sr_bb & mask:
                    piece = "s"

                if piece:
                    if num != 0:
                        fen += str(num)
                    fen += piece
                    num = 0
                else:
                    num += 1
            
            if num != 0:
                fen += str(num)

        if self.turn:
            fen += " b "
        else:
            fen += " r "

        fen += str(self.halfmove_clock)

        return fen[1:]

    def copy(self, copy_stack: bool = True) -> Board:
        n = Board(None)
        n.rb_bb = self.rb_bb
        n.pb_bb = self.pb_bb
        n.sb_bb = self.sb_bb
        n.rr_bb = self.rr_bb
        n.pr_bb = self.pr_bb
        n.sr_bb = self.sr_bb

        n.halfmove_clock = self.halfmove_clock
        n.turn = self.turn

        if copy_stack:
            n.move_stack = self.move_stack.copy()
            n.halfmove_stack = self.halfmove_stack.copy()

        return n

    def apply(self, move: Move) -> None:
        self.move_stack.append(move)
        self.halfmove_stack.append(self.halfmove_clock)

        remove_piece = 1 << move.from_sq
        add_piece = 1 << move.to_sq
        move_xor = add_piece | remove_piece

        if move.is_capture():
            if not self.turn:
                if move.capture == ROCK:
                    self.rb_bb ^= add_piece
                elif move.capture == PAPER:
                    self.pb_bb ^= add_piece
                elif move.capture == SCISSORS:
                    self.sb_bb ^= add_piece
            else:
                if move.capture == ROCK:
                    self.rr_bb ^= add_piece
                elif move.capture == PAPER:
                    self.pr_bb ^= add_piece
                elif move.capture == SCISSORS:
                    self.sr_bb ^= add_piece

        if self.rb_bb & remove_piece:
            self.rb_bb ^= move_xor
        elif self.pb_bb & remove_piece:
            self.pb_bb ^= move_xor
        elif self.sb_bb & remove_piece:
            self.sb_bb ^= move_xor
        elif self.rr_bb & remove_piece:
            self.rr_bb ^= move_xor
        elif self.pr_bb & remove_piece:
            self.pr_bb ^= move_xor
        elif self.sr_bb & remove_piece:
            self.sr_bb ^= move_xor

        if move.is_zeroing():
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        self.turn = not self.turn

    def undo(self) -> Move:
        self.turn = not self.turn
        self.halfmove_clock = self.halfmove_stack.pop()
        move = self.move_stack.pop()

        remove_piece = 1 << move.to_sq
        add_piece = 1 << move.from_sq
        move_xor = add_piece | remove_piece

        if self.rb_bb & remove_piece:
            self.rb_bb ^= move_xor
        elif self.pb_bb & remove_piece:
            self.pb_bb ^= move_xor
        elif self.sb_bb & remove_piece:
            self.sb_bb ^= move_xor
        elif self.rr_bb & remove_piece:
            self.rr_bb ^= move_xor
        elif self.pr_bb & remove_piece:
            self.pr_bb ^= move_xor
        elif self.sr_bb & remove_piece:
            self.sr_bb ^= move_xor

        if move.is_capture():
            if not self.turn:
                if move.capture == ROCK:
                    self.rb_bb ^= remove_piece
                elif move.capture == PAPER:
                    self.pb_bb ^= remove_piece
                elif move.capture == SCISSORS:
                    self.sb_bb ^= remove_piece
            else:
                if move.capture == ROCK:
                    self.rr_bb ^= remove_piece
                elif move.capture == PAPER:
                    self.pr_bb ^= remove_piece
                elif move.capture == SCISSORS:
                    self.sr_bb ^= remove_piece

        return move

    def peek(self) -> Move:
        return self.move_stack[-1]

    def color_board(self, color: Color) -> int:
        if color:
            return self.rb_bb | self.pb_bb | self.sb_bb
        else:
            return self.rr_bb | self.pr_bb | self.sr_bb

    def full_board(self) -> int:
        return self.rb_bb | self.pb_bb | self.sb_bb | self.rr_bb | self.pr_bb | self.sr_bb

    def is_draw(self) -> bool:
        return self.halfmove_clock >= 200 # assuming a move == 2 ply - need clarification

    def is_win(self, color: Color | None = None) -> bool:
        if color is None:
            return self.is_win(BLUE) or self.is_win(RED)

        if color:
            if self.color_board(BLUE) & BLUE_WIN_MASK:
                return True
        else:
            if self.color_board(RED) & RED_WIN_MASK:
                return True

        orig_turn = self.turn
        self.turn = not color
        try:
            if self.num_legal_moves() == 0:
                return True
        finally:
            self.turn = orig_turn

        return False

    def is_game_over(self) -> bool:
        return self.is_draw() or self.is_win()

    def full_hash(self) -> int:
        return (
            self.rb_bb
            | (self.pb_bb << 81)
            | (self.sb_bb << 162)
            | (self.rr_bb << 243)
            | (self.pr_bb << 324)
            | (self.sr_bb << 405)
            | (int(self.turn) << 486)
            | (self.halfmove_clock << 487)
        )

    def legal_moves(self) -> list[Move]: # to be improved
        if self.turn:
            self_rock = self.rb_bb
            self_paper = self.pb_bb
            self_scissors = self.sb_bb
            opp_rock = self.rr_bb
            opp_paper = self.pr_bb
            opp_scissors = self.sr_bb
        else:
            self_rock = self.rr_bb
            self_paper = self.pr_bb
            self_scissors = self.sr_bb
            opp_rock = self.rb_bb
            opp_paper = self.pb_bb
            opp_scissors = self.sb_bb
        free = (~self.full_board()) & FULL_BOARD
        moves = []
        for index in range(81):
            for piecetype, pieces in enumerate((self_rock, self_paper, self_scissors)):
                if pieces & (1 << index):
                    if piecetype == ROCK:
                        capture_free = free | opp_scissors
                    elif piecetype == PAPER:
                        capture_free = free | opp_rock
                    else:
                        capture_free = free | opp_paper
                    right = (index % 9 != 8)
                    left = (index % 9 != 0)
                    up = (index // 9 != 8)
                    down = (index // 9 != 0)

                    if right and ((1 << (index + 1)) & capture_free):
                        moves.append(Move(
                            index,
                            index + 1,
                            CAPTURES[piecetype] if ((1 << (index + 1)) & free) == 0 else None))
                    if left and ((1 << (index - 1)) & capture_free):
                        moves.append(Move(
                            index,
                            index - 1,
                            CAPTURES[piecetype] if ((1 << (index - 1)) & free) == 0 else None))
                    if down and ((1 << (index - 9)) & capture_free):
                        moves.append(Move(
                            index,
                            index - 9,
                            CAPTURES[piecetype] if ((1 << (index - 9)) & free) == 0 else None))
                    if up and ((1 << (index + 9)) & capture_free):
                        moves.append(Move(
                            index,
                            index + 9,
                            CAPTURES[piecetype] if ((1 << (index + 9)) & free) == 0 else None))
                    if right and down and ((1 << (index - 8)) & capture_free):
                        moves.append(Move(
                            index,
                            index - 8,
                            CAPTURES[piecetype] if ((1 << (index - 8)) & free) == 0 else None))
                    if right and up and ((1 << (index + 10)) & capture_free):
                        moves.append(Move(
                            index,
                            index + 10,
                            CAPTURES[piecetype] if ((1 << (index + 10)) & free) == 0 else None))
                    if left and down and ((1 << (index - 10)) & capture_free):
                        moves.append(Move(
                            index,
                            index - 10,
                            CAPTURES[piecetype] if ((1 << (index - 10)) & free) == 0 else None))
                    if left and up and ((1 << (index + 8)) & capture_free):
                        moves.append(Move(
                            index,
                            index + 8,
                            CAPTURES[piecetype] if ((1 << (index + 8)) & free) == 0 else None))

        return moves

    def num_legal_moves(self) -> int: # to be improved significantly
        return len(self.legal_moves())

    def as_line(self, starting_fen: str = STARTING_FEN, meafed: bool = False) -> str:
        line = ""
        test_b = Board(starting_fen)
        for n, move in enumerate(self.move_stack):
            if n % 2 == 0:
                line += f"{n // 2 + 1}. "
            if not meafed:
                line += f"{move.san(test_b)} "
            else:
                line += f"{move.san(test_b)[1:].upper()} "
            test_b.apply(move)
        return line

    def __str__(self) -> str:
        str_board = ""
        for rank in range(8, -1, -1):
            str_board += f"{rank + 1} "
            for file in range(9):
                index = file * 9 + rank
                mask = 1 << index
                if self.rb_bb & mask:
                    str_board += "R "
                elif self.pb_bb & mask:
                    str_board += "P "
                elif self.sb_bb & mask:
                    str_board += "S "
                elif self.rr_bb & mask:
                    str_board += "r "
                elif self.pr_bb & mask:
                    str_board += "p "
                elif self.sr_bb & mask:
                    str_board += "s "
                else:
                    str_board += ". "
            str_board += "\n"
        str_board += "  a b c d e f g h i"

        return str_board

    def __repr__(self) -> str:
        return f"Board(\"{self.fen()}\"), {self.move_stack}, {self.halfmove_stack}"
