#!/usr/bin/env python3
import random
import sys
import time
from collections import OrderedDict
from typing import Generator, List


class IllegalMoveException(Exception):
    """
    Thrown when a player tries to carry out an illegal move
    """
    pass


class DuplicateMoveException(Exception):
    """
    Thrown when a player tries to carry out an illegal move
    """
    pass


def main():
    game = NoughtsAndCrosses()
    game.play()


class State:
    __slots__ = ['moves', 'score', 'turn', 'winner', 'players', 'tokens']

    def __init__(self, player1, player2):
        """
        Setup the initial state
        """
        self.players = [player1, player2]
        self.tokens = {
            ' ': ' ',
            player1: 'X',
            player2: 'O',
        }
        self.score = {
            player1: 0,
            player2: 0,
        }
        self.moves = None
        self.winner = None
        self.turn = ''
        self.reset()

    def reset(self) -> None:
        """
        Resets the game maintaining the score
        """
        self.moves = OrderedDict()
        self.turn = random.choice(self.players)
        self.winner = None

    def set_move(self, position: int) -> None:
        """
        Sets the position played

        :param position: The position the player has set
        """
        if position not in range(1, 10):
            raise IllegalMoveException
        elif position in self.moves:
            raise DuplicateMoveException
        self.moves[position] = self.turn
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]

    def finished(self) -> bool:
        """
        Check if we have a winner

        :return: True if the game finished (someone won or no moves available)
        """
        win_lines = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9],
            [1, 5, 9],
            [7, 5, 3],
        ]
        for win_line in win_lines:
            if (
                    self.moves.get(win_line[0], '') and
                    (
                            self.moves.get(win_line[0], '') ==
                            self.moves.get(win_line[1], '') ==
                            self.moves.get(win_line[2], '')
                    )
            ):
                self.winner = self.moves[next(reversed(self.moves))]
                self.score[self.winner] += 1
        if self.winner or len(self.moves) == 9:
            return True
        return False

    def _set_winner(self, winner: str) -> None:
        """
        Updates the scoreboard

        :param winner: The winner of the current game
        """
        self.score[winner] += 1
        self.winner = winner

    def compile_board(self, moves=None) -> List[List[str]]:
        """
        Provides a list of each line on the board

        :param moves: The list of moves to view.

        :return: List containing a list of each value on a line
        """
        if not moves:
            moves = self.moves
        board = []
        current_line = []
        for itr in range(1, 10):
            current_line.append(
                self.tokens[moves.get(itr, ' ')]
            )
            if itr % 3 == 0 and current_line:
                board.append(current_line)
                current_line = []
        board.append(current_line)
        return board

    def move_replay(self) -> Generator[List[List[str]], None, None]:
        """
        Generator to allow iteration of the moves to show a replay

        :return: List containing a list of each value on a line
        """
        current_moves = OrderedDict()
        for move in self.moves:
            current_moves[move] = self.moves[move]
            yield self.compile_board(current_moves)

    @property
    def player1(self) -> str:
        return self.players[0]

    @property
    def player2(self) -> str:
        return self.players[1]

    @property
    def player1_score(self) -> int:
        return self.score[self.players[0]]

    @property
    def player2_score(self) -> int:
        return self.score[self.players[1]]


class NoughtsAndCrosses:
    def __init__(self):
        self.state = None
        self.set_plays()

    def set_plays(self) -> None:
        """
        Setsup the new plays
        """
        player1 = self._get_input('What is the name of player 1?')
        player2 = self._get_input('What is the name of player 2?')
        self.state = State(player1, player2)

    def play(self):
        self._display_message('Input a square from 1-9 to move.')
        while not self.state.finished():
            try:
                self._display_message(self.state.turn + ' to play: ')
                sys.stdout.flush()
                action = sys.stdin.readline()
                self.state.set_move(int(action))
                self.show_board(self.state.compile_board())
            except KeyboardInterrupt:
                self._display_message("Don't leave meeeeee..............")
            except (IllegalMoveException, ValueError):
                self._display_error(
                    'That is not a valid move, '
                    'try again selecting a number between 1 and 9'
                )
            except DuplicateMoveException:
                self._display_error(
                    'Someone has already occupied this space, '
                    'please choose an empty space'
                )
        self.display_result()

        replay = self._get_input('Would you like to view a replay?')
        if replay.lower() == 'y':
            self.show_replay()

        play_again = self._get_input('Would you like to play again?')
        if play_again.lower() == 'y':
            self.state.reset()
            self.play()

        self._display_message(
            'Fine then, go, see if I care. Ok wait, please..., come back!'
        )

    def show_replay(self) -> None:
        """
        Displays the replay
        """
        for move in self.state.move_replay():
            self.show_board(move)
            time.sleep(1)

    @staticmethod
    def show_board(board) -> None:
        """
        Outputs the given board

        :param board: List of List of strings to output the play board
        """
        for line in board:
            print('|'.join(line))

    def display_result(self) -> None:
        """
        Displays the result of the game.
        """
        winner = self.state.winner
        if winner:
            self._display_message(winner + ' wins!')
        else:
            self._display_message('Draw')

        self._display_message(
            f'\n{self.state.player1} has {self.state.player1_score} wins'
        )
        self._display_message(
            f'{self.state.player2} has {self.state.player2_score} wins\n'
        )

    @staticmethod
    def _get_input(question: str) -> str:
        """
        Ask the user a question and get a response

        :param question: Question requiring an answer

        :return: Users response
        """
        print(question)
        sys.stdout.flush()
        user_input = sys.stdin.readline()
        user_input = user_input.strip()
        return user_input

    @staticmethod
    def _display_error(message: str) -> None:
        """
        Output text as an error

        :param message: Message to be output
        """
        print()
        print(message, end='\n\n')

    @staticmethod
    def _display_message(message: str) -> None:
        """
        Output text as a message

        :param message: Message to be output
        """
        print(message)


if __name__ == '__main__':
    main()
