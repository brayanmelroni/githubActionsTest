import math
import argparse
# https://www.youtube.com/watch?v=cdblJqEUDNo

parser = argparse.ArgumentParser(description='Calculate Volume of Cyllinder')
parser.add_argument('-r','--radius',type=int,required=True, help='Radius Of Cyllinder')
parser.add_argument('-H','--height',type=int,required=True, help='Height Of Cyllinder')
group = parser.add_mutually_exclusive_group(required=False)  
group.add_argument('-q','--quiet',action='store_true', help='print quiet') # store_true means default is false, when given a value it is true
group.add_argument('-v','--verbose',action='store_true', help='print verbose')
args = parser.parse_args()

def cylinder_volume(radius, height):
    vol = (math.pi)*(radius ** 2)*height
    return vol

if __name__ == "__main__":
    volume = cylinder_volume(args.radius,args.height)
    if args.quiet:
        print(volume)
    elif args.verbose:
        print('Verbose Mode: '+ str(volume)) 
    else:
        print('No mode' + str(volume))