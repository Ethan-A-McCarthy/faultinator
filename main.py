##CLI i/o for now 
## will probably make web part later 
from riotAPIs import get_account_info, get_match_history, get_single_match, get_match_timeline
import requests
import pandas as pd
import time 


def main():
    
    puuid = get_account_info("hummus", "SWAG")
    print(puuid)
    match_history = get_match_history(puuid, count=20)
    print(match_history)
    
    #test_match = get_single_match(match_history[0])
    #test_timeline = get_match_timeline(match_history[0])
    
    #pd.json_normalize(test_match)
    #print(test_match)
    
    
    
    
if  __name__ == "__main__":
    main()
    