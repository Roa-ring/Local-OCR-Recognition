import json

def json_cal(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scores = data['rec_scores']
    avg = sum(scores) / len(scores)
    return avg