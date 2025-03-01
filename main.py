import chess
import chess.pgn
import requests
from fastapi import FastAPI

app = FastAPI()

LICHESS_API_URL = "https://lichess.org/api/cloud-eval"

@app.get("/")
def read_root():
    return {"message": "Chess Analysis API is running!"}



def parse_pgn(file_path):
    """Reads a PGN file and extracts moves."""
    try:
        with open(file_path, 'r', encoding='utf-8') as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                raise ValueError("Invalid PGN file or empty content.")

            board = game.board()
            fen_positions = []

            for move in game.mainline_moves():
                board.push(move)  # Play the move on the board
                fen_positions.append(board.fen())  # Store FEN after each move

            return fen_positions

    except Exception as e:
        print(f"Error: {e}")
        return None
    

def analyze_position(fen):
    """Send FEN position to Lichess API for analysis."""
    try:
        response = requests.get(f"{LICHESS_API_URL}?fen={fen}")
        
        if response.status_code == 200:
            data = response.json()
            best_moves = data.get("pvs", [{}])[0].get("moves", "").split()
            best_move = best_moves[0] if best_moves else "Unknown"

            eval_score = data.get("pvs", [{}])[0].get("cp", None)
            mate = data.get("pvs", [{}])[0].get("mate", None)

            return {
                "fen": fen,
                "best_move": best_move,
                "eval": eval_score,
                "mate": mate,
            }
        else:
            print(f"Error: Lichess API returned {response.status_code}")
            return None

    except Exception as e:
        print(f"Request failed: {e}")
        return None

def evaluate_position(eval_score, mate):
    """Convert Stockfish evaluation into user-friendly feedback."""
    if mate is not None:
        return f"Checkmate in {mate} moves!" if mate > 0 else f"Opponent has checkmate in {-mate} moves!"

    if eval_score == "N/A":
        return "No evaluation available."

    if eval_score > 100:
        return "Winning position! Keep up the attack!"
    elif 50 < eval_score <= 100:
        return "You have a strong advantage."
    elif -50 <= eval_score <= 50:
        return "Game is balanced."
    elif -100 <= eval_score < -50:
        return "You're in a difficult position. Consider defending."
    else:
        return "Losing position. Try finding a counterplay!"

    
def analyze_pgn(file_path):
    """Parse PGN and analyze each position."""
    fen_positions = parse_pgn(file_path)
    if not fen_positions:
        print("No valid positions found.")
        return None

    results = []
    for i, fen in enumerate(fen_positions):
        print(f"Analyzing move {i+1}/{len(fen_positions)}...")
        analysis = analyze_position(fen)
        if analysis:
            formatted_eval = evaluate_position(analysis["eval"], analysis["mate"])
            results.append({
                "move_number": i + 1,
                "best_move": analysis["best_move"],
                "evaluation": formatted_eval
            })

    return results

if __name__ == "__main__":
    file_path = "example.pgn"  # Replace with your actual PGN file
    analysis_results = analyze_pgn(file_path)

    if analysis_results:
        print("\n📊 Full Game Analysis:")
        for result in analysis_results:
            print(f"\n🔹 Move {result['move_number']}:")
            print(f"💡 Best Move: {result['best_move']}")
            print(f"📉 Evaluation: {result['evaluation']}")
    else:
        print("Analysis failed.")

