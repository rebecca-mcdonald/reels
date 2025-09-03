#!/usr/bin/env python3
"""
make_ig_reel.py (Fixed Import)
Create an Instagram Reel (1080x1920) with luxury static text overlays and smooth jazz audio.
"""
import argparse
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def load_font(size, fallback=None):
    if fallback and os.path.isfile(fallback):
        try:
            return ImageFont.truetype(fallback, size)
        except Exception:
            pass
    for name in ["DejaVuSerif-Bold.ttf","DejaVuSerif.ttf","Arial.ttf","FreeSerifBold.ttf","Times New Roman.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_text_strip(text, fontsize=70, box_width=1000, box_height=150,
                    font_color=(255,255,255,255), bg_color=(0,0,0,160), font_path=None):
    font = load_font(fontsize, font_path)
    img = Image.new("RGBA", (box_width, box_height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    radius = 20
    draw.rounded_rectangle([0,0,box_width,box_height], radius=radius, fill=bg_color)
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_w = text_bbox[2]-text_bbox[0]
    text_h = text_bbox[3]-text_bbox[1]
    x = (box_width - text_w)//2
    y = (box_height - text_h)//2
    draw.text((x, y), text, font=font, fill=font_color)
    return np.array(img)

def loop_audio_to_duration(audio_clip, duration):
    if audio_clip.duration >= duration:
        return audio_clip.subclip(0, duration)
    loops = int(np.ceil(duration / audio_clip.duration))
    clips = [audio_clip] * loops
    concatenated = clips[0]
    for c in clips[1:]:
        concatenated = concatenated.append(c)
    return concatenated.subclip(0, duration)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", default="ig_reel_final.mp4")
    ap.add_argument("--title", default="Premium Drink Menu Available on Sundays!")
    ap.add_argument("--cta", default="Book Now")
    ap.add_argument("--font", default="")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--bitrate", default="8M")
    ap.add_argument("--top_y", type=int, default=200)
    ap.add_argument("--bottom_y", type=int, default=1600)
    ap.add_argument("--title_size", type=int, default=65)
    ap.add_argument("--cta_size", type=int, default=90)
    ap.add_argument("--box_width", type=int, default=1000)
    ap.add_argument("--title_box_height", type=int, default=150)
    ap.add_argument("--cta_box_height", type=int, default=160)
    ap.add_argument("--opacity", type=int, default=160)
    args = ap.parse_args()

    clip = VideoFileClip(args.video)
    clip_resized = clip.resize(height=1920)
    clip_cropped = clip_resized.crop(x_center=clip_resized.w/2, width=1080, height=1920)
    duration = clip_cropped.duration

    title_img = draw_text_strip(args.title, fontsize=args.title_size,
                                box_width=args.box_width, box_height=args.title_box_height,
                                bg_color=(0,0,0,args.opacity), font_path=args.font or None)
    cta_img = draw_text_strip(args.cta, fontsize=args.cta_size,
                              box_width=args.box_width, box_height=args.cta_box_height,
                              bg_color=(0,0,0,args.opacity), font_path=args.font or None)

    title_clip = (ImageClip(title_img, transparent=True)
                  .set_duration(duration/2)
                  .set_position(("center", args.top_y)))
    cta_clip = (ImageClip(cta_img, transparent=True)
                .set_duration(duration/2)
                .set_start(duration/2)
                .set_position(("center", args.bottom_y)))

    jazz = AudioFileClip(args.audio)
    jazz_looped = loop_audio_to_duration(jazz, duration)

    final = CompositeVideoClip([clip_cropped, title_clip, cta_clip]).set_audio(jazz_looped)
    final.write_videofile(args.out, codec="libx264", audio_codec="aac",
                          fps=args.fps, bitrate=args.bitrate, threads=4, preset="medium")

if __name__ == "__main__":
    main()
