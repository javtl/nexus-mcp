"""Generates simple placeholder icons and a carousel image for the Alexa+ add-on."""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path("alexa-addon/assets")
OUT.mkdir(parents=True, exist_ok=True)
BG, FG = (20, 40, 90, 255), (255, 255, 255, 255)


def draw_mark(size: tuple[int, int], path: Path) -> None:
    img = Image.new("RGBA", size, BG)
    d = ImageDraw.Draw(img)
    w, h = size
    pad = min(w, h) // 5
    d.rectangle([pad, pad, w - pad, h - pad], outline=FG, width=max(2, min(w, h) // 18))
    d.line([pad, h // 2, w - pad, h // 2], fill=FG, width=max(2, min(w, h) // 18))
    img.save(path)


for s in (72, 64, 88, 126, 180, 241):
    draw_mark((s, s), OUT / f"icon-{s}x{s}.png")
draw_mark((600, 900), OUT / "carousel-1.png")
print("Generated:", sorted(p.name for p in OUT.iterdir()))