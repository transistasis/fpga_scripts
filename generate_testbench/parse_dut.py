#!/usr/bin/python3
#
# Name        : parse_dut.py
# Author      : transistasis
# Contact     : transistasis@myfinalheaven.org
# Date        : 6/8/2023
# Description : Parses a Design Under Test (DUT) top-level SystemVerilog file to obtain the following:
#                 1) Parameter fields and values (returned as a list of dictionaries)
#                 2) Port names, directions, dimensionalities, and types (returned as a list of dictionaries)
#
# NOTE:
#   * This module only does cursory syntax checking (directionality and type), so compilation must be checked externally
#   * Port declarations that leverage the signal kind attribute will NOT be processed correctly, as there's no reason to define ports this way
#       e.g. input wire logic clk_i,
#         * This should be written as follows, since they're the same under the hood (no reason to reintroduce attributes that are abstracted away for a reason):
#             input logic clk_i,
#   * Interfaces and user-defined types are NOT processed correctly, as these should NOT be used in the top-level DUT port declarations
#   * Multidimensional packed arrays are supported, though only 1D arrays should be used in top-level DUT port declarations, if desired (I might change this)

import re
import sys

class ParseDut:

  def __init__( self, dut ):
    self.dut = open( dut, 'r' )
    self.dut = str( self.dut.read() )


  ###########################################################################################################
  # Function    : remove_list_whitespace
  # Inputs      : List
  # Outputs     : List
  # Description : Removes the whitespace in a list, stripping the ends of each element and replacing all
  #               whitespace with a single space
  ###########################################################################################################
  def remove_list_whitespace( self, raw_list, regex = r'\s+' ):
    for index, parameter in enumerate( raw_list ):
      raw_list[index] = parameter.strip()
      raw_list[index] = re.sub( regex, ' ', raw_list[index] )

    return raw_list


  ###########################################################################################################
  # Function    : get_raw_parameter_list
  # Inputs      : N/A
  # Outputs     : List
  # Description : Parses the DUT to get a raw list of each defined parameter in a SystemVerilog module
  ###########################################################################################################
  def get_raw_parameter_list( self ):
    self.raw_parameter_list = []

    self.raw_parameter_list = re.findall( r'#\((.*?)\)', self.dut, re.DOTALL )

    if ( self.raw_parameter_list != [] ):
      self.raw_parameter_list = self.raw_parameter_list[0].replace( '\n ', '' ).replace( 'parameter ', '' ).strip()
      self.raw_parameter_list = self.raw_parameter_list.split( ',' )
    else:
      print( 'NOTE: No parameter list was found!\n')

    self.raw_parameter_list = self.remove_list_whitespace( self.raw_parameter_list )

    return self.raw_parameter_list


  ###########################################################################################################
  # Function    : get_parameter_dict
  # Inputs      : List
  # Outputs     : List of dictionaries
  # Description : Processes a raw parameter list to generate a list of parameter dictionaries
  ###########################################################################################################
  def get_parameter_dict( self, raw_parameter_list ):
    self.parameter_dict_list = []

    for index, parameter in enumerate( raw_parameter_list ):
      if ( '=' in parameter ):
        parameter = parameter.split( '=' )
        self.parameter_dict_list.append( { 'name' : parameter[0].strip(), 'value' : parameter[1].strip() } )
      else:
        self.parameter_dict_list.append( { 'name' : parameter.strip(), 'value' : None } )

    return self.parameter_dict_list


  ###########################################################################################################
  # Function    : get_raw_port_list
  # Inputs      : N/A
  # Outputs     : List
  # Description : Parses the DUT to get a raw list of each defined port in a SystemVerilog module
  ###########################################################################################################
  def get_raw_port_list( self ):
    self.raw_port_list = []

    self.raw_port_list = re.findall( r'(?<!#)\((.*)\)', self.dut, re.DOTALL )
    self.raw_port_list = self.raw_port_list[0].replace( '\n ', '' )
    self.raw_port_list = self.raw_port_list.split( ',' )

    self.raw_port_list = self.remove_list_whitespace( self.raw_port_list )

    return self.raw_port_list


  ###########################################################################################################
  # Function    : get_port_dict
  # Inputs      : List
  # Outputs     : List of dictionaries
  # Description : Processes a raw port list to generate a list of port dictionaries
  #               NOTE:
  #                 * Interfaces and user-defined types are NOT supported, as they should NOT be used in the top-level DUT port declarations
  #                 * Multidimensional packed arrays ARE supported, but should still NOT be used in the top-level DUT port declarations
  ###########################################################################################################
  def get_port_dict( self, raw_port_list ):
    self.port_dict_list  = []
    self.port_directions = [ 'input', 'output', 'inout' ]
    self.port_types      = [ 'logic', 'wire',   'tri' ]

    for index, line in enumerate( raw_port_list ):
      # Format multidimensional array indices for processing
      if ( '[' in line ):
        line = re.sub( r'\]\s+\[', '][', line )
        self.line_dimension = re.findall( r'\[.*\]', line, re.DOTALL )
        self.line_dimension = ''.join( self.line_dimension )
      else:
        self.line_dimension = None

      # Create a list from a port declaration line
      line = line.split( ' ' )

      # Process and check each port direction (will always be at Index 0 of the port declaration list)
      if ( any( signal_direction in line for signal_direction in self.port_directions ) ):
        self.line_direction = line[0]
      else:
        print( "\nERROR: Port direction must be 'input', 'output', or 'inout':\n" )
        print( "\t" + line[0] + '\n' )
        sys.exit()

      # Process and check each port type (will always be at Index 1 of the port declaration list)
      if ( any( signal_type in line for signal_type in self.port_types ) ):
        self.line_type = line[1]
      else:
        print( "\nERROR: Port type must be 'logic', 'wire', or 'tri':\n" )
        print( "\t" + line[1] + '\n' )
        sys.exit()

      # Capture the signal name (will always be the last element of the port declaration list)
      self.line_name = line[-1]

      # Add the port declaration information for a given line to the list of dictionaries
      self.port_dict_list.append( { 'name' : self.line_name, 'direction' : self.line_direction, 'type' : self.line_type, 'dimension' : self.line_dimension } )

    return self.port_dict_list


  ###########################################################################################################
  # Function    : parse_dut
  # Inputs      : N/A
  # Outputs     : List of dictionaries for both parameters and ports
  # Description : Processes the parameter and port lists for the DUT and stores them as lists of dictionaries
  ###########################################################################################################
  def parse_dut( self ):
    # Parameters
    self.get_raw_parameter_list()
    self.get_parameter_dict( self.raw_parameter_list )

    # Ports
    self.get_raw_port_list()
    self.get_port_dict( self.raw_port_list )



if ( __name__ == '__main__' ):
  pd = ParseDut( "test/dut_with_parameters.sv" )
  pd.parse_dut()

  for element in pd.parameter_dict_list:
    print( element )

  for element in pd.port_dict_list:
    print( element )