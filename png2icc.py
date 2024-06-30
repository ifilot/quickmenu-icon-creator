# -*- coding: utf-8 -*-

#
# Purpose: Convert a .PNG file to a .ICC file
#

from qic import QIC

def main():
    infile = 'png/pop.png'
    outfile = 'icc/POP.ICC'

    # perform conversion
    q = QIC()
    q.png2icc(infile, outfile)

    # visualize the result
    q.show_icc(outfile)

if __name__ == '__main__':
    main()