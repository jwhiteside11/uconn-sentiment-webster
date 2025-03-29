'''Module summarizes scores for sentiment project'''

import os
import pandas as pd

def summarize_csv(input_location, output_location):
    '''
    summarize_CSV Takes a CSV (created from output_df in scoring.py) and summarizes all columns
    conforming to project specs and outputs a CSV with the summarized data.
    '''
    for input_file_name in os.listdir(input_location):
        input_df = pd.read_csv(input_location + "/" + input_file_name)

        print(input_df)

        # output_df.to_csv(output_location + '/' + input_file_name, index=False)