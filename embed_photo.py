#!/usr/bin/env python3
"""
Usage: python3 embed_photo.py <slot> <image_file>

Slots:
  flybridge        - Flybridge section main image
  salon-thumb2     - Heart of Solaire 2nd thumbnail
  cabin-aft        - Starboard Aft Cabin main image
  cabin-forward    - Starboard Forward Cabin main image
  cabin-port       - Port Forward Cabin main image

Example:
  python3 embed_photo.py salon-thumb2 flybridge.jpg
  python3 embed_photo.py flybridge flybridge.jpg
"""

import sys, base64, re, os

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(1)

slot, img_path = sys.argv[1], sys.argv[2]
html_path = os.path.join(os.path.dirname(__file__), 'index.html')

with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
data_uri = f'data:image/jpeg;base64,{b64}'

with open(html_path, 'r') as f:
    html = f.read()

def set_main_img(section_id, alt_text):
    pattern = rf'(<div id="{section_id}".*?<div class="cabin-imgs">\s*<img class="main-img" src=")[^"]*(")'
    if not re.search(pattern, html, re.DOTALL):
        pattern = rf'(<div id="{section_id}".*?<div class="cabin-imgs">\s*<img class="main-img" src=")[^"]*(")'
    return re.sub(pattern, rf'\g<1>{data_uri}\g<2>', html, count=1, flags=re.DOTALL)

def set_flybridge_main():
    pattern = r'(<span class="cabin-tag">Flybridge</span>.*?<div class="cabin-imgs">\s*<img class="main-img" src=")[^"]*(")'
    if re.search(pattern, html, re.DOTALL):
        return re.sub(pattern, rf'\g<1>{data_uri}\g<2>', html, count=1, flags=re.DOTALL)
    # No main-img yet — insert one
    old = '<span class="cabin-tag">Flybridge</span>'
    cabin_imgs_start = html.rfind('<div class="cabin-imgs">', 0, html.find(old))
    cabin_imgs_end = html.find('\n', cabin_imgs_start) + 1
    new_img = f'      <img class="main-img" src="{data_uri}" alt="Flybridge" onerror="this.style.opacity=\'.15\'">\n'
    return html[:cabin_imgs_end] + new_img + html[cabin_imgs_end:]

def set_salon_thumb2():
    salon_idx = html.find('<div id="salon"')
    thumb_idx = html.find('<div class="thumb-row">', salon_idx)
    # Find the placeholder img with id="salonflybridge"
    placeholder = '<img id="salonflybridge"'
    ph_idx = html.find(placeholder, thumb_idx)
    if ph_idx >= 0:
        end = html.find('>', ph_idx) + 1
        new_img = f'<img src="{data_uri}" alt="Flybridge dining" onerror="this.style.opacity=\'.15\'">'
        return html[:ph_idx] + new_img + html[end:]
    # No placeholder — append after first thumb
    first_img_end = html.find('>', html.find('<img', thumb_idx)) + 1
    new_img = f'\n        <img src="{data_uri}" alt="Flybridge dining" onerror="this.style.opacity=\'.15\'">'
    return html[:first_img_end] + new_img + html[first_img_end:]

slots = {
    'flybridge':      set_flybridge_main,
    'salon-thumb2':   set_salon_thumb2,
    'cabin-aft':      lambda: set_main_img('master', 'Starboard Aft Cabin'),
    'cabin-forward':  lambda: set_main_img('port', 'Starboard Forward Cabin'),
    'cabin-port':     lambda: set_main_img('starboard', 'Port Forward Cabin'),
}

if slot not in slots:
    print(f"Unknown slot '{slot}'. Valid slots: {', '.join(slots)}")
    sys.exit(1)

new_html = slots[slot]()
with open(html_path, 'w') as f:
    f.write(new_html)

print(f"Done — embedded {img_path} into slot '{slot}'")
print(f"File size: {os.path.getsize(html_path)/1024/1024:.1f} MB")
