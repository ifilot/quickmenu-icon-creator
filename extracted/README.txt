QuikMenu III 3.1h bundled icons

Source supplied by the user:
https://winworldpc.com/download/11c3b3c3-837f-e284-a243-11c3a4c2ac5a
Archive: QuickMenu 3.1 (3.5), disk1.img, QM2.CMP.
The running program identifies itself as Version 3.1h, September 17, 1998.

Contents:
  color/: 100 original 1032-byte ICC records and 100 transparent 32x32 PNGs.
  mono/: 100 original 1032-byte ICM records and 100 transparent 32x32 PNGs.
  color-contact-sheet.png and mono-contact-sheet.png: all library slots.
  dosbox-quickmenu.png: screenshot of the program running in DOSBox.
  manifest.json: source and individual record SHA-256 checksums and offsets.
  quickmenu-icons.zip: bundle of the above (excluding itself).

Record numbers are 1-based positions in each library, not original names.
Empty or duplicate slots are intentionally retained. These are all icons in
both default libraries on this disk. The separately sold 500-icon add-on is
not present on the disk and is not included.

Extraction reads records directly, preserving all source bytes, including
unused monochrome buffer padding. Concatenating records in numeric order
reproduces each original DEF file byte-for-byte; this was verified for both
libraries. PNGs use standard EGA RGB values and binary transparency. Custom
QuickMenu display palettes may produce different on-screen colors.

The matching installation was opened successfully in DOSBox. The downloaded
libraries were also compared against the local installation disk and matched
exactly. All 200 PNGs were verified as 32x32 RGBA images.

To reproduce with Pillow installed:
  python3 extract-icons.py /path/to/installed/quickmenu extracted

The icons are original QuikMenu artwork by its original rights holders;
extraction does not change their licensing.
