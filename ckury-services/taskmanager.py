import sys
import yaml
from google.cloud import datastore

def getTaskForVM():
    client = datastore.Client()
    query = client.query(kind="Task_List")

    query.add_filter(property_name="Status", operator="=", value="Waiting")
    
    try:
        task = list(query.fetch(limit=1))[0]
    except IndexError:
        return f'Failed, no task found. Check kind=Task_List for status "Waiting"'

    task["Status"] = "Claimed"
    task["Status_Message"] = "VM claimed task and is preparing to process"

    client.put(task)

    data = {"Id": task.key.id, "Kind": task.key.kind, "Input_File": task['Input_File'], "Keyword_List": task['Keyword_List'], "Yahoo_Ticker": task['Yahoo_Ticker'], "DateTime": task['DateTime']}

    with open("task.yaml", "w") as taskfile:
        taskfile.write(yaml.dump(data))

    return f'Success, Claimed task: {task.key.id}, and wrote to taskfile.yaml'

def getFromYAML(tag):
    with open("task.yaml", "r") as taskfile:
        data = yaml.safe_load(taskfile)
    return data.get(tag)

if __name__ == "__main__":
    option = sys.argv[1]

    if option == "get-task":
        print(getTaskForVM())

    if option == "task-inputfile":
        print(getFromYAML("Input_File"))

    if option == "task-keywordlocations":
        print(getFromYAML("Keyword_List"))

    if option == "task-ticker":
        print(getFromYAML("Yahoo_Ticker"))

    if option == "task-datetime":
        print(getFromYAML("DateTime"))
