import time

import chess
import chess.engine
import chess.pgn

from functions.eval import evaluate
from players.mcts_player import MCTSPlayer


def check_board_result(board):
    if not board.is_game_over():
        return None
    result = board.result()
    outcome = ''
    if result == '1-0':
        outcome = "Win - White"
    elif result == '0-1':
        outcome = "Win - Black"
    else:
        if board.is_stalemate():
            outcome = "Tie - Stalemate"
        if board.is_insufficient_material():
            outcome = "Tie - Insufficient Material"
        if board.is_seventyfive_moves():
            outcome = "Tie - 75 Moves"
        if board.is_fivefold_repetition():
            outcome = "Tie - Fivefold Repetition"
    return outcome


def max_depth(node):
    if len(node.children) == 0:
        return 0
    deepest_child = 0
    for child in node.children:
        child_depth = max_depth(child)
        if child_depth > deepest_child:
            deepest_child = child_depth

    return 1 + deepest_child


def play(player1, player2, player1_plays_first=True, verbose=False, board=None, **kwargs):
    engine = None

    if board is None:
        board = chess.Board()

    if player1_plays_first:
        white_player = player1
        black_player = player2
    else:
        white_player = player2
        black_player = player1

    if player1_plays_first:
        title1 = kwargs.get('title1', white_player.get_name())
        title2 = kwargs.get('title2', black_player.get_name())
    else:
        title2 = kwargs.get('title1', white_player.get_name())
        title1 = kwargs.get('title2', black_player.get_name())

    if verbose:
        engine = chess.engine.SimpleEngine.popen_uci('stockfish.exe')
        print('----- Game Start -----')
        print(board)

    start = time.time()
    while not board.is_game_over():
        if verbose:
            print()
            print(
                f"{title1 if board.turn else title2} - {'White' if board.turn else 'Black'} turn")
        if board.turn:
            move = white_player.get_next_move(board, verbose)
            if move:
                board.push(move)
        else:
            move = black_player.get_next_move(board, verbose)
            if move:
                board.push(move)
        if verbose:
            print(board)
            print(board.fen())
            print(f"Move made: {move}")
            print(f"Static eval: {evaluate(board, not board.turn)} ({'Black' if board.turn else 'White'})")
            print("Stockfish eval:", engine.analyse(board, chess.engine.Limit(time=0.01))['score'])
            if board.turn and type(black_player) == MCTSPlayer:
                print(f"Search tree depth: {max_depth(black_player.algo_model.tree)}")
            elif not board.turn and type(white_player) == MCTSPlayer:
                print(f"Search tree depth: {max_depth(white_player.algo_model.tree)}")
    end = time.time()

    outcome = check_board_result(board)
    results = [0, 0, 0]
    if outcome == "Win - White":
        if player1_plays_first:
            results[0] += 1
        else:
            results[1] += 1
    elif outcome == 'Win - Black':
        if player1_plays_first:
            results[1] += 1
        else:
            results[0] += 1
    else:
        results[2] += 1
    total_time = end - start
    if engine is not None:
        engine.close()

    return outcome, results, total_time


def compare_models(player1, player2, num_games=50, verbose=False, board=None, **kwargs):
    """
    Compare two models and print the results
    """
    title1 = kwargs.get("title1", player1.get_name())
    title2 = kwargs.get("title2", player2.get_name())
    results = {
        "Model 1": {"Wins": 0, "Simulations": 0, "Computing Time": 0},
        "Model 2": {"Wins": 0, "Simulations": 0, "Computing Time": 0},
        "Ties": 0,
        "Outcomes": {'Win - White': 0, 'Win - Black': 0, 'Tie - Stalemate': 0, 'Tie - Insufficient Material': 0,
                     'Tie - 75 Moves': 0, 'Tie - Fivefold Repetition': 0},
        "Total Time": 0,
    }
    outcomes = []

    # simulate the games
    for i in range(num_games):
        if board is not None:
            new_board = board.copy()
        else:
            new_board = None
        print(f"Simulating game {i + 1}/{num_games}...")
        if i % 2 == 0:
            outcome, result, total_time = play(player1, player2, player1_plays_first=True, verbose=verbose,
                                               board=new_board, title1=title1, title2=title2)
        else:  # player2 plays white
            outcome, result, total_time = play(player1, player2, player1_plays_first=False, verbose=verbose,
                                               board=new_board, title1=title1, title2=title2)
        player1.reset()
        player2.reset()

        results["Model 1"]["Wins"] += result[0]
        results["Model 2"]["Wins"] += result[1]
        results["Ties"] += result[2]
        results["Total Time"] += total_time
        outcomes.append(outcome)

        print(
            f'{title1} wins: {results["Model 1"]["Wins"]} | {title2} wins: {results["Model 2"]["Wins"]} | Ties: {results["Ties"]} ')
    # process the results
    for o in outcomes:
        results['Outcomes'][o] += 1
    if type(player1) != MCTSPlayer:
        player1.close()
        del results["Model 1"]["Simulations"]
        del results["Model 1"]["Computing Time"]
    else:
        stats = player1.get_stats()
        results['Model 1']['Simulations'] += stats['total_simulations']
        results['Model 1']['Computing Time'] += stats['total_time']
    if type(player2) != MCTSPlayer:
        player2.close()
        del results["Model 2"]["Simulations"]
        del results["Model 2"]["Computing Time"]
    else:
        stats = player2.get_stats()
        results['Model 2']['Simulations'] += stats['total_simulations']
        results['Model 2']['Computing Time'] += stats['total_time']

    print("----- Statistics -----")
    print(f"Average time per game: {results['Total Time'] / num_games:.2f} s")
    print("Game Results:")
    print(
        f"\t{title1} - Wins: {results['Model 1']['Wins']} | Win Percentage: {results['Model 1']['Wins'] / num_games:.2%}")
    if type(player1) == MCTSPlayer:
        print(
            f"\t{title1} - Total Simulations: {results['Model 1']['Simulations']} | Total Computing Time: {results['Model 1']['Computing Time']:.2f} | Simulations per sec: {results['Model 1']['Simulations'] / results['Model 1']['Computing Time']:.2f} sims/sec")
    print(
        f"\t{title2} - Wins: {results['Model 2']['Wins']} | Win Percentage: {results['Model 2']['Wins'] / num_games:.2%}")
    if type(player2) == MCTSPlayer:
        print(
            f"\t{title2} - Total Simulations: {results['Model 2']['Simulations']} | Total Computing Time: {results['Model 2']['Computing Time']:.2f} | Simulations per sec: {results['Model 2']['Simulations'] / results['Model 2']['Computing Time']:.2f} sims/sec")
    print(f"\tTies: {results['Ties']} | Tie Percentage: {results['Ties'] / num_games:.2%}")
    print()
    print(f"Outcome occurrences:")
    for key, val in results['Outcomes'].items():
        print(f"\t{key}: {val}")
    print()
