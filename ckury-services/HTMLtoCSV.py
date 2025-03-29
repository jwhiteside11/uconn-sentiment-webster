from bs4 import BeautifulSoup
import sys

def extract_data(htmlfile, outputfile):

    with open(htmlfile, 'r') as f:
        soup = BeautifulSoup(f.read(), features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    lines = [line.strip() for line in text.splitlines()]

    with open(outputfile, 'w') as f:
        for line in lines:
            if line == '':
                continue

            f.write(line + "\n")

if __name__ == '__main__':
    htmlfile = sys.argv[1]
    outputfile = sys.argv[2]

    extract_data(htmlfile=htmlfile, outputfile=outputfile)
