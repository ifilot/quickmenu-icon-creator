# -*- coding: utf-8 -*-

#
# Purpose: Convert a .PNG file to a .ICC file
#

from qic import QIC

def main():
    infile = 'png/dune2.png'
    outfile = 'icc/DUNE2.ICC'

    # perform conversion
    q = QIC()
    q.png2icc(infile, outfile)

    # visualize the result
    q.compare_icc(infile, outfile)

if __name__ == '__main__':
    main()