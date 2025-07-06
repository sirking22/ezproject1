import requests

url = "https://api.notion.com/v1/databases/d09df250ce7e4e0d9fbe4e036d320def/query"
headers = {
    "Authorization": "Bearer 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",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers)
print(response.status_code, response.text) 