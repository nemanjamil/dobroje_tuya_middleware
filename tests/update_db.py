import http.client
import json

conn = http.client.HTTPConnection("dobroje.rs")

payload = json.dumps({
    "device": "XXXXTEST",
    "data": {"result": 1}
})

headers = {
    'Content-Type': 'application/json'
}

conn.request("POST", "/parametri.php?action=tuyapayload", payload, headers)
response = conn.getresponse()

# Check the response status code
print("Status Code:", response.status)

# Print the raw response content
response_content = response.read().decode()
print("Response Content:", response_content)

# Check if the response content type is JSON
if response.getheader('Content-Type') == 'application/json':
    try:
        response_json = json.loads(response_content)
        print(response_json)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
else:
    print("Response is not in JSON format")

conn.close()
