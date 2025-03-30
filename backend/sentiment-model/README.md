# Sentiment Scoring Model

This repository holds all of the code needed by the virtual machine to provide a sentiment score for a block of text.

## From past students' works

This code was copied into this respository from [ckury's backend repo](https://github.com/ckury/uconn-sentiment-backend), leaving behind everything but the sentiment scoring functionality. As with all the services, it is exposed as a Flask server.

# API reference
Interact with the flask server using HTTP calls to `localhost:5400`. 

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