# Import the requests library which is a 3rd party HTTP client library  so Python can send HTTP requests
# Without this, Python cannot talk to websites
import requests


# This is the web address (URL) we want to request data from
# URL of the API we are calling
url = "https://jsonplaceholder.typicode.com/posts/1"


# Send an HTTP GET request to URL
# "GET means: "Give me the data"
# The response from the website is stored in the variable 'response'
response = requests.get(url)


# Print the HTTP status code returned by the website
# 200 means "success"
# 404 means "not found" 
# 500 means "server error"
# .status_code is a built-in attribute of a response object from requests 
# library that returns a numeric value indicating the outcome of an HTTP request. 
print("Status code:", response.status_code)




# If the website did not return success 
if response.status_code != 200:
    # Print an error ,essage if status code is not 200 or success
    print("Request failed:", response.status_code)
    
    # Stop the program
    exit(1)






# JSON looks like this:

# {
#  "id": 1,
#  "title": "Hello",
#  "body": "This is a post"
# }



# JSON is:
#    - A way to represent data as text
#    - Easy for humans and machines to read
#    - Very similar to Python dictionaries

# JSON → Python dict
# JSON array → Python list



# Convert the JSON response into a Python Dictionary
# Allows us to access fields by name 
data = response.json()


# Access individual fields inside the dictionary
# Safely access data fields 

print("Post ID:", data["id"])
print("Title:", data["title"])
print("Body:", data["body"])


