#so this is score calculator but i have no idea how I am going to calculate for different roles 
#In the future I could add constraints per role but for now i will focus on top/mid/bot as they are a little more straightforward

import yaml

def load_yaml(path='config.yaml') -> dict:
    with open(path, 'r') as file:
        return yaml.safe_load(file)['constraints']
    
def scoring(value: float, thresholds: dict, lower_is_better=False) -> float:
    #for now we will just map scores to these values but once i figure it out it will be more precise and on a per role basis
    order = ["excellent", "good", "average", "poor"]
    scores = [100, 75, 50, 25]

    if lower_is_better:
        value = -value
        thresholds = {k: -v for k, v in thresholds.items()}

    for label, score in zip(order, scores):
        if value >= thresholds[label]:
            return score
    return 10  # below poor

def extract_stats(match: dict, puuid: str) -> dict:
    participant = next(p for p in match['info']['participants'] if p['puuid'] == puuid)
    duration = match['info']['gameDuration'] / 60
    
    kills = participant['kills']
    deaths = participant['deaths']
    assists = participant['assists']
    cs = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
    #gold = participant['goldEarned'] will add later 
    vision_score = participant['visionScore']
    damage_dealt = participant['totalDamageDealtToChampions']
    team_damage = sum(p['totalDamageDealtToChampions'] for p in match['info']['participants'] if p['teamId'] == participant['teamId'])
    total_deaths = sum(p['deaths'] for p in match['info']['participants'] if p['teamId'] == participant['teamId'])
    
    return {
        "kda": (kills + assists) / max(1, deaths),
        "cs_per_min": cs / duration,
        "vision_score_per_min": vision_score / duration,
        "death_share": participant['deaths'] / max(1, total_deaths),
        "damage_share": damage_dealt / max(1, team_damage)
    }
    
LOWER_IS_BETTER = ["death_share"]

def calculate_score(match: dict, puuid: str, constraints: dict) -> float:
    stats = extract_stats(match, puuid)
    results = {}
    total_weight = sum(c['weight'] for c in constraints.values()) #should be 100 
    weighted_score = 0
    
    for name, config in constraints.items():
        if name not in stats:
            continue
        raw = stats[name]
        score = scoring(raw, config['thresholds'], lower_is_better=(name in LOWER_IS_BETTER))
        weighted_score += score * (config['weight'] / total_weight)
        weighted_sum += weighted_score
        results[name] = {
            "raw": raw,
            "score": score,
            "weight": config['weight']
        }
        results["total_score"] = weighted_sum
        return results
    