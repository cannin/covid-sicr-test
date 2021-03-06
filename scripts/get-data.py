#!/usr/bin/env python
# coding: utf-8


import argparse
from niddk_covid_sicr import data
from pathlib import Path

# Parse all the command-line arguments
parser = argparse.ArgumentParser(description='Get data to use for fitting')
parser.add_argument('-dp', '--data-path', default='./data',
                    help='Path for storing data')
parser.add_argument('-s', '--sources', default=['jhu', 'covid-tracking'],
                    nargs='+', help='Data sources to use')
parser.add_argument('-fi', '--filter', default=1, type=int,
                    help='Whether or not to filter based on data thresholds')
parser.add_argument('-fn', '--fix-negatives', default=0, type=int,
                    help=("Whether or not to fix negative values "
                          "in the daily data or not"))
args = parser.parse_args()

# Create the data path
data_path = Path(args.data_path)
data_path.mkdir(parents=True, exist_ok=True)
assert data_path.exists(), "%s is not a valid data path" % data_path.resolve()


def get_scraper(name):
    func_name = 'get_%s' % name.replace('-', '_')
    try:
        f = getattr(data, func_name)
    except AttributeError:
        raise Exception("No function named %s in the data.py module"
                        % func_name)
    return f


for source in args.sources:
    print("Getting data from %s..." % source)
    f = get_scraper(source)
    f(data_path, filter=args.filter)

if args.fix_negatives:
    print("Fixing negative values in daily data...")
    data.fix_negatives(data_path)

print("Data now available at %s" % data_path.resolve())
