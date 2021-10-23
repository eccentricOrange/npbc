import argparse

parser = argparse.ArgumentParser(description='calculate your newspaper bill')
parser.add_argument('command')
parser.add_argument('-l', nargs=1, default=0)
parser.add_argument('-c', nargs=1, default=0, help ="trgd")

args = parser.parse_args()
print(args)