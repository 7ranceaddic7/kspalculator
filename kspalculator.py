#!/usr/bin/env python3

from argparse import ArgumentParser

epilog = """
deltav:pressure tuples:
You specify which delta-v (in m/s) at which pressure (0.0 = vacuum, 1.0 = ATM)
your ship must be able to reach. You might specify more than one of these
tuples. This might be useful if you're going to fly through different
environments, e.g. starting in atmosphere and later flying through vacuum.
A safe kerbin launch is "905:13:1.0 3650:13:0.18".
"""

# TODO: calculate good launch delta-v, maybe autogenerated

parser = ArgumentParser(description='Determine best rocket design', epilog=epilog)
parser.add_argument('payload', type=float, help='Payload in kg')
parser.add_argument('dvtuples', metavar='deltav[:min_acceleration[:pressure]]', nargs='+',
        help='Tuples of required delta v, minimum acceleration and environment pressure at each '
        'flight phase. Defaults for minimum acceleration is 0 m/s² and for '
        'pressure 0 ATM (= vacuum)')
parser.add_argument('-c', '--cheapest', action='store_true',
        help='Sort by cost instead of weight')
parser.add_argument('-b', '--boosters', action='store_true',
        help='Allow adding solid fuel boosters')
parser.add_argument('-S', '--preferred-size', choices=['tiny', 'small', 'large', 'extralarge'],
        help='Preferred width of the stage')
parser.add_argument('-g', '--best-gimbal', action='store_true',
        help='Not only compare whether engine has gimbal or not, but also the maximum '
        'trust vectoring angle')
parser.add_argument('--keep', action='store_true', help='Do not hide bad solutions')

args = parser.parse_args()

# we have the import here (instead of above) to have short execution time in
# case of calling with e.g. '-h' only.
from design import FindDesigns
from parts import RadialSize

ps = None
if args.preferred_size is not None:
    if args.preferred_size == "tiny":
        ps = RadialSize.Tiny
    elif args.preferred_size == "small":
        ps = RadialSize.Small
    elif args.preferred_size == "large":
        ps = RadialSize.Large
    else:
        ps = RadialSize.ExtraLarge

dv = []
ac = []
pr = []
for st in args.dvtuples:
    s = st.split(':')
    dv.append(float(s[0]))
    ac.append(0.0 if len(s) < 2 else float(s[1]))
    pr.append(0.0 if len(s) < 3 else float(s[2]))

all_designs = FindDesigns(args.payload, pr, dv, ac, ps, args.best_gimbal, args.boosters)

if args.keep:
    D = all_designs
else:
    D = [d for d in all_designs if d.IsBest]

if args.cheapest:
    D = sorted(D, key=lambda dsg: dsg.cost)
else:
    D = sorted(D, key=lambda dsg: dsg.mass)

for d in D:
    d.PrintInfo()
    print("")
