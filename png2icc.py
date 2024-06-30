# -*- coding: utf-8 -*-

from qic import QIC

def main():
    q = QIC() 
    res = q.png2icc('png/pop.png', 'icc/POP.ICC')

if __name__ == '__main__':
    main()