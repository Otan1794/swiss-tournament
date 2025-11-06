import math

from compute import score_update, pairing, final_tie_breaker

#player_list = ['jojo', 'momo', 'koko', 'bobo', 'lolo', 'nono', 'papa'] #For testing
player_list = []

print("Enter player names one by one. Press Enter without typing a name to finish.")

while True:
    name = input("Enter player name: ")
    if name == "": #replace with signal from front end to stop input
        break
    if name in player_list:
        print("That name is already in the list. Please enter a different name.")
        continue    
    player_list.append(name)

print("Players:", player_list)

player_scores = {name: 0 for name in player_list}
match_win_percentage = {name: 0.0 for name in player_list}
omw = {name: 0.0 for name in player_list} #Opponents' Match Win Percentage
oomw = {name: 0.0 for name in player_list} #Opponent's Opponents' Match Win Percentage

#print(player_scores)
#print(match_win_percentage)

player_count = len(player_list)
print(f"Total players: {player_count}")

number_of_rounds = math.ceil(math.log2(player_count))

print(f"Total number of rounds: {number_of_rounds}")

pairings = []
pairing_history = {name: [] for name in player_list}  #Track past opponents
match_result_history = {name: [] for name in player_list} #Track past match results
player_tie_breakers = {name: [] for name in player_list} #Track tie breakers
round_number = 1

for i in range(number_of_rounds):
    player_scores, pairing_history, pairings, match_result_history, omw, oomw = pairing(
        round_number, 
        player_list, 
        player_scores, 
        pairing_history, 
        pairings, 
        player_count,
        match_win_percentage,
        match_result_history,
        omw,
        oomw
    )

    player_scores, match_win_percentage, round_number, match_result_history = score_update(
        pairings, 
        player_scores, 
        match_win_percentage, 
        round_number,
        match_result_history
    )
    

player_tie_breakers = final_tie_breaker(player_list, player_scores, omw, oomw, player_tie_breakers, match_result_history)
    
print("Scores:")
for name, score in player_scores.items():
    print(f"{name}: {score}")
    
print("Match Results History:")
for name, results in match_result_history.items():
    print(f"{name}: {results}")

print("Pairing History:")
for name in player_list:
    print(f"Pairing history of {name}: ", pairing_history[name])
    
print("Match Win Percentage:")
for name, mwp in match_win_percentage.items():
    print(f"{name}: {mwp:.2f}%")    

print("Opponents' Match Win Percentage (OMW):")
for name, val in omw.items():
    print(f"{name}: {val:.2f}%")
    
print("Opponent's Opponents' Match Win Percentage (OOMW):")
for name, val in oomw.items():
    print(f"{name}: {val:.2f}%")
    
print("Player Tie Breakers:")
for name, val in player_tie_breakers.items():
    print(f"{name}: {val}")
    
print("Final Rankings:")
rankings = sorted(player_list, key=lambda x: (-player_tie_breakers[x], x))
for rank, name in enumerate(rankings, start=1):
    print(f"{rank}. {name} (Score: {player_scores[name]}, OMW: {omw[name]}, OOMW: {oomw[name]}, tie-breaker: {player_tie_breakers[name]})")
