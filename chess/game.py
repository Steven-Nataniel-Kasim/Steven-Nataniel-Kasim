import chess
import json
import os
import sys
import re

REPO = "Steven-Nataniel-Kasim/Steven-Nataniel-Kasim"
STATE_FILE = "chess/state.json"
README_FILE = "README.md"

PIECE_UNICODE = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "fen": chess.STARTING_FEN,
        "move_count": 0,
        "last_move": None,
        "last_player": None,
        "history": []
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def render_board(board):
    lines = []
    lines.append('|   | a | b | c | d | e | f | g | h |')
    lines.append('|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|')
    for rank in range(7, -1, -1):
        cells = [f'**{rank + 1}**']
        for file in range(8):
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            if piece:
                cells.append(PIECE_UNICODE[piece.symbol()])
            else:
                cells.append('·')
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)

def generate_move_links(board):
    moves = sorted(board.legal_moves, key=lambda m: m.uci())
    links = []
    for move in moves:
        uci = move.uci()
        san = board.san(move)
        url = (
            f"https://github.com/{REPO}/issues/new?"
            f"title=chess%7C{uci}&"
            f"body=Playing+move:+{san}"
        )
        links.append(f'[`{san}`]({url})')
    return links

def build_chess_section(board, state, move_links):
    turn = "⬜ White" if board.turn == chess.WHITE else "⬛ Black"
    status_line = ""
    if board.is_checkmate():
        winner = "⬛ Black" if board.turn == chess.WHITE else "⬜ White"
        status_line = f"\n\n🏆 **Checkmate! {winner} wins!** [Start new game](https://github.com/{REPO}/issues/new?title=chess%7Cnew&body=Start+a+new+game!)"
    elif board.is_stalemate():
        status_line = f"\n\n🤝 **Stalemate! Draw.** [Start new game](https://github.com/{REPO}/issues/new?title=chess%7Cnew&body=Start+a+new+game!)"
    elif board.is_check():
        status_line = f"\n\n⚠️ **{turn} is in CHECK!**"

    last_move_info = ""
    if state.get('last_move') and state.get('last_player'):
        last_move_info = f" | Last move: `{state['last_move']}` by @{state['last_player']}"

    moves_display = ""
    if move_links:
        moves_display = f"<details>\n<summary>🎯 <b>Click to make a move</b></summary>\n<br/>\n\n{' · '.join(move_links)}\n\n</details>"

    board_str = render_board(board)

    section = (
        f"<!-- CHESS:START -->\n"
        f"<div align=\"center\">\n\n"
        f"### ♟️ Community Chess\n\n"
        f"> Play chess directly in my README! Pick a move below to open an issue.\n\n"
        f"{board_str}\n\n"
        f"**Turn:** {turn} | **Move:** {state['move_count']}{last_move_info}"
        f"{status_line}\n\n"
        f"{moves_display}\n\n"
        f"</div>\n"
        f"<!-- CHESS:END -->"
    )
    return section

def update_readme(chess_section):
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'<!-- CHESS:START -->.*?<!-- CHESS:END -->'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, chess_section, content, flags=re.DOTALL)
    else:
        content += '\n\n' + chess_section
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def make_move(uci_str, player="unknown"):
    state = load_state()
    board = chess.Board(state['fen'])
    try:
        move = chess.Move.from_uci(uci_str)
    except ValueError:
        return False
    if move not in board.legal_moves:
        return False
    san = board.san(move)
    board.push(move)
    state['fen'] = board.fen()
    state['move_count'] += 1
    state['last_move'] = san
    state['last_player'] = player
    state['history'].append({"move": uci_str, "san": san, "player": player})
    save_state(state)
    move_links = generate_move_links(board) if not board.is_game_over() else []
    chess_section = build_chess_section(board, state, move_links)
    update_readme(chess_section)
    return True

def new_game():
    state = {"fen": chess.STARTING_FEN, "move_count": 0, "last_move": None, "last_player": None, "history": []}
    board = chess.Board()
    save_state(state)
    move_links = generate_move_links(board)
    chess_section = build_chess_section(board, state, move_links)
    update_readme(chess_section)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    action = sys.argv[1]
    if action == "new":
        success = new_game()
    elif action == "move":
        uci = sys.argv[2]
        player = sys.argv[3] if len(sys.argv) >= 4 else "unknown"
        success = make_move(uci, player)
    else:
        sys.exit(1)
    sys.exit(0 if success else 1)
