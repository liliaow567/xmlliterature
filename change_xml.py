import getdata as gt
import sys

def main(argv):
    file = argv[0]
    gt.change(file)

if __name__ == "__main__":
    main(sys.argv[1:])