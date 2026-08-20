"""Helper script: embeds OCR TTS image base64 into landing_page.py"""
import base64, sys

img_path = r'C:\Users\souri\.gemini\antigravity-ide\brain\bc460722-f260-4501-9457-22ab4ff18453\ocr_tts_card_1785622534468.png'

with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')

data_url = 'data:image/png;base64,' + b64
print(f'Image b64 length: {len(b64)}')

with open(r'C:\Users\souri\OneDrive\Desktop\sensai\views\landing_page.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
replaced = False
for i, line in enumerate(lines):
    stripped = line.strip()
    # Match any img2 = "..." assignment line
    if stripped.startswith('img2 ='):
        lines[i] = f'    img2 = "{data_url}"'
        replaced = True
        print(f'Replaced img2 at line {i+1}')
        break

if not replaced:
    print('ERROR: could not find img2 assignment line')
    for i, line in enumerate(lines):
        if 'img2' in line and '=' in line:
            print(f'  Candidate line {i+1}: {repr(line[:80])}')
    sys.exit(1)

with open(r'C:\Users\souri\OneDrive\Desktop\sensai\views\landing_page.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Done - landing_page.py updated with embedded OCR TTS image.')
