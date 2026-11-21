from PIL import Image, ImageDraw, ImageFont

# Load your existing scannable QR code
qr = Image.open("qr_codes/FHIR-00001.png").convert("RGB")

# Hospital wristband canvas (wide strip: ~9" x 2.1" if printed)
W, H = 1800, 420
band = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(band)

# Outer wristband border & medical blue accent bar on left
draw.rounded_rectangle([10, 10, W - 10, H - 10], radius=36, outline="#CBD5E1", width=6)
draw.rectangle([16, 16, 52, H - 16], fill="#0284C7")

# Wristband sizing snap-holes on the left strap
for x in range(110, 320, 65):
    draw.ellipse([x - 14, H // 2 - 14, x + 14, H // 2 + 14], outline="#94A3B8", width=4)

# Dashed perforation line separating strap from ID tag
for y in range(24, H - 24, 24):
    draw.line([(365, y), (365, y + 12)], fill="#CBD5E1", width=3)

# Load macOS Helvetica (falls back cleanly if unavailable)
def get_font(size):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()

font_title = get_font(44)
font_sub = get_font(30)
font_tag = get_font(26)

# Patient wristband text block
x_text = 415
draw.text((x_text, 55), "CITY CLINICAL CENTER", fill="#0284C7", font=font_tag)
draw.text((x_text, 105), "PATIENT ID: FHIR-00001", fill="#0F172A", font=font_title)
draw.text((x_text, 175), "RECORD: FHIR R4 LIVE CHART", fill="#334155", font=font_sub)
draw.text((x_text, 225), "SCAN WITH SMART GLASSES FOR HUD", fill="#64748B", font=font_tag)

# Red clinical alert pill (like a hospital allergy/caution band)
draw.rounded_rectangle([x_text, 290, x_text + 360, 355], radius=12, fill="#DC2626")
draw.text((x_text + 24, 306), "CLINICAL ALERT ACTIVE", fill="white", font=font_tag)

# Paste razor-sharp QR code on the right with quiet zone
qr_size = 330
qr_resized = qr.resize((qr_size, qr_size), Image.Resampling.NEAREST)
band.paste(qr_resized, (1240, (H - qr_size) // 2))

# Right strap end-holes
for x in range(1640, 1740, 65):
    draw.ellipse([x - 14, H // 2 - 14, x + 14, H // 2 + 14], outline="#94A3B8", width=4)

out_path = "qr_codes/wristband_FHIR-00001.png"
band.save(out_path)
print(f"Saved scannable hospital wristband to {out_path}")
