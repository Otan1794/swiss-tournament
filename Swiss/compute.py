import random

def find_pairings(unpaired, pairing_history, current_pairs):
    if not unpaired:
        return current_pairs
    p1 = unpaired[0]
    for idx in range(1, len(unpaired)):
        p2 = unpaired[idx]
        if p2 not in pairing_history[p1]:
            next_unpaired = unpaired[1:idx] + unpaired[idx+1:]
            result = find_pairings(next_unpaired, pairing_history, current_pairs + [(p1, p2)])
            if result is not None:
                return result
    # If no pair found for p1, return None to signal backtrack
    return None

def pairing(round_number, player_list, player_scores, pairing_history, pairings, player_count, match_win_percentage, match_result_history, omw, oomw):
    if round_number == 1:
        pairings.clear()
        random.shuffle(player_list)
        bye_player = None
        for i in range(0, player_count - 1, 2):
            p1 = player_list[i]
            p2 = player_list[i+1]
            pairings.append((p1, p2))
            pairing_history[p1].append(p2)
            pairing_history[p2].append(p1)

        if player_count % 2 == 1:
            bye_player = player_list[-1]
            print(f"Bye: {bye_player}")
            player_scores[bye_player] += 3
            pairing_history[bye_player].append("BYE")
            match_result_history[bye_player].append("W (BYE)")

        print("Round 1 Pairings:")
        for p1, p2 in pairings:
            print(f"{p1} vs {p2}")
        return player_scores, pairing_history, pairings, match_result_history, omw, oomw, bye_player

    else:
        pairings.clear()
        for name in player_list:
            opponents = [opp for opp in pairing_history[name] if opp != "BYE"]
            if opponents:
                omw[name] = round(sum(match_win_percentage[opp] for opp in opponents) / len(opponents), 1)
                oomw[name] = round(sum(omw[opp] for opp in opponents) / len(opponents), 1) if opponents else 0.0

        sorted_players = sorted(player_list, key=lambda x: (-player_scores[x], x))
        unpaired = list(sorted_players)
        print(sorted_players)

        # Try to find full pairings
        best_pairings = find_pairings(unpaired, pairing_history, [])
        bye_player = None
        if best_pairings is None:
            # If not possible, try with one BYE (lowest ranked player)
            for idx in range(len(unpaired)-1, -1, -1):
                test_unpaired = unpaired[:idx] + unpaired[idx+1:]
                test_pairings = find_pairings(test_unpaired, pairing_history, [])
                if test_pairings is not None:
                    best_pairings = test_pairings
                    bye_player = unpaired[idx]
                    break

        if best_pairings is not None:
            for p1, p2 in best_pairings:
                pairings.append((p1, p2))
                pairing_history[p1].append(p2)
                pairing_history[p2].append(p1)
        if bye_player:
            print(f"Bye: {bye_player}")
            player_scores[bye_player] += 3
            pairing_history[bye_player].append("BYE")
            match_result_history[bye_player].append("W (BYE)")

        print(f"Round {round_number} Pairings:")
        for p1, p2 in pairings:
            print(f"{p1} vs {p2}")
    return player_scores, pairing_history, pairings, match_result_history, omw, oomw, bye_player

def score_update(pairings, player_scores, mwp, round_number, match_result_history, results):
    #print("Result in compute.py", results)
    for p1, p2 in pairings:
        result = results.get((p1, p2))
        print("Result in compute.py", result)
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
            match_result_history[p1].append('L')
            match_result_history[p2].append('L')
        for p in (p1, p2):
            mwp[p] = round(player_scores[p] / 3 / round_number * 100, 1)
            
    round_number += 1
    return player_scores, mwp, round_number, match_result_history

def final_tie_breaker(player_list, player_scores, omw, oomw, player_tie_breakers, match_result_history):
    
    for name in player_list:
        loss_rounds = [i + 1 for i, result in enumerate(match_result_history[name]) if result == 'L']
        score_str = f"{player_scores[name]:02d}"
        omw_str = str(int(omw[name]*10))
        oomw_str = str(int(oomw[name]*10))
        sslr = sum(r ** 2 for r in loss_rounds)
        sslr_str = f"{sslr:03d}"
        player_tie_breakers[name] = int(score_str + omw_str + oomw_str + sslr_str)
    
    return player_tie_breakers

