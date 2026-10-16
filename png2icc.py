# -*- coding: utf-8 -*-

#
# Purpose: Convert a .PNG file to a .ICC file
#

import argparse
from pathlib import Path

from qic import QIC


ALGORITHMS = {
    'legacy': ('legacy', 'rgb', 0.0),
    'rgb': ('ega', 'rgb', 0.0),
    'lab': ('ega', 'lab', 0.0),
    'lab40': ('ega', 'lab', 0.4),
    'lab70': ('ega', 'lab', 0.7),
}


def main():
    parser = argparse.ArgumentParser(description='Convert a 32x32 PNG to a QuickMenu ICC icon.')
    parser.add_argument('infile', type=Path, nargs='?', default=Path('png/dune2.png'))
    parser.add_argument('outfile', type=Path, nargs='?', default=Path('icc/DUNE2.ICC'))
    parser.add_argument('--algorithm', '-a', type=str.lower, choices=ALGORITHMS,
                        default='lab40', help='conversion preset (default: lab40)')
    parser.add_argument('--preview', type=Path, metavar='PNG',
                        help='save a PNG decoded from the converted ICC')
    parser.add_argument('--show', action='store_true',
                        help='open a side-by-side comparison in an image viewer')
    args = parser.parse_args()

    palette, metric, dither = ALGORITHMS[args.algorithm]
    q = QIC(palette=palette)
    print(f'Algorithm: {args.algorithm} (palette={palette}, metric={metric}, dither={dither:g})')
    try:
        q.png2icc(args.infile, args.outfile, metric=metric, dither=dither)
        if args.preview:
            q.icc2png(args.outfile, args.preview)
        if args.show:
            q.compare_icc(args.infile, args.outfile)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
