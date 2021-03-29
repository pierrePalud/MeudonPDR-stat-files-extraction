# MeudonPDR-stat-files-extraction

Extraction of integrated intensities of a set of lines for a grid of simulations of Meudon PDR code

# Installation

Simply clone this repository. No additional installation is needed.

To run the present code, please check that you have python installed with basic packages (pandas, numpy, tqdm). 

# Usage

To extract the results of a simulation grid :

1. Put all the .in files in one folder (here, `./data/PDR17G1E20_n_PDRIN`)
2. Put all the results files from the simulation (_s_20.stat) in one folder (here, `PDR17G1E20_n_Results`)
3. Indicate in a csv file the names of the parameters you want to extract from the .in files and the corresponding names you want in your final file (cf `input_params.csv` as an example)
4. Indicate in a csv file the names of the spectral lines you want to extract from the .stat files and the corresponding names you want in your final file (cf `lines_to_extract.csv` as an example)
5. choose a name for the file that will contain the result of the extraction (by default `grid.dat`)

And then run 

```
python main.py
```

Notes
* that I let 3 simulations (.in and .stat) in this repo and the necessary files set for an extraction (in the utils fodler). As a first test, I recommend you run directly `python main.py` after installing to test. 

* In case you change the names indicated as examples above, indicate the new value when you run the program. If you want to check the documentation for available arguments :

```
python main.py -h
```