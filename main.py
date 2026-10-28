#!/usr/bin/env python3
import argparse
from pathlib import Path
from src.generator import generate
from src.core.serialization import convert


def main():
    parser=argparse.ArgumentParser(description='Deterministic Geometry Dash challenge generator')
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--generate',choices=['absolute-collapse'])
    action.add_argument('--convert',type=Path,metavar='LEVEL_FILE')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'output')
    args=parser.parse_args()
    if args.generate:
        report=generate(args.output)
        print(f"{report['status']}: {report['objects']} objects; exports in {args.output}")
        print('Exact GD physics, in-game import, song synchronization and TOP 1 rating are unverified.')
    else:
        args.output.mkdir(parents=True,exist_ok=True)
        convert(args.convert,args.output/(args.convert.stem+'.gmd'))

if __name__=='__main__': main()
