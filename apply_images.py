import base64
from PIL import Image
import io
import re
import os

def get_b64(path):
    img = Image.open(path).convert('RGB')
    img = img.resize((400, 250))
    buffered = io.BytesIO()
    img.save(buffered, format='JPEG', quality=85)
    b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f'data:image/jpeg;base64,{b64}'

def get_b64_logo(path):
    img = Image.open(path).convert('RGBA')
    img = img.resize((200, 200))
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{b64}'

emo = get_b64(r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\emotion_analysis_old_1786987731866.png')
scene = get_b64(r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\scene_explaining_old_1786987996297.png')
sign = get_b64(r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\sign_language_old_1786988014510.png')
nova = get_b64_logo(r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\nova_ai_logo_old_1786988030600.png')

with open('views/landing_page.py', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

def replace_line(line_idx, new_str):
    line = lines[line_idx]
    # Replace anything starting with https://lh3... up to the end quote
    lines[line_idx] = re.sub(r'https://lh3\.googleusercontent\.com/aida/[a-zA-Z0-9_-]+', new_str, line)

replace_line(451, nova)
replace_line(1090, nova)
replace_line(504, sign)
replace_line(1171, sign)
replace_line(506, emo)
replace_line(1155, emo)
replace_line(507, scene)
replace_line(1163, scene)

with open('views/landing_page.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

with open('views/_patch_navbar_hero.py', 'r', encoding='utf-8') as f:
    ph_lines = f.read().split('\n')
ph_lines[13] = re.sub(r'https://lh3\.googleusercontent\.com/aida/[a-zA-Z0-9_-]+', nova, ph_lines[13])
with open('views/_patch_navbar_hero.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(ph_lines))

# Touch app.py
with open('app.py', 'a', encoding='utf-8') as f:
    f.write('\n')

print('Images replaced successfully!')
