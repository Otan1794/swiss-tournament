import networkx as nx
import random

def pairing_graph(round_number, player_list, player_scores, pairing_history, match_result_history):
    """
    Returns pairings and bye player using NetworkX matching.
    - pairing_history: dict of sets {player: {previous_opponents}}
    """
    players = player_list.copy()
    pairings = []
    bye_player = None

    # If odd number of players, assign a bye to the lowest scoring player who hasn't had a bye
    if len(players) % 2 != 0:
        sorted_players = sorted(players, key=lambda x: (player_scores[x], random.random()))
        for p in sorted_players:
            if 'BYE' not in pairing_history.get(p, set()):
                bye_player = p
                players.remove(p)
                player_scores[p] += 3  # award point for bye
                pairing_history.setdefault(p, set()).add('BYE')
                match_result_history[p].append("W (BYE)")
                break

    # Build graph
    G = nx.Graph()
    for i, p1 in enumerate(players):
        for p2 in players[i+1:]:
            # Avoid rematches
            if p2 not in pairing_history.get(p1, set()):
                # Edge weight could be negative score difference to prioritize similar scores
                weight = -abs(player_scores[p1] - player_scores[p2])
                G.add_edge(p1, p2, weight=weight)

    # Compute matching
    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)

    # Convert matching set of tuples to a list
    for p1, p2 in matching:
        pairings.append((p1, p2))
        # Add to pairing history
        pairing_history.setdefault(p1, set()).add(p2)
        pairing_history.setdefault(p2, set()).add(p1)

    return pairings, bye_player, pairing_history


def score_update(pairings, player_scores, mwp, round_number, match_result_history, results, player_list, match_win_percentage, omw, oomw, pairing_history):
    
    for name in player_list:
        opponents = {opp for opp in pairing_history[name] if opp != "BYE"}
        if opponents:
            omw[name] = round(sum(match_win_percentage[opp] for opp in opponents) / len(opponents), 1)
            oomw[name] = round(sum(omw[opp] for opp in opponents) / len(opponents), 1) if opponents else 0.0
    #print("Result in compute.py", results)
    for p1, p2 in pairings:
        result = results.get((p1, p2))
        #print("Result in compute.py", result)
        if result not in ['1', '2', 'D']: #limit what can be inputted in UI
            print("Invalid input. Please enter 1, 2, or D.")
            continue
        if result == '1':
            player_scores[p1] += 3
            match_result_history[p1].append('W')
            match_result_history[p2].append('L')    
        elif result == '2':
            player_scores[p2] += 3
            match_result_history[p2].append('W')
            match_result_history[p1].append('L')
        else:
            match_result_history[p1].append("L (DRAW)")
            match_result_history[p2].append("L (DRAW)")
        for p in (p1, p2):
            mwp[p] = round(player_scores[p] / 3 / round_number * 100, 1)
            
    round_number += 1
    return player_scores, mwp, round_number, match_result_history

def final_tie_breaker(player_list, player_scores, omw, oomw, player_tie_breakers, match_result_history):
    
    for name in player_list:
        loss_rounds = [i + 1 for i, result in enumerate(match_result_history[name]) if result == 'L' or result == "L (DRAW)"]
        score_str = f"{player_scores[name]:02d}"
        #print(name, "Score String:", score_str)
        omw_str = f"{min(int(omw[name]*10), 999):03d}"
        #print(name, "OMW String:", omw_str)
        oomw_str = f"{min(int(oomw[name]*10), 999):03d}"
        #print(name, "OOMW String:", oomw_str)
        sslr = sum(r ** 2 for r in loss_rounds)
        sslr_str = f"{sslr:03d}"
        #print(name, "SSLR String:", sslr_str)
        player_tie_breakers[name] = int(score_str + omw_str + oomw_str + sslr_str)
    
    return player_tie_breakers

