# Quick Menu Icon Creator

[Quick Menu](https://en.wikipedia.org/wiki/Quick_Menu) is a graphical user
interface for MS-DOS developed by OSCS Software Development. Quick Menu allows
users to create their own menu structures for efficient launching of games and
applications without having to navigate a drive via MS-DOS commands such as `cd`
and `dir`.

Quick Menu employs 32x32 icons with the EGA (4 bits per pixel) color scheme. The
icons are stored in Quick Menu in an internal archive, but can be exported to or
imported from `.icc` files. This repository contains a set of Python-based
scripts to read those `.icc` files or to convert `.png` files to `.icc` files.

![Dune II source and EGA conversion variants, including LAB40](examples/dune2/comparison.png)

The LAB40 result is the fifth column, labeled "Perceptual / 40% diffusion".
The imported result is shown below under **LAB40 imported into QuickMenu**.

## ICC File format

The ICC file format stores an icon. These files are always exactly 1032 bytes
long and can be separated into two parts, being the icon bitmap and the mask
bitmap. Each bitmap start with a header sequence of 4 bytes (`0x1F, 0x00, 0x1F,
0x00`) followed by the pixel data. Each 16 bytes of pixel data corresponds to a
row of the icon. The pixel information is stored on per-bit basis. The first
four bytes correspond to the LSB of each pixel for each of the 32 pixels in a
row. Each subsequent set of 4 bytes correspond to the next bit for each pixel in
that row such that exactly 16 bytes are needed to store all the pixel
information for a given row (giving a color resolution of 4 bits per pixel). The
mask bitmap uses the same encoding as the icon bitmap, yet each pixel either
corresponds to a value of `0x0` (transparent) or to `0xF` (opague).

## Conversion

The Python script in this repository allows for a conversion from a `.png` to an
`.icc`. It is assumed that these `.png` files carry an alpha channel (allowing
for transparency) and are exactly 32x32 pixels in size. Since `.png` files er
encoded with 24 bits per pixel (bpp), a downconversion to the EGA color scheme
is required. This is achieved by calculating the vector difference between the
24bpp color and each of the 4bpp colors. The color in the EGA pallette whose
difference has the least Euclidean distance with respect to the original 24bpp
color is then chosen. Although this conversion is automatic, it should be noted
that this is not always the most ideal result and the user is recommended to
make further adjustment to the final icon in Quick Menu.

## Improved EGA conversion

The original converter matches colors by RGB distance using an approximate
palette. This can turn the Dune II soldier's olive armor into gray or black.
You can opt into the standard 16-color EGA palette, perceptual CIELAB matching,
and partial Floyd–Steinberg error diffusion:

```python
from qic import QIC

q = QIC(palette='ega')
q.png2icc('png/dune2.png', 'icc/DUNE2_NEW.ICC', metric='lab', dither=0.4)
q.icc2png('icc/DUNE2_NEW.ICC', 'png/dune2-new.png')
```

`dither=0` disables diffusion; `dither=1` diffuses the full error. At 32x32,
strong diffusion can obscure small features. The transparency threshold remains
alpha > 100, and error does not spread into or out of transparent pixels.
`QIC()` preserves the original palette and conversion defaults.

Run `python3 dune2-compare.py` to reproduce four ICC/PNG alternatives and
`examples/dune2/comparison.png`, with enlarged previews and actual-size views
against gray, blue, and black. The original DUNE2.ICC is preserved. All
candidate PNGs are decoded from their ICC files and checked for EGA colors,
binary transparency, and the original silhouette. EGA has no dark olive color;
pixel editing is still useful for emphasizing the helmet and armor at this size.

### LAB40 imported into QuickMenu

This DOSBox capture shows `DUNE2_LAB40.ICC` imported into QuickMenu's icon
editor, including its transparency mask and previews. QuickMenu's display
palette differs from the standard EGA RGB values used in the comparison above;
the imported icon retains the same EGA color indices.

![LAB40 Dune II icon imported into QuickMenu's icon editor](img/qm-icon-creation-lab40.png)

Recreate the imported file with:

```bash
python3 png2icc.py png/dune2.png icc/DUNE2_LAB40.ICC --algorithm lab40
```

## Dependencies

The scripts in this repository depend on the
[PIL](https://pillow.readthedocs.io/en/stable/) and [NumPy](https://numpy.org/)
modules. You can install these modules easily using

```bash
pip install -r requirements.txt
```

## Usage

### Conversion

1. Clone this repository.
2. Place source `.PNG` files in the `.png` folder
3. Select an algorithm and specify the input and output paths:

```bash
python3 png2icc.py png/dune2.png icc/DUNE2_NEW.ICC --algorithm lab40
```

LAB40 is the command-line default. Algorithm names are case-insensitive.

| Algorithm | Palette | Color matching | Error diffusion |
| --- | --- | --- | --- |
| `legacy` | Original approximate palette | RGB | None |
| `rgb` | Standard EGA | RGB | None |
| `lab` | Standard EGA | Perceptual CIELAB | None |
| `lab40` | Standard EGA | Perceptual CIELAB | 40% |
| `lab70` | Standard EGA | Perceptual CIELAB | 70% |

Add `--preview png/dune2-new.png` to save a decoded PNG, or `--show` to open
a comparison in an image viewer. Conversion runs without opening a viewer by
default. Omitting both paths uses `png/dune2.png` and `icc/DUNE2.ICC` (overwriting
that output). The Python `QIC()` API retains its original defaults.

### Visualization

1. Clone this repository.
2. Place `.ICC` in the `icc` folder.
3. Use `icc-show.py` to visualize an `.ICC` file
