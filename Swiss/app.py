from flask import Flask, render_template, request, redirect, url_for, session
import math
import time

from compute import score_update, pairing_graph, final_tie_breaker

app = Flask(__name__, template_folder='template')

app.secret_key = "your_secret_key"

def init_session():
    session.setdefault("player_list", [])
    session.setdefault("player_scores", {})
    session.setdefault("match_win_percentage", {})
    session.setdefault("omw", {})
    session.setdefault("oomw", {})
    session.setdefault("pairings", [])
    session.setdefault("pairing_history", {})
    session.setdefault("match_result_history", {})
    session.setdefault("player_tie_breakers", {})
    session.setdefault("round_number", 1)
    session.setdefault("number_of_rounds", 0)
    session.setdefault("rounds", {}) 
    # Timer related session variables
    session.setdefault("timer_duration", 3000)  
    session.setdefault("timer_start", None)
    session.setdefault("timer_paused", True)
    session.setdefault("timer_remaining_paused", None)

@app.route('/', methods=['GET'])
def index():
    init_session()
    return render_template(
        'index.html',
        player_list=session["player_list"],
        number_of_rounds=session["number_of_rounds"]
    )

@app.route('/add_player', methods=['POST'])
def add_player():
    init_session()
    name = request.form.get('player_name', '').strip()
    if name and name not in session["player_list"]:
        session["player_list"].append(name)
        session["player_scores"][name] = 0
        session["match_win_percentage"][name] = 0.0
        session["omw"][name] = 0.0
        session["oomw"][name] = 0.0
        session["pairing_history"][name] = []
        session["match_result_history"][name] = []
        session["player_tie_breakers"][name] = []
        session["number_of_rounds"] = math.ceil(math.log2(len(session["player_list"]))) if len(session["player_list"]) > 1 else 0
        
        session.modified = True
    return {'success': True, 'player_list': session["player_list"], 'count': len(session["player_list"]), 'number_of_rounds': session["number_of_rounds"]}

@app.route('/remove_player', methods=['POST'])
def remove_player():
    init_session()
    name = request.form.get('player_name')
    if name in session["player_list"]:
        session["player_list"].remove(name)
        session["player_scores"].pop(name, None)
        session["match_win_percentage"].pop(name, None)
        session["omw"].pop(name, None)
        session["oomw"].pop(name, None)
        session["pairing_history"].pop(name, None)
        session["match_result_history"].pop(name, None)
        session["player_tie_breakers"].pop(name, None)
        session["number_of_rounds"] = math.ceil(math.log2(len(session["player_list"]))) if len(session["player_list"]) > 1 else 0
        
        session.modified = True
        
    return {'success': True, 'player_list': session["player_list"], 'count': len(session["player_list"]), 'number_of_rounds': session["number_of_rounds"]}

@app.route('/remove_all', methods=['POST'])
def remove_all():
    init_session()
    session["player_list"].clear()
    session["player_scores"].clear()
    session["match_win_percentage"].clear()
    session["omw"].clear()
    session["oomw"].clear()
    session["pairings"].clear()
    session["pairing_history"].clear()
    session["match_result_history"].clear()
    session["player_tie_breakers"].clear()
    session["round_number"] = 1
    session["number_of_rounds"] = 0
    return {'success': True, 'player_list': session["player_list"], 'count': len(session["player_list"]), 'number_of_rounds': session["number_of_rounds"]}

@app.route('/start_tournament', methods=['GET', 'POST'])
def start_tournament():
    init_session()

    player_list = session["player_list"]
    player_scores = session["player_scores"]
    match_win_percentage = session["match_win_percentage"]
    omw = session["omw"]
    oomw = session["oomw"]
    match_result_history = session["match_result_history"]
    round_number = session["round_number"]
    number_of_rounds = session["number_of_rounds"]
    
    results = {}

    # Convert pairing_history list→set
    pairing_history = {k: set(v) for k, v in session["pairing_history"].items()}

    # Pairings may not exist yet
    pairings = session.get("pairings", [])
    bye_player = session.get("bye_player")  

    if request.method == 'POST':
        # Process results from the form
        session["timer_start"] = None
        session["timer_paused"] = True
        for p1, p2 in pairings:
            winner = request.form.get(f"{p1}_vs_{p2}")
            results[(p1, p2)] = winner
        # print("Here are the results:", results)
        # print("Here are the pairings:", pairings)
        player_scores, match_win_percentage, round_number, match_result_history = score_update(
            pairings, player_scores, match_win_percentage, round_number, match_result_history, results, player_list, 
            match_win_percentage, omw, oomw, pairing_history
        )
        
                # Save updated values back to session
        session["player_scores"] = player_scores
        session["match_win_percentage"] = match_win_percentage
        session["round_number"] = round_number
        session["match_result_history"] = match_result_history
        
        if round_number > number_of_rounds:
            return redirect(url_for('tournament_results'))        
        
        pairings, bye_player, pairing_history = pairing_graph(
            player_list, player_scores, pairing_history, match_result_history
        )
        
        session["pairings"] = pairings
        session["bye_player"] = bye_player
        
        safe_results = {f"{p1}__vs__{p2}": w for (p1, p2), w in results.items()}
        
        session["rounds"][str(round_number)] = {
            "pairings": pairings,
            "bye_player": bye_player,
            "prev_results": safe_results
        }
        
        print("Session rounds data:", session["rounds"])
        
        # Convert set→list for session
        session["pairing_history"] = {k: list(v) for k, v in pairing_history.items()}
        
        session.modified = True
               
    if round_number == 1 and not session.get("pairings"):
        
        session["timer_start"] = None
        session["timer_paused"] = True
        
        pairings, bye_player, pairing_history = pairing_graph(
            player_list, player_scores, pairing_history, match_result_history
        )
        
        session["pairings"] = pairings
        session["bye_player"] = bye_player
        
        safe_results = {f"{p1}__vs__{p2}": w for (p1, p2), w in results.items()}
        
        session["rounds"][str(round_number)] = {
            "pairings": pairings,
            "bye_player": bye_player,
            "prev_results": safe_results
        }

        session["pairing_history"] = {k: list(v) for k, v in pairing_history.items()}
        session.modified = True

    pairing_history = {k: set(v) for k, v in session["pairing_history"].items()}
    
    player_tie_breakers = session.get("player_tie_breakers", {})
    
    player_tie_breakers = final_tie_breaker(player_list, player_scores, omw, oomw, player_tie_breakers, match_result_history)
    rankings = sorted(player_list, key=lambda x: (-player_tie_breakers[x], x))
    
    rankings_data = []
    for rank, name in enumerate(rankings, start=1):
        entry = {
            'rank': rank,
            'name': name,
            'score': player_scores.get(name, 0),
            'omw': omw.get(name, 0),
            'oomw': oomw.get(name, 0),
            'tie': player_tie_breakers.get(name, 0)
        }
        rankings_data.append(entry)
        print(f"{rank}. {name} (Score: {entry['score']}, OMW: {entry['omw']}, OOMW: {entry['oomw']}, tie-breaker: {entry['tie']})")

    return render_template('start_tournament.html',
                           round_number=session["round_number"],
                           pairings=session["pairings"],
                           bye_player=session.get("bye_player"),
                           prev_round_data=session["rounds"],
                           player_scores=player_scores,
                           match_result_history=match_result_history,
                           match_win_percentage=match_win_percentage,
                           omw=omw,
                           oomw=oomw,
                           number_of_rounds=number_of_rounds,
                           player_tie_breakers=player_tie_breakers,
                           rankings=rankings,
                           rankings_data=rankings_data,
                           pairing_history=pairing_history,
                           timer_duration=session["timer_duration"],
                           timer_start=session["timer_start"],
                           timer_paused=session["timer_paused"])
    
@app.route('/tournament_results', methods=['GET', 'POST'])
def tournament_results():
    init_session()
    
    # Load state from session
    player_list = session["player_list"]
    player_scores = session["player_scores"]
    match_win_percentage = session["match_win_percentage"]
    omw = session["omw"]
    oomw = session["oomw"]
    match_result_history = session["match_result_history"]
    number_of_rounds = session["number_of_rounds"]

    # Convert pairing_history from list→set for algorithms
    pairing_history = {k: set(v) for k, v in session["pairing_history"].items()}
    
    player_tie_breakers = session.get("player_tie_breakers", {})
    
    player_tie_breakers = final_tie_breaker(player_list, player_scores, omw, oomw, player_tie_breakers, match_result_history)
    rankings = sorted(player_list, key=lambda x: (-player_tie_breakers[x], x))
    
    rankings_data = []
    for rank, name in enumerate(rankings, start=1):
        entry = {
            'rank': rank,
            'name': name,
            'score': player_scores.get(name, 0),
            'omw': omw.get(name, 0),
            'oomw': oomw.get(name, 0),
            'tie': player_tie_breakers.get(name, 0)
        }
        rankings_data.append(entry)
        print(f"{rank}. {name} (Score: {entry['score']}, OMW: {entry['omw']}, OOMW: {entry['oomw']}, tie-breaker: {entry['tie']})")
    
    return render_template('tournament_results.html',
                           player_scores=player_scores,
                           match_result_history=match_result_history,
                           match_win_percentage=match_win_percentage,
                           omw=omw,
                           oomw=oomw,
                           number_of_rounds=number_of_rounds,
                           player_tie_breakers=player_tie_breakers,
                           rankings=rankings,
                           rankings_data=rankings_data,
                           pairing_history=pairing_history)

@app.route('/reset_tournament', methods=['POST'])
def reset_tournament():
    init_session()
    session["player_list"].clear()
    session["player_scores"].clear()
    session["match_win_percentage"].clear()
    session["omw"].clear()
    session["oomw"].clear()
    session["pairings"].clear()
    session["pairing_history"].clear()
    session["match_result_history"].clear()
    session["player_tie_breakers"].clear()
    session["round_number"] = 1
    session["number_of_rounds"] = 0
    return redirect(url_for('index'))

@app.route('/set_timer_duration', methods=['POST'])
def set_timer_duration():
    init_session()
    duration = request.form.get('duration', type=int)
    if duration and duration > 0:
        session["timer_duration"] = duration
        session.modified = True
    return {'success': True, 'duration': session["timer_duration"]}

@app.route('/start_timer', methods=['POST'])
def start_timer():
    init_session()
    if session["timer_start"] is None:
        session["timer_start"] = time.time()
    elif session["timer_remaining_paused"] is not None:
        # Adjust start time based on remaining time when resuming
        session["timer_start"] = time.time() - (session["timer_duration"] - session["timer_remaining_paused"])
        session["timer_remaining_paused"] = None
    session["timer_paused"] = False
    session.modified = True
    return {'success': True, 'start_time': session["timer_start"], 'paused': session["timer_paused"]}

@app.route('/pause_timer', methods=['POST'])
def pause_timer():
    init_session()
    if session["timer_start"] and not session["timer_paused"]:
        # Calculate remaining time at pause
        current_time = time.time()
        elapsed = current_time - session["timer_start"]
        session["timer_remaining_paused"] = max(0, session["timer_duration"] - elapsed)
    session["timer_paused"] = True
    session.modified = True
    return {'success': True, 'paused': session["timer_paused"]}

@app.route('/reset_timer', methods=['POST'])
def reset_timer():
    init_session()
    session["timer_start"] = None
    session["timer_paused"] = True
    session["timer_remaining_paused"] = None  # Clear paused remaining time
    session.modified = True
    return {'success': True, 'start_time': session["timer_start"], 'paused': session["timer_paused"]}

@app.route('/get_timer_state', methods=['GET'])
def get_timer_state():
    init_session()
    current_time = time.time()
    
    if session["timer_paused"] and session["timer_remaining_paused"] is not None:
        # When paused, show the stored remaining time
        remaining = session["timer_remaining_paused"]
    elif session["timer_start"] and not session["timer_paused"]:
        # When running, calculate remaining time
        elapsed = current_time - session["timer_start"]
        remaining = max(0, session["timer_duration"] - elapsed)
    else:
        # When not started or reset, show full duration
        remaining = session["timer_duration"]
    
    return {
        'remaining': int(remaining),
        'duration': session["timer_duration"],
        'paused': session["timer_paused"],
        'started': session["timer_start"] is not None
    }

if __name__ == '__main__':
    app.run(debug=True)