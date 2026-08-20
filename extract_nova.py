import json
log_file = r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\.system_generated\logs\transcript_full.jsonl'
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        if 'AP1WRLvP-iGszTnj-sK8440-iIuV-hZ_Jt1iK7jV-lJ3wS3_Hn4YxG' in line:
            idx = line.find('AP1WRLvP-iGszTnj-sK8440-iIuV-hZ_Jt1iK7jV-lJ3wS3_Hn4YxG')
            val = line[idx:idx+300].split('"')[0].split("'")[0]
            print('nova_bg=' + val)
            break
