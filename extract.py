import json

prefixes = [
    'AP1WRLtU28KEnYY8lgh7DfLWAjgrqHiCdKWc191N6J6smydAPZQ_V',
    'AP1WRLtwpc5Ze64_W__2rWfFiszmuNKgerosLP7FGCfj6PB_D06T2',
    'AP1WRLtWmOCClTnCwez_QnsOgY6U_xsT_Hg5DBCQ-du_4HEf7MdPF',
    'AP1WRLvYun4SAvOme4MWZV6evMMwNwJ0YzzGKj-k8jCVx2rygQ',
    'AP1WRLvP-iGszTnj-sK8440-iIuV-hZ_Jt1iK7jV-lJ3wS3_Hn4YxG'
]
results = {p: None for p in prefixes}

log_file = r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\.system_generated\logs\transcript_full.jsonl'
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        for p in prefixes:
            if p in line and results[p] is None:
                idx = line.find(p)
                substr = line[idx:idx+350]
                end_chars = ['"', "'", ' ', '<', '>']
                idxs = [substr.find(c) for c in end_chars if substr.find(c) > 0]
                end_idx = min(idxs) if idxs else 350
                results[p] = substr[:end_idx]

for k, v in results.items():
    print(f'{k[:15]}...=https://lh3.googleusercontent.com/aida/{v}')
