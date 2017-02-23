#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script that extracts coordinates from many ADF files, in order to create an ESI
for a paper.
Last Update 2016-09-20 by Emmanuel Nicolas
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
    output_format = runvalues['output_format']
    # Parse all files
    parsed_files = parse_all_files(list_of_raw_files)

    # For every file, create output
    if output_format == 'xyz':
        for file in parsed_files:
            filename = list_of_raw_files[parsed_files.index(file)]
            write_xyz(file, filename)
    elif output_format == 'cif':
        write_cif(parsed_files, list_of_raw_files,
                  runvalues['output_filename'])


def get_options():
    """
        Check command line options and accordingly set computation parameters
    """
    parser = argparse.ArgumentParser(description=help_description(),
                                     epilog=help_epilog())
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument('-o', '--output', type=str, dest='output_format',
                        default='xyz', help="Output format for the ESI")
    parser.add_argument('-f', '--filename', type=str, dest='output_filename',
                        default='output.cif', help="File name for the output")
    parser.add_argument('outFiles', type=str, nargs='+',
                        help='The ADF output files to submit')

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as error:
        print(str(error))  # Print something like "option -a not recognized"
        sys.exit(2)

    runvalues = dict.fromkeys(['files', 'output_format', 'output_filename'])
    # Get values from parser
    runvalues['files'] = [os.path.basename(x) for x in args.outFiles]
    runvalues['output_format'] = args.output_format
    runvalues['output_filename'] = args.output_filename

    # Test values for validity
    return runvalues


def parse_all_files(files):
    """
        Parse all files in list of files
    """
    opened_files = [cclib.io.ccopen(f) for f in files]
    parsed_files = [f.parse() for f in opened_files]
    return parsed_files


def extract_atom_coordinates(file):
    """
        Extracts atom coordinates from every file in list
    """
    if file.atomcoords.ndim == 3:
        atom_coordinates = file.atomcoords[-1].tolist()
    else:
        atom_coordinates = file.atomcoords.tolist()
    return atom_coordinates


def write_cif(parsed_files, list_of_raw_files, filename):
    """
        Take data from parsed_files and create a valid cif file.
    """
    coordinates = []
    number_of_atoms = []
    atoms = []
    periodic_table = cclib.parser.utils.PeriodicTable()

    for file in parsed_files:
        # Take last item of coordinates, i.e. the optimized ones.
        coordinates.append(file.atomcoords[-1].tolist())
        # Retrieve number of atoms
        number_of_atoms.append(file.natom)
        # Retrieve atomic numbers
        atoms.append(file.atomnos.tolist())

    output = []
    for i, coords in enumerate(coordinates):
        # Retrieve file name
        output.append(str(os.path.splitext(list_of_raw_files[i])[0]))
        # Add number of atoms
        # output.append(str(number_of_atoms[i]))
        # Append atom coordinates
        for j, atomcoords in enumerate(coords):
            # Take every atom, print it as:
            # H         0.000123       0.000456      -1.234567
            output.append(periodic_table.element[atoms[i][j]].ljust(3) +
                          " ".join(['{:,f}'.format(a).rjust(15)
                                    for a in atomcoords]))
        # Add a line break after the molecule
        output.append("\n")

    # Final line break
    output.append("\n")
    with open(filename, mode='w') as output_file:
        output_file.write('\n'.join(output))


def write_xyz(file, filename):
    """
        Take file, write xyz coord in txt file with same name.
    """
    # Extract xyz line straight from cclib
    xyz = str(file.writexyz())
    # Refactor the string, remove first two lines plus add \n at the end
    xyz = xyz.split(sep='\n')
    xyz = '\n'.join(xyz[2:]) + '\n'
    # Build output name from filename
    basename = os.path.splitext(filename)[0]
    output_file = basename + ".txt"
    with open(output_file, mode='w') as output:
        output.write(xyz)


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
