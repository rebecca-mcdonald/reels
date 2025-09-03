#!/usr/bin/env python3
"""
make_ig_reel.py
Create an Instagram Reel (1080x1920) with luxury static text overlays and smooth jazz audio.
- Crops/centers your source video to vertical 9:16
- Adds two static text strips (first half / second half)
- Replaces original audio with your provided jazz track (looped to full duration)
Requires: moviepy, Pillow (PIL), numpy
"""
import argparse
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.audio.AudioClip import AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def find_font(preferred=("DejaVuSerif-Bold.ttf","DejaVuSerif.ttf","Arial.ttf","FreeSerifBold.ttf","Times New Roman.ttf")):
    # Try a few common fonts; fallback to PIL default
    for name in preferred:
        try:
            return ImageFont.truetype(name, 1).path  # triggers OSError if missing
        except Exception:
            continue
    return None

def load_font(size, fallback=None):
    font_path = None
    # If user provided a font file path, try that first
    if fallback and os.path.isfile(fallback):
        try:
            return ImageFont.truetype(fallback, size)
        except Exception:
            pass
    # Try common fonts on system
    for name in ["DejaVuSerif-Bold.ttf","DejaVuSerif.ttf","Arial.ttf","FreeSerifBold.ttf","Times New Roman.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    # Last resort: PIL default bitmap font (not ideal, but works)
    return ImageFont.load_default()

def draw_text_strip(text, fontsize=70, box_width=1000, box_height=150, font_color=(255,255,255,255), bg_color=(0,0,0,160), font_path=None, padding=24):
    font = load_font(fontsize, font_path)
    img = Image.new("RGBA", (box_width, box_height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rect background
    radius = 20
    rect = [0, 0, box_width, box_height]
    # rounded rectangle (Pillow >= 8.2): draw.rounded_rectangle
    draw.rounded_rectangle(rect, radius=radius, fill=bg_color)

    # Center text
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_w = text_bbox[2]-text_bbox[0]
    text_h = text_bbox[3]-text_bbox[1]
    x = (box_width - text_w)//2
    y = (box_height - text_h)//2
    draw.text((x, y), text, font=font, fill=font_color)
    return np.array(img)

def loop_audio_to_duration(audio_clip, duration):
    # Loop the audio seamlessly to match video duration
    if audio_clip.duration >= duration:
        return audio_clip.subclip(0, duration)
    loops = int(np.ceil(duration / audio_clip.duration))
    clips = [audio_clip] * loops
    concatenated = clips[0]
    for c in clips[1:]:
        concatenated = concatenated.append(c)
    return concatenated.subclip(0, duration)

def main():
    ap = argparse.ArgumentParser(description="Render an IG Reel with static luxury overlays and jazz audio")
    ap.add_argument("--video", required=True, help="Path to source video (e.g., new.mov)")
    ap.add_argument("--audio", required=True, help="Path to smooth jazz audio (mp3/wav/m4a)")
    ap.add_argument("--out", default="ig_reel_final.mp4", help="Output MP4 path")
    ap.add_argument("--title", default="Premium Drink Menu Available on Sundays!", help="Top message (first half)")
    ap.add_argument("--cta", default="Book Now", help="Bottom message (second half)")
    ap.add_argument("--font", default="", help="Optional path to a TTF/OTF font file (serif recommended)")
    ap.add_argument("--fps", type=int, default=30, help="Output frame rate")
    ap.add_argument("--bitrate", default="8M", help="Video bitrate (e.g., 6M, 8M)")
    ap.add_argument("--top_y", type=int, default=200, help="Y position for top strip")
    ap.add_argument("--bottom_y", type=int, default=1600, help="Y position for bottom strip")
    ap.add_argument("--title_size", type=int, default=65, help="Font size for title")
    ap.add_argument("--cta_size", type=int, default=90, help="Font size for CTA")
    ap.add_argument("--box_width", type=int, default=1000, help="Strip width")
    ap.add_argument("--title_box_height", type=int, default=150, help="Title strip height")
    ap.add_argument("--cta_box_height", type=int, default=160, help="CTA strip height")
    ap.add_argument("--opacity", type=int, default=160, help="Black box opacity 0-255")
    args = ap.parse_args()

    # Load and prepare video
    clip = VideoFileClip(args.video)
    # Resize height to 1920, keep center, crop width to 1080
    clip_resized = clip.resize(height=1920)
    clip_cropped = clip_resized.crop(x_center=clip_resized.w/2, width=1080, height=1920)
    duration = clip_cropped.duration

    # Build text strips
    title_img = draw_text_strip(
        args.title, fontsize=args.title_size, box_width=args.box_width,
        box_height=args.title_box_height, font_color=(255,255,255,255),
        bg_color=(0,0,0,args.opacity), font_path=args.font or None
    )
    cta_img = draw_text_strip(
        args.cta, fontsize=args.cta_size, box_width=args.box_width,
        box_height=args.cta_box_height, font_color=(255,255,255,255),
        bg_color=(0,0,0,args.opacity), font_path=args.font or None
    )

    title_clip = (ImageClip(title_img, transparent=True)
                  .set_duration(duration/2)
                  .set_position(("center", args.top_y)))
    cta_clip = (ImageClip(cta_img, transparent=True)
                .set_duration(duration/2)
                .set_start(duration/2)
                .set_position(("center", args.bottom_y)))

    # Replace audio with jazz
    jazz = AudioFileClip(args.audio)
    jazz_looped = loop_audio_to_duration(jazz, duration)

    final = CompositeVideoClip([clip_cropped, title_clip, cta_clip]).set_audio(jazz_looped)

    # Export
    final.write_videofile(
        args.out,
        codec="libx264",
        audio_codec="aac",
        fps=args.fps,
        bitrate=args.bitrate,
        threads=4,
        preset="medium"
    )

if __name__ == "__main__":
    main()
