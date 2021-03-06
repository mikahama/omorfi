#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
This script converts Finnish TSV-formatted lexicon to github wiki
"""


# Author: Tommi A Pirinen <flammie@iki.fi> 2009, 2011

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
#

import argparse
import csv
from sys import stderr


# standard UI stuff


def main():
    # initialise argument parser
    ap = argparse.ArgumentParser(
        description="Convert omorfi database to github pages")
    ap.add_argument("--quiet", "-q", action="store_false", dest="verbose",
                    default=False,
                    help="do not print output to stdout while processing")
    ap.add_argument("--verbose", "-v", action="store_true", default=False,
                    help="print each step to stdout while processing")
    ap.add_argument("--paradigm-docs", "-P", action="append", required=True,
                    metavar="PDFILE", help="read paradigm docs from PDFILEs")
    ap.add_argument("--paradigms", "-A", required=True,
                    metavar="PARAFILE",
                    help="read paradigm data from PARAFILE")
    ap.add_argument("--version", "-V", action="version")
    ap.add_argument("--output", "-o", action="store", required=True,
                    type=argparse.FileType('w'),
                    metavar="OFILE", help="write docs OFILE")
    ap.add_argument("--outdir", "-O", action="store", required=True,
                    metavar="ODIR", help="write individual paradigms to " +
                    "ODIR/paradigm.md")
    ap.add_argument("--fields", "-F", action="store", default=2,
                    metavar="N", help="read N fields from master")
    ap.add_argument("--separator", action="store", default="\t",
                    metavar="SEP", help="use SEP as separator")
    ap.add_argument("--comment", "-C", action="append", default=["#"],
                    metavar="COMMENT",
                    help="skip lines starting with COMMENT that"
                    "do not have SEPs")
    ap.add_argument("--strip", action="store",
                    metavar="STRIP",
                    help="strip STRIP from fields before using")

    args = ap.parse_args()

    # write preamble to wiki page
    print('# Paradigms', file=args.output)
    print(file=args.output)
    print("_This is an automatically generated documentation based on omorfi" +
          " lexical database._", file=args.output)
    print(file=args.output)
    print("Paradigms are sub-groups of lexemes that have unique " +
          "morpho-phonological features. " +
          "In omorfi database there is a unique " +
          "paradigm for every possible combination of certain features:",
          file=args.output)
    print(file=args.output)
    print("* Universal Part-of-speech", file=args.output)
    print("* Morphophonology, such as: vowel harmony, gradation pattern, " +
          " stem variations and allomorph selection", file=args.output)
    print("* Other morphotactic limitations, such as: only plurals allowed, " +
          " obligatory possessive suffixes, etc.", file=args.output)
    print(file=args.output)
    print("All other lexical information is coded on per lexeme basis",
          file=args.output)
    print("## Paradigms in alphabetical order", file=args.output)
    print(file=args.output)
    print("* The _Notes_ column is informal hints for lexicographers to " +
          "discriminate the classes, for further details each paradigm has " +
          "their own page with details and exampels linked ", file=args.output)
    print("* The _KOTUS_ column is official dictionary class, if you are  " +
          "familiar with Finnish dictionaries. ", file=args.output)
    print("* The _Harmony_ column is vowel harmony; back, front, both or N/A",
          file=args.output)
    print("* The _Inflection tables_ column links to inflection tables of the" +
          " example word, *full* for full-form list and *short* for " +
          "wiktionary-style inflection tables.", file=args.output)
    # read from csv files
    print(file=args.output)
    print("| **Paradigm** | **UPOS** | _Notes_ | KOTUS | Harmony | Infl. " +
          "Tables |", file=args.output)
    print("|:-------------|---------:|:--------|------:|:-------:|:------" +
          "-------|", file=args.output)

    paradata = dict()
    with open(args.paradigms) as tsv_file:
        tsv_reader = csv.DictReader(tsv_file, delimiter=args.separator,
                                    strict=True)
        for tsv_parts in tsv_reader:
            paradata[tsv_parts['new_para']] = dict()
            for key in tsv_parts.keys():
                if key != 'new_para':
                    paradata[tsv_parts['new_para']][key] = tsv_parts[key]
    paradigms = set(paradata.keys())
    for tsv_filename in args.paradigm_docs:
        if args.verbose:
            print("Reading from", tsv_filename)
        linecount = 0
        # for each line
        with open(tsv_filename, 'r', newline='') as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter=args.separator,
                                        strict=True)
            for tsv_parts in tsv_reader:
                linecount += 1
                if len(tsv_parts) < 2:
                    print("Too few tabs on line", linecount,
                          "skipping following line completely:", file=stderr)
                    print(tsv_parts, file=stderr)
                    continue
                outfilename = args.outdir + \
                    tsv_parts['new_para'].replace('?', '_').replace('_', '/',
                                                                    1)
                outfile = open(outfilename + '.markdown', 'w')
                print('---', file=outfile)
                print('layout: paradigm', file=outfile)
                print('paradigm:', tsv_parts['new_para'], file=outfile)
                print('---', file=outfile)
                print("### `", tsv_parts['new_para'], "`",
                      file=outfile)
                print(file=outfile)
                print('* _' + tsv_parts['doc'] + '_', file=outfile)
                if tsv_parts['new_para'] in paradata:
                    if not tsv_parts['doc']:
                        print("missing DOC:", tsv_parts['new_para'])
                        exit(1)
                    if len(tsv_parts['doc']) > 40:
                        docshort = tsv_parts['doc'][:40] + '...'
                    else:
                        docshort = tsv_parts['doc']
                    if paradata[tsv_parts['new_para']]['kotus_tn'] == 99:
                        kotus = '[N/A](#kotus_exceptions)'
                    else:
                        kotus = paradata[tsv_parts['new_para']]['kotus_tn']
                        if paradata[tsv_parts['new_para']]['kotus_av'] !=\
                                'None':
                            kotus = kotus + "-" + \
                                paradata[tsv_parts['new_para']]['kotus_av']
                    if paradata[tsv_parts['new_para']]['harmony'] == 'None':
                        harmony = 'N/A'
                    else:
                        harmony = paradata[tsv_parts['new_para']]['harmony']
                    # organise non-doc values as doc:
                    print("* Universal POS is",
                          paradata[tsv_parts['new_para']]['upos'],
                          "and legacy POS is",
                          paradata[tsv_parts['new_para']]['pos'],
                          file=outfile)
                    if harmony == 'both':
                        print("* suffixes can use " +
                              "both vowel harmonies", file=outfile)
                    elif harmony == 'N/A':
                        print("* no vowel harmony applies to this paradigm",
                              file=outfile)
                    else:
                        print("* suffixes use", harmony, "vowel harmony",
                              file=outfile)
                    if 'N/A' not in kotus:
                        print("* KOTUS paradigm used in",
                              "their dictionary is", kotus, file=outfile)
                    else:
                        print("* This paradigm could not be mapped to",
                              "dictionary's classification scheme",
                              file=outfile)
                    if paradata[tsv_parts['new_para']]['deletion'] != 'None':
                        print("* The lemmas must end in *",
                              paradata[tsv_parts['new_para']]['deletion'],
                              "* (which will be deleted to form an",
                              "invariant stub) and the regex matching the",
                              "lemma is `",
                              paradata[tsv_parts['new_para']]['suffix_regex'],
                              "`", file=outfile)
                    else:
                        print("* There is no lemma suffix pattern",
                              "for this paradigm", file=outfile)
                    if paradata[tsv_parts['new_para']]['plurale_tantum'] != \
                            'False':
                        print("* This is a [plurale tantum](" +
                              "https://en.wikipedia.org/wiki/Plurale_tantum" +
                              ") paradigm for plural only nominals.",
                              file=outfile)
                    # something XXX:
                    paradigms.remove(tsv_parts['new_para'])
                else:
                    print("found in docs but not in data:",
                          tsv_parts['new_para'], file=stderr)
                    exit(1)
                print(file=outfile)
                print("## See also", file=outfile)
                print(file=outfile)
                genfilename = outfilename.split("/")[-1]
                if 'PROPN' not in outfilename:
                    genfilename = genfilename[0].upper() + '/' + \
                        genfilename.lower()
                else:
                    genfilename = genfilename[0].upper() + '/' + \
                        genfilename[0] + genfilename[1:].lower()
                genfilename = "gen/" + genfilename
                genfilename = genfilename.replace("51", "")
                print("* Inflection tables: " +
                      "[full](" + genfilename + ".html), [short](" +
                      genfilename + "_wikt.html)", file=outfile)
                print(file=outfile)
                print("| " + " [" + tsv_parts['new_para'] + "](" +
                      outfilename + ".html) | " +
                      paradata[tsv_parts['new_para']]['upos'] + " | " +
                      docshort + " | " + kotus + " | " + harmony + " | " +
                      "[full](" + genfilename + ".html) [short](" +
                      genfilename + "_wikt.html) |", file=args.output)
    if paradigms:
        print("Undocumented paradigms left:", ", ".join(paradigms),
              file=stderr)
    print('''<!-- vim: set ft=markdown:-->''', file=args.output)
    exit()


if __name__ == "__main__":
    main()
