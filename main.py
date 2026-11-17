##CLI i/o for now 
## will probably make web part later 
from riotAPIs import get_account_info, get_match_history, get_single_match, get_match_timeline
from analyzer import calculate_score, load_yaml, scoring, extract_stats
import requests
import pandas as pd
import time 


def main():
    
    puuid = get_account_info("blockeater43", "777")
    print(puuid)
    match_history = get_match_history(puuid, count=20)
    #print(match_history)
    
    test_match = get_single_match(match_history[0])
    test_timeline = get_match_timeline(match_history[0])
    #print(test_match)
    #print(test_timeline)

    test_match_df = pd.json_normalize(test_match["info"]["participants"])
    participant = next(p for p in test_match['info']['participants'] if p['puuid'] == puuid)
    #print(participant['largestCriticalStrike'])
    #print(test_match_df['kills'])
    
    #test_timeline_df = pd.json_normalize(test_timeline)
    #print(test_timeline_df)
    
    
    
    #analyzer testing i thinking 
    constraints = load_yaml()
    results = calculate_score(test_match, puuid, constraints)
    print(results)
    
    #so the total score is stored with the results so if i want to i can look at which constraints are maybe too heavy or too light 
    #but accesssing might be a little weird since its nested in the results dict
    
    
    
    

if  __name__ == "__main__":
    main()
    