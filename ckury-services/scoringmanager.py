from scoring import score_csv
from HTMLtoCSV import extract_data
import sys, os

if __name__ == "__main__":
    option = sys.argv[1]
    args = sys.argv[2:]

    if option == "HTMLtoCSV":
        inputdir = args[0]
        outputdir = args[1]

        for input in os.listdir(inputdir):
            extract_data(inputdir + '/' + input, outputdir + '/' + input.split(".")[0] + ".csv")

    if option == "Score":
        inputdir = args[0]
        outputdir = args[1]
        keyworddir = args[2]

        for keywordfile in os.listdir(keyworddir):
            keywordname = keywordfile.split('.')[0]
            score_csv(inputdir, keyworddir + '/' + keywordfile, outputdir + '/' + keywordname)

    if option == "Summarize":
        inputdir = args[0]
        outputdir = args[1]