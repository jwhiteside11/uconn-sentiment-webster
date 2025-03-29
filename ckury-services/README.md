# CODE MERGE AND CLEANUP IN-PROGRESS
	
# Sentiment Project Backend
This repository holds all of the code needed by the virtual machine to:
1. Score conference calls
2. Summarize data
3. Upload data to cloud datastore. 

Please note that most of this code has been developed by others and only was cleaned up by me and consolidated into a single repository to improve the ease of cloning data into the virtual machine.

# API reference
This code is wrapped with a Flask server. Interact with this code base using HTTP calls to `localhost:5200`. 

In the examples below, I use the `curl` shell command, but you can interface with the containers any HTTP library in any language.

## Endpoints

### POST /score_text

Perform sentiment analysis on text, returns sentiment score and magnitude.

#### Request
- **Method**: POST
- **URL**: `/score_text`
- **Content-Type**: `application/json`

#### Data
| Key    | Type   | Description                        |
|--------------|--------|------------------------------------|
| `text_content`       | str    | The text to score (required). |

#### Example Request
`curl -d '{"text_content": "Example body of text."}' -H "Content-Type: application/json" localhost:5200/score_text`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
{
  "score": 0.00372, 
  "magnitude": 4.929653806909
}
```