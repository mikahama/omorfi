#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
This script is nothing but a simple ?SV file join. It uses 1 master
database with N fields and joins all matching fields on M files to extra
fields on right.
"""

# Author: Tommi A. Pirinen <tommi.pirinen@helsinki.fi> 2009, 2011

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sys import stdin, stdout, stderr, exit, argv
import argparse
import locale
import csv

def main():
    ap = argparse.ArgumentParser(description=
            "Join N field master CSV or TSV file with others having N+1 fields")

    ap.add_argument("--quiet", "-q", action="store_false", dest="verbose",
            default=False,
            help="do not print output to stdout while processing")
    ap.add_argument("--verbose", "-v", action="store_true", default=False,
            help="print each step to stdout while processing")
    ap.add_argument("--version", "-V", action="version")
    ap.add_argument("--input", "-i", action="append", required=True, 
            dest='infilenames',
            metavar="IFILE", help="read dictionary data from IFILEs")
    ap.add_argument("--join", "-j", action="append", required=True, 
            dest='joinfilenames',
            metavar="JFILE",
            help="read auxiliary data from JFILEs")
    ap.add_argument("--output", "-o", action="store", required=True,
            dest='outfilename',
            metavar="OFILE",
            help="write resulting data to OFILE")
    ap.add_argument("--fields", "-f", action="store", default=2,
            metavar="N", help="read N fields from master")
    ap.add_argument("--separator", "-s", action="store", default="\t",
            metavar="SEP", help="use SEP as separator")
    ap.add_argument("--comment", "-C", action="append", default=["#"],
            metavar="COMMENT", help="skip lines starting with COMMENT that"
                "do not have SEPs")
    ap.add_argument("--strip", "-S", action="store",
            metavar="STRIP", help="strip STRIP from fields before using")
    args = ap.parse_args()

    if args.strip == '"' or args.strip == "'":
        quoting = csv.QUOTE_ALL
    else:
        quoting = csv.QUOTE_NONE

    words = dict()
    for csv_filename in args.infilenames:
        if args.verbose:
            print("Reading dictionary from", csv_filename)
        linecount = 0
        entry_count = 0
        with open(csv_filename, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file, 
                    delimiter=args.separator, quoting=quoting,
                    strict=True)
            for csv_parts in csv_reader:
                linecount += 1
                if args.verbose and (linecount % 10000) == 0:
                    print(linecount, "...", end='\r')
                if len(csv_parts) < args.fields - 1:
                    print("Must have at least N-1 separators on each "
                          "non-comment non-empty line. Skipping:", csv_line,
                          file=stderr)
                    continue
                if csv_parts[-1].endswith('<-HEADERS'):
                    # skip header line
                    continue
                key = args.separator.join(csv_parts[0:args.fields])
                words[key] = csv_parts
                entry_count += 1
        if args.verbose:
            print("\n", entry_count, "entries in database")
    # join all join files (slow but more workable)
    for join_filename in args.joinfilenames:
        if args.verbose:
            print("Reading joins from", join_filename)
        linecount = 0
        joincount = 0
        with open(join_filename, 'r', newline='') as join_file:
            join_reader = csv.reader(join_file, 
                    delimiter=args.separator, quoting=quoting,
                    strict=True)
            for join_parts in join_reader:
                linecount += 1
                if args.verbose and (linecount % 10000) == 0:
                    print(linecount, "...", end='\r')
                join_on = ''
                if len(join_parts) < args.fields:
                    print("Must have at least N separtors on each",
                        "non-comment non-empty line of join; Skipping:", join_line,
                        file=stderr)
                    continue
                join_on = args.separator.join(join_parts[0:args.fields])
                if join_parts[-1].endswith('<-HEADERS'):
                    # skip header line
                    continue
                if not join_on in words.keys():
                    print("\033[93mMissing!\033[0m "
                          "Could not find the key",
                          join_on, "used by", join_file.name,
                          "line", linecount, "in any of", 
                          args.infilenames, file=stderr)
                else:
                    this_entry = words[join_on]
                    this_entry += [join_parts[args.fields]]
                    words[join_on] = this_entry
                    joincount += 1
                join_line = join_file.readline()
        if args.verbose:
            print("\n", joincount, "joins in that table")
    with open(args.outfilename, "w", newline='') as output:
        if args.verbose:
            print("Writing master database to", args.outfilename)
            print("Sorting")
        print("# This file was automatically generated from", 
                args.infilenames,
                "\n# and",
                args.joinfilenames,
                "\n# using tsvjoin.py\n", file=output)
        linecount = 0
        tsv_writer = csv.writer(output, delimiter=args.separator,
                quoting=quoting, strict=True)
        for (line,fields) in sorted(words.items()):
            linecount += 1
            if args.verbose and ((linecount % 10000) == 0 or linecount == 1):
                print(linecount, "...", end='\r')
            tsv_writer.writerow(fields)
        if args.verbose:
            print()
    exit()


if __name__ == "__main__":
    main()
