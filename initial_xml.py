import getdata as gt
import sys

def main(argv):
    file = argv[0]
    gt.initial(file)

if __name__ == "__main__":
    main(sys.argv[1:])