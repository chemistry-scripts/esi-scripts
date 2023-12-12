#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script that extracts energies for many Gaussian log files.
Last Update 2023-10-02 by Emmanuel Nicolas
email emmanuel.nicolas -at- cea.fr
Requires Python3 to be installed.
"""

import argparse
import sys
import os
import cclib


def main():
    """
        Main function.
        Retrieves names of files to extract, eventual parameters, starts
        extraction, exports the results in txt files.
    """
    # Get parameters from command line
    runvalues = get_options()
    list_of_raw_files = runvalues['files']
    # Parse all files
    parse_all_files(list_of_raw_files, runvalues['full'])


def get_options():
    """
        Check command line options and accordingly set computation parameters
    """
    parser = argparse.ArgumentParser(description=help_description(),
                                     epilog=help_epilog())
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument('logFiles', type=str, nargs='+',
                        help='The Gaussian log files from which to extract the relevant energies.')

    parser.add_argument("-s", "--short", help="Shorthand print", action="store_true")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as error:
        print(str(error))  # Print something like "option -a not recognized"
        sys.exit(2)

    runvalues = dict.fromkeys(['files', 'full'])
    # Get values from parser
    runvalues['files'] = [os.path.basename(x) for x in args.logFiles]
    if args.short:
        runvalues['full'] = False
    else:
        runvalues['full'] = True
    # Test values for validity
    return runvalues


def extract_data(file):
    energies = dict()
    with open(file, 'r') as file:
        for line in file:
            if line[1:9] == 'SCF Done':
                energies['scf_energy'] = float(line.split()[4])
            if "Zero-point correction" in line:
                energies['zpve'] = float(line.split()[2])
            if "Thermal correction to Energy" in line:
                energies['energy'] = float(line.split()[4])
            if "Thermal correction to Enthalpy" in line:
                energies['enthalpy'] = float(line.split()[4])
            if "Thermal correction to Gibbs Free Energy" in line:
                energies['gibbsenergy'] = float(line.split()[6])
    return energies


def parse_all_files(files, full):
    """
        Parse all files in list of files
    """
    for file in files:
        data = extract_data(file)
        if full:
            print_energies(data, file)
        else:
            print_energies_short(data, file)


def print_energies(data, filename):
    """
        Print energies as a tab-separated single line with:
        fileName -> SCF Energy -> ZPE Correction -> E correction -> H correction -> G Correction
    """
    name = os.path.splitext(filename)[0]
    printout = [name, data['scf_energy'], data['zpve'], data['energy'], data['enthalpy'], data['gibbsenergy']]
    printout = [str(i) for i in printout]

    print('\t'.join(printout))


def print_energies_short(data, filename):
    """
        Print energies as a tab-separated single line with:
        fileName -> SCF Energy -> ZPE Correction -> E correction -> H correction -> G Correction
    """
    name = os.path.splitext(filename)[0]
    printout = [name, data['scf_energy'], data['enthalpy'], data['gibbsenergy']]
    printout = [str(i) for i in printout]

    print('\t'.join(printout))


def help_description():
    """
        Returns description of program for help message
    """
    return ""


def help_epilog():
    """
        Returns additionnal help message
    """
    return ""


if __name__ == '__main__':
    main()
