from flask import Flask, render_template, request, redirect, url_for
import math

from compute import score_update, pairing, final_tie_breaker

app = Flask(__name__, template_folder='template')

player_list = []
player_scores = {}
match_win_percentage = {}
omw = {}
oomw = {}
pairings = []
pairing_history = {}
match_result_history = {}
player_tie_breakers = {}
round_number = 1
number_of_rounds = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    global number_of_rounds
    if request.method == 'POST':
        # handle add player via server form
        name = request.form.get('player_name', '').strip()
        if name and name not in player_list:
            player_list.append(name)
            player_scores[name] = 0
            match_win_percentage[name] = 0.0
            omw[name] = 0.0
            oomw[name] = 0.0
            pairing_history[name] = []
            match_result_history[name] = []
            player_tie_breakers[name] = []
            number_of_rounds = math.ceil(math.log2(len(player_list))) if len(player_list) > 1 else 0
        return redirect(url_for('index'))

    return render_template('index.html',
                           player_list=player_list,
                           number_of_rounds=number_of_rounds)

@app.route('/add_player', methods=['POST'])
def add_player():
    global number_of_rounds
    data = request.get_json()
    name = data.get('player_name','').strip()
    if name and name not in player_list:
        player_list.append(name)
        player_scores[name] = 0
        match_win_percentage[name] = 0.0
        omw[name] = 0.0
        oomw[name] = 0.0
        pairing_history[name] = []
        match_result_history[name] = []
        player_tie_breakers[name] = []
        number_of_rounds = math.ceil(math.log2(len(player_list))) if len(player_list) > 1 else 0
    return {'player_list': player_list, 'number_of_rounds': number_of_rounds}

# existing remove_player route should remain as POST form action
@app.route('/remove_player', methods=['POST'])
def remove_player():
    global number_of_rounds
    name = request.form.get('player_name')
    if name in player_list:
        player_list.remove(name)
        player_scores.pop(name, None)
        match_win_percentage.pop(name, None)
        omw.pop(name, None)
        oomw.pop(name, None)
        pairing_history.pop(name, None)
        match_result_history.pop(name, None)
        player_tie_breakers.pop(name, None)
        number_of_rounds = math.ceil(math.log2(len(player_list))) if len(player_list) > 1 else 0
    return redirect(url_for('index'))

@app.route('/remove_all', methods=['POST'])
def remove_all():
    global player_list, player_scores, match_win_percentage, omw, oomw, pairings, pairing_history, match_result_history, player_tie_breakers, round_number, number_of_rounds
    player_list.clear()
    player_scores.clear()
    match_win_percentage.clear()
    omw.clear()
    oomw.clear()
    pairings.clear()
    pairing_history.clear()
    match_result_history.clear()
    player_tie_breakers.clear()
    round_number = 1
    number_of_rounds = 0
    return redirect(url_for('index'))

@app.route('/start_tournament', methods=['GET', 'POST'])
def start_tournament():
    global round_number, pairings, player_scores, pairing_history, match_result_history, omw, oomw, match_win_percentage, bye_player
    player_count = len(player_list)
    print(player_list)
        
    if request.method == 'POST':
        # Process results from the form
        results = {}
        for p1, p2 in pairings:
            winner = request.form.get(f"{p1}_vs_{p2}")
            results[(p1, p2)] = winner
        #print("Here are the results:", results)
        player_scores, match_win_percentage, round_number, match_result_history = score_update(
            pairings, player_scores, match_win_percentage, round_number, match_result_history, results
        )
        
        if round_number > number_of_rounds:
            return redirect(url_for('tournament_results'))        
        
        player_scores, pairing_history, pairings, match_result_history, omw, oomw, bye_player = pairing(
            round_number, player_list, player_scores, pairing_history, pairings, player_count,
            match_win_percentage, match_result_history, omw, oomw
        )
               
    if round_number == 1:
        player_scores, pairing_history, pairings, match_result_history, omw, oomw, bye_player = pairing(
            round_number, player_list, player_scores, pairing_history, pairings, player_count,
            match_win_percentage, match_result_history, omw, oomw
        )

    return render_template('start_tournament.html',
                           round_number=round_number,
                           pairings=pairings,
                           bye_player=bye_player)
    
@app.route('/tournament_results', methods=['GET', 'POST'])
def tournament_results():
    global number_of_rounds, player_scores, match_result_history, match_win_percentage, omw, oomw, player_tie_breakers, rankings
    
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
                           rankings_data=rankings_data)

@app.route('/reset_tournament', methods=['POST'])
def reset_tournament():
    global player_list, player_scores, match_win_percentage, omw, oomw, pairings, pairing_history, match_result_history, player_tie_breakers, round_number, number_of_rounds
    player_list.clear()
    player_scores.clear()
    match_win_percentage.clear()
    omw.clear()
    oomw.clear()
    pairings.clear()
    pairing_history.clear()
    match_result_history.clear()
    player_tie_breakers.clear()
    round_number = 1
    number_of_rounds = 0
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)