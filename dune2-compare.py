#!/usr/bin/env python3
"""Generate EGA conversion candidates without replacing the original DUNE2.ICC."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from qic import QIC


def main():
    root = Path(__file__).resolve().parent
    output = root / 'examples' / 'dune2'
    output.mkdir(parents=True, exist_ok=True)
    source = root / 'png' / 'dune2.png'
    ega = QIC(palette='ega')
    variants = [('Source (full color)', Image.open(source).convert('RGBA'))]

    # Show the saved icon with its original preview palette and with standard EGA.
    QIC().icc2png(root / 'icc' / 'DUNE2.ICC', output / 'original-preview.png')
    ega.icc2png(root / 'icc' / 'DUNE2.ICC', output / 'original-ega.png')
    variants.append(('Existing ICC / EGA', Image.open(output / 'original-ega.png')))
    for stem, title, metric, dither in (
        ('RGB', 'RGB nearest / EGA', 'rgb', 0),
        ('LAB', 'Perceptual / EGA', 'lab', 0),
        ('LAB40', 'Perceptual / 40% diffusion', 'lab', 0.4),
        ('LAB70', 'Perceptual / 70% diffusion', 'lab', 0.7),
    ):
        icc = output / f'DUNE2_{stem}.ICC'
        png = output / f'DUNE2_{stem}.png'
        ega.png2icc(source, icc, metric=metric, dither=dither)
        ega.icc2png(icc, png)
        with Image.open(png) as image:
            rgba = np.array(image)
            assert image.size == (32, 32)
            assert set(map(tuple, rgba[:, :, :3].reshape(-1, 3))) <= set(ega.colors)
            assert set(np.unique(rgba[:, :, 3])) <= {0, 255}
            assert np.array_equal(rgba[:, :, 3] > 0,
                                  np.array(Image.open(source))[:, :, 3] > 100)
            variants.append((title, image.copy()))
        data = icc.read_bytes()
        assert len(data) == 1032
        assert data[:4] == data[516:520] == bytes((31, 0, 31, 0))

    sheet = Image.new('RGB', (1320, 350), '#dddddd')
    draw = ImageDraw.Draw(sheet)
    for i, (title, image) in enumerate(variants):
        x = i * 220 + 10
        draw.text((x, 12), title, fill='black')
        backdrop = Image.new('RGBA', (32, 32), (170, 170, 170, 255))
        backdrop.alpha_composite(image)
        sheet.paste(backdrop.convert('RGB').resize((192, 192), Image.Resampling.NEAREST),
                    (x, 40))
        draw.text((x, 244), 'Actual size:', fill='black')
        for n, color in enumerate(((170, 170, 170), (0, 0, 170), (0, 0, 0))):
            background = Image.new('RGBA', (32, 32), (*color, 255))
            background.alpha_composite(image)
            sheet.paste(background.convert('RGB'), (x + n * 55, 270))
    draw.text((10, 326), '32 x 32 pixels; previews enlarged 6x with nearest-neighbor scaling.',
              fill='black')
    sheet.save(output / 'comparison.png')
    print(f'Comparison and four verified ICC/PNG candidates: {output}')


if __name__ == '__main__':
    main()
