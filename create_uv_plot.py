#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script that extracts excitations from TDDFT calculations and plots the
corresponding UV spectra.

Last Update 2016-09-20 by Emmanuel Nicolas
email emmanuel.nicolas-at-cea.fr
Requires Python3 to be installed.
"""

import argparse
import shlex
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
    list_of_raw_files, *plotting_parameters = get_options()

    # Parse all files
    filenames, parsed_files = parse_all_files(list_of_raw_files)

    # For every file, run the routine.
    for i, file in enumerate(parsed_files):
        # Print filename and log information
        print(80 * "=")
        print("=== " + filenames[i])

        # Extract transitions
        transitions = get_transitions(file)
        print("Extracted {0} transitions.".format(len(transitions)))

        # Format transitions and save them in file
        formatted_transitions = format_transitions(transitions)
        write_transitions(formatted_transitions, filenames[i])

        # Setup gnuplot script
        gnuplot_script = write_gnuplot(transitions,
                                       plotting_parameters,
                                       filenames[i])
        print("")

        # Run gnuplot
        os.system('gnuplot {0}'.format(shlex.quote(gnuplot_script)))

    print("All files have been generated.\n")


def get_options():
    """
        Check command line options and accordingly set computation parameters
    """
    parser = argparse.ArgumentParser(description=help_description(),
                                     epilog=help_epilog())
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument('-s', '--sigma', type=float, dest='sigma',
                        default='0.4',
                        help="Sigma value for Gaussian broadening")
    parser.add_argument('-w', '--window', type=str, dest='window',
                        default='200:800', help="Limits for the wavelength")
    parser.add_argument('outFiles', type=str, nargs='+',
                        help='The calculations to plot')

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as error:
        print(str(error))  # Print something like "option -a not recognized"
        sys.exit(2)

    # Test values for validity
    return ([os.path.basename(x) for x in args.outFiles], args.sigma,
            args.window)


def parse_all_files(files):
    """
        Parse all files in list of files
    """
    opened_files = [cclib.io.ccopen(f) for f in files]
    print(files)
    filenames = [f.filename for f in opened_files]
    parsed_files = [f.parse() for f in opened_files]
    return (filenames, parsed_files)


def get_transitions(file):
    """
        Extracts transitions from logfiles
        Returns a list of lists, containing all [transition, oscillator
        strength] couples, in cm-1 and unitless respectively.
    """
    energies = file.etenergies
    oscillator_strengths = file.etoscs
    transitions = zip(energies, oscillator_strengths)
    return list(transitions)


def format_transitions(transitions):
    """
        Reformat transitions into a usable list, e.g. as:
                 353.02         0.2667
                 294.12         0.0000
        In nm an unitless respectively.
    """
    # Convert cm-1 in nm
    transitions_converted = [[round(10E6/x[0], 2), round(x[1], 4)]
                             for x in transitions]
    # Format the list
    transitions_formatted = ['{:.2f}'.format(x[0]).rjust(15) +
                             '{:.4f}'.format(x[1]).rjust(15)
                             for x in transitions_converted]
    return transitions_formatted


def write_gnuplot(transitions, parameters, filename):
    """
        Write gnuplot files
    """

    print(parameters)

    # Process filename
    basename = os.path.splitext(filename)[0]

    # Initialize script
    gnuplot_script = []
    gnuplot_script.append("set terminal png\n")
    gnuplot_script.append("set encoding utf8\n")
    gnuplot_script.append('set output "{0}.png"\n'.format(basename))
    gnuplot_script.append("\n")

    # Style parameters
    gnuplot_script.append("set xrange [{0}]\n".format(parameters[1]))
    gnuplot_script.append("set yrange [0:1]\n")
    gnuplot_script.append("set style line 1 linecolor rgb '#0060ad' "
                          "linetype 1 linewidth 2\n")

    # Add useful functions
    gnuplot_script.append("Band(nu,nu_i,sigma,osc_str) = 1.3062974 * 10**8")
    gnuplot_script.append(" * osc_str / sigma * exp( -( (nu - nu_i)/sigma) )")

    gnuplot_script.append("")
    # Write to file
    gnuplot_name = basename + ".plt"

    with open(gnuplot_name, mode='w') as gnuplot_file:
        # Write script to file
        gnuplot_file.writelines(gnuplot_script)

    # return gnuplot filename
    return gnuplot_name


def write_transitions(transitions, filename):
    """
        Write a file containing the formatted transisions
    """
    dat_name = os.path.splitext(filename)[0] + ".dat"
    with open(dat_name, mode='w', newline="\n") as dat_file:
        # Write transitions to file
        dat_file.write("Wavelength (nm)   Osc Strength\n")
        dat_file.write('\n'.join(transitions))


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
