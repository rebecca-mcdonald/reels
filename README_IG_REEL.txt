IG REEL TOOLKIT (Luxury Static Text + Smooth Jazz)

FILES
- make_ig_reel.py    -> Main script to render your reel
- requirements.txt   -> Python dependencies (install via pip)

QUICK START
1) Install Python 3.9+.
2) Install dependencies:
   pip install -r requirements.txt

3) Prepare your media:
   - Input video:   /path/to/new.mov  (any orientation; script will crop to 1080x1920)
   - Jazz audio:    /path/to/jazz.mp3 (or .wav/.m4a). Aim for 60–120s; script will loop as needed.

4) Run the script (example):
   python make_ig_reel.py --video "/path/to/new.mov" --audio "/path/to/jazz.mp3" --out "ig_reel_final.mp4"

DEFAULTS IT USES
- Vertical 1080x1920
- 30 fps, ~8 Mbps
- Title (first half): "Premium Drink Menu Available on Sundays!"
- CTA (second half):  "Book Now"
- White serif text over soft black rounded strips
- Strip positions: title near y=200, CTA near y=1600 (tweak via --top_y / --bottom_y)

TWEAKS
- Change text:
  --title "Your Headline" --cta "Your CTA"
- Move strips:
  --top_y 250 --bottom_y 1550
- Alter sizes:
  --title_size 70 --cta_size 90 --box_width 980 --title_box_height 160 --cta_box_height 170
- Opacity of black box (0-255):
  --opacity 150
- Custom font file (.ttf / .otf):
  --font "/path/to/YourSerifFont.ttf"

TROUBLESHOOTING
- If fonts look basic, supply a font via --font (e.g., a premium serif).
- If export is slow, try adding:  --bitrate 6M  --fps 24
- If audio seems short, don’t worry — it’s looped to your video length.

Enjoy!