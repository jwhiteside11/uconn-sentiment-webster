#! /bin/bash

machinename=$(uname -n)

gcloud logging write production_log "${machinename}: New VM Created"

curl -H 'Cache-Control: no-cache, no-store' -o shutdown-script.sh https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/shutdown-script.sh

curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

cd /
mkdir sentiment-data

cd sentiment-data/

apt install -y python3-pip
gcloud logging write production_log "${machinename}: Installed pip"

curl -H 'Cache-Control: no-cache, no-store' -o requirements.txt https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/requirements.txt
gcloud logging write production_log "${machinename}: Downloaded requirements.txt"

python3 -m pip install -r requirements.txt --break-system-packages

curl -H 'Cache-Control: no-cache, no-store' -o taskmanager.py https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/taskmanager.py
gcloud logging write production_log "${machinename}: Downloaded taskmanager"

gcloud logging write production_log "${machinename}: taskmanager: $(python3 taskmanager.py get-task)"

mkdir html_files/
gcloud storage cp gs://production_upload_data_sentiment-analysis-379200/Raw_CC/$(python3 taskmanager.py task-inputfile)/* html_files/

gcloud logging write production_log "${machinename}: Downloaded inputs ${input_file}"

keywordlocations=$(python3 taskmanager.py task-keywordlocations)
ticker=$(python3 taskmanager.py task-ticker)
datetime=$(python3 taskmanager.py task-datetime)

curl -H 'Cache-Control: no-cache, no-store' -o keywordcollector.py https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/keywordcollector.py
gcloud logging write production_log "${machinename}: Downloaded keywordcollector"

mkdir keywords/
python3 keywordcollector.py ${keywordlocations} keywords/
gcloud logging write production_log "${machinename}: Downloaded keywords"

curl -H 'Cache-Control: no-cache, no-store' -o requirements.txt https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/requirements.txt
python3 -m pip install -r requirements.txt --break-system-packages

curl -H 'Cache-Control: no-cache, no-store' -o scoringmanager.py https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/scoringmanager.py
curl -H 'Cache-Control: no-cache, no-store' -o HTMLtoCSV.py https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/HTMLtoCSV.py
curl -H 'Cache-Control: no-cache, no-store' -o scoring.py https://raw.githubusercontent.com/ckury/uconn-sentiment-backend/main/scoring.py

mkdir input_files/
python3 scoringmanager.py HTMLtoCSV html_files/ input_files/
gcloud logging write production_log "${machinename}: Converted HTMLs to CSVs"

mkdir scored_files/
python3 scoringmanager.py Score input_files/ scored_files/ keywords/
gcloud logging write production_log "${machinename}: Scored transcripts"

mkdir scored_summarized_files/
python3 scoringmanager.py Summarize scored_files/ scored_summarized_files/
gcloud logging write production_log "${machinename}: Summarized unweighted scores"

# python3 uploading.py scored_files/ Detailed ${keywordlocations} ${ticker} ${datetime}
# python3 uploading.py scored_summarized_files/ weighted_summarized_files/ Summary ${keywordlocations} ${ticker} ${datetime}

cd /
bash ./shutdown-script.sh