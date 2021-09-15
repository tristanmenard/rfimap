# rfi_propagation_mapper
RFI propagation mapping based on rasp, a python implementation of the Longey-Rice signal propagation model

September 14 2021 -- TAFL transmitter data currently has a delimiter error in the CSV file. If you encounter `ValueError: could not convert string to float: '7K60F1W'`, you should edit the TAFL_LTAF.csv file (found in your cache directory) manually. Simply replace the first `"` after E369 on line 127551 with `'`. 
