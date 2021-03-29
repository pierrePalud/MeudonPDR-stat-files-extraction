import sys
import glob
import os

import numpy as np
import pandas as pd

from tqdm.auto import tqdm

import argparse


def extract_input_parameters(path_file_in, df_input_params, dict_result={}):
   """extracts the data from the input file of the simulation

   Parameters
   ----------
   path_file_in : string
       relative path to the file that contains the input of the simulation
   df_input_params : pd.Series
       names of the parameters to extract in the input files with the corresponding
       names wanted in the final file 
   dict_result : dict, optional
       previous state of the dict containing the extracted data, by default {}

   Returns
   -------
   dict_result : dict
       new state of the dict containing the extracted data
   """
   with open(path_file_in) as f:
      lines = f.readlines()

      # for each parameter we want to extract, read the file line by line until we find
      # the corresponding one 
      for param_key in df_input_params.index:
         param_name = df_input_params.at[param_key]
         for line in lines:
            if param_key in line:
               dict_result[param_name] = line.split()[0]
               break
               
         if param_name not in dict_result.keys():
            raise NameError(f"parameter {param_key} not in file {path_file_in}")

   return dict_result


def extract_result_data(path_file_result, df_lines_to_extract, dict_result={}):
   """extracts the data from the result file of the simulation

   Parameters
   ----------
   path_file_result : string 
       relative path to the file that contains the results of the simulation
   df_lines_to_extract : pd.Series
       names of the transitions to extract in the result files with the corresponding
       names wanted in the final file
   dict_result : dict, optional
       previous state of the dict containing the extracted data, by default {}

   Returns
   -------
   dict_result : dict
       new state of the dict containing the extracted data   
   """
#   ListQuant_Flags = [0] * len(df_lines_to_extract)
#   index = -1
   with open(path_file_result) as f:
      lines = f.readlines()

      # for each transition intensity we want to extract, read the file line by line
      #  until we find the corresponding one 
      for quant_key in df_lines_to_extract.index:
         quant_name = df_lines_to_extract.at[quant_key]
#         index += 1
         for line in lines:
            if line.startswith(f"value {quant_key}"):
               dict_result[quant_name] = line.split(" # ")[2]
#               ListQuant_Flags[index] = 1
               break
         
         if quant_name not in dict_result.keys():
            raise NameError(f"name {quant_key} is not in results file {path_file_result}")

   return dict_result


def process_one_simulation(filename_result, path_pdr_in, path_results, df_input_params, df_lines_to_extract):
   """extracts the data corresponding to a simulation (this
   simulation is identified with the name of the result file)

   Parameters
   ----------
   filename_result : string
       name of the file containing the results of the simulation
       (this name allows to retrieve the simulation input file)
   path_pdr_in :str
       path to the input files (.in) of the grid simulation
   path_results : str
       path to the results files (.stat) of the grid simulation
   df_input_params : pd.Series
       names of the parameters to extract in the input files with the corresponding
       names wanted in the final file 
   df_lines_to_extract : pd.Series
       names of the transitions to extract in the result files with the corresponding
       names wanted in the final file

   Returns
   -------
   dict
       contains all the columns that we want to extract (that 
       are listed in the the ordered dict in utils.constants) 
   """
   dict_result = {}

   # get input parameters
   root_filename_in = filename_result.split("_s_20.stat")[0]
   path_file_in = f"{path_pdr_in}/{root_filename_in}.in"
   dict_result = extract_input_parameters(path_file_in, df_input_params, dict_result)

   # get result data
   path_file_result = f"{path_results}/{filename_result}"
   dict_result = extract_result_data(path_file_result, df_lines_to_extract, dict_result)

   return dict_result
   

def write_header(filename_out, df_input_params, df_lines_to_extract):
   """automatically writes the header of the output file using the names in 
   the csv files

   Parameters
   ----------
   filename_out : string
       name of the output file in which the data should be written
   df_input_params : pd.Series
       names of the parameters to extract in the input files with the corresponding
       names wanted in the final file 
   df_lines_to_extract : pd.Series
       names of the transitions to extract in the result files with the corresponding
       names wanted in the final file
   """
   col_names = list(df_input_params.values) + list(df_lines_to_extract.values)
   col_names = [f"[{('00' + str(i+1))[-3:]}]{col}" for i, col in enumerate(col_names)]

   # longest name string
   max_len = max([len(col) for col in col_names])

   # list of cols
   header = "#"
   for i, col_name in enumerate(col_names):
      header += col_name + " " * (max_len + 1 - len(col_name))
      if (i+1) % 5 == 0:
         header += "\n#"

   # [001]   [002]   etc. row
   header += "\n#" + 4*" " 
   header += (" " * 8).join([
      f"[{('00' + str(i+1))[-3:]}]" for i in range(len(col_names))
   ])
   header += "\n"

   # write header to file
   with open(filename_out, "w") as f:
      f.write(header)


def write_data(filename_out, list_results):
   """writes the data extracted from input and result files to 
   filename_out

   Parameters
   ----------
   filename_out : string
       name of the output file in which the data should be written
   list_results : list of dict
       data to be written
   """
   # convert the list of dicts to a dataframe
   df = pd.DataFrame(list_results)
   for col in df.columns:
      df[col] = df[col].apply(lambda x: f"{float(x):.4E}")

   # fuse the columns of the dataframe
   df_1col = df.apply(lambda row: "   ".join(list(row)), 1)

   # save to output file
   df_1col.to_csv(filename_out, index=False, header=False, mode="a")



def check_arguments(path_pdr_in, path_results, filename_out, filename_input_params, filename_lines_to_extract):
   """checks the validity of the arguments passed through CLI
   """
   print("Starting extraction for :")
   print(f"--path_pdr_in : \t\t{path_pdr_in}")
   assert os.path.isdir(path_pdr_in), f"the indicated path ({path_pdr_in}) does not seem to exist."
   list_filenames_pdr_in = sorted(glob.glob(f"{path_pdr_in}/*.in"))
   assert len(list_filenames_pdr_in) > 0, f"There seem to be no .in files in the {path_pdr_in} directory."
   
   print(f"--path_results : \t\t{path_results}")
   assert os.path.isdir(path_results), f"the indicated path ({path_results}) does not seem to exist."
   list_filenames_results = sorted(glob.glob(f"{path_results}/*_s_20.stat"))
   assert len(list_filenames_results) > 0, f"There seem to be no .stat files in the {path_results} directory."


   print(f"--filename_out : \t\t{filename_out}")
   assert ".dat" in filename_out, f"The output file needs to be a .dat file. You indicated {filename_out}"

   print(f"--filename_input_params : \t{filename_input_params}")
   assert os.path.isfile(filename_input_params), f"the file {filename_input_params} does not seem to exist. Please check the path."
   
   print(f"--filename_lines_to_extract : \t{filename_lines_to_extract}")
   assert os.path.isfile(filename_lines_to_extract), f"the file {filename_lines_to_extract} does not seem to exist. Please check the path."
   




def main(path_pdr_in, path_results, filename_out, filename_input_params, filename_lines_to_extract):
   """Extraction of integrated intensities of a set of lines for a grid of simulations of Meudon PDR code

   Parameters
   ----------
   path_pdr_in : str
       path to the input files (.in) of the grid simulation
   path_results : str
       path to the results files (.stat) of the grid simulation
   filename_out : str
       name of the file (.dat) in which the result of the extraction is to be saved
   filename_input_params : str
       name of the file (.csv) that contains the list of params to extract from .in files
   filename_lines_to_extract : str
       name of the file (.csv) that contains the list of lines to extract from .stat files
   """
   # import input data into dataframe and convert to pd.Series
   df_input_params = pd.read_csv(filename_input_params)
   df_input_params = df_input_params.set_index("name_in_file")['param_name']

   # import result data into dataframe and convert to pd.Series
   df_lines_to_extract = pd.read_csv(filename_lines_to_extract)
   df_lines_to_extract = df_lines_to_extract.set_index("name_in_file")['transition_name']

   # list of names of results files
   list_filenames_results = sorted(glob.glob(f"{path_results}/*_s_20.stat"))
   list_filenames_results = [filename.split("/")[-1] for filename in list_filenames_results]

   # extract data from files
   list_results = []
   for filename_result in tqdm(list_filenames_results):
      dict_result = process_one_simulation(
         filename_result, path_pdr_in, path_results, 
         df_input_params, df_lines_to_extract
         )
      list_results.append(dict_result)

   # save results
   write_header(filename_out, df_input_params, df_lines_to_extract)
   write_data(filename_out, list_results)

   print("Extraction successfull.")




if __name__ == "__main__":
   msg = "Extraction of integrated intensities of a set of lines for a grid of simulations of Meudon PDR code"
   parser = argparse.ArgumentParser(msg)

   parser.add_argument(
      "-pi", "--path_pdr_in", default="./data/PDR17G1E20_n_PDRIN",
      help="path to the input files (.in) of the grid simulation")
   parser.add_argument(
      "-pr", "--path_results", default="./data/PDR17G1E20_n_Results",
      help="path to the results files (.stat) of the grid simulation")
   parser.add_argument(
      "-fo", "--filename_out", default="grid.dat",
      help="name of the file (.dat) in which the result of the extraction is to be saved")
   parser.add_argument(
      "-fip", "--filename_input_params", default='./utils/input_params.csv',
      help="name of the file (.csv) that contains the list of params to extract from .in files")
   parser.add_argument(
      "-flte", "--filename_lines_to_extract", default='./utils/lines_to_extract.csv',
      help="name of the file (.csv) that contains the list of lines to extract from .stat files")

   args = parser.parse_args()


   check_arguments(
      args.path_pdr_in, 
      args.path_results, 
      args.filename_out, 
      args.filename_input_params, 
      args.filename_lines_to_extract
   )

   main(
      args.path_pdr_in, 
      args.path_results, 
      args.filename_out, 
      args.filename_input_params, 
      args.filename_lines_to_extract
   )