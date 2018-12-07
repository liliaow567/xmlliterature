import getdata as gt
import sys

def main(argv):
    file = argv[0]
    title = argv[1]
    gt.initial(file,title)

if __name__ == "__main__":
    main(sys.argv[1:])