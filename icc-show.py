# -*- coding: utf-8 -*-

#
# Purpose: Visualize a .ICC file
#

from qic import QIC

def main():    
    q = QIC()
    q.show_icc('icc/POP.ICC')

if __name__ == '__main__':
    main()