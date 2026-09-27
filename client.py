import requests

response = requests.post(
    "http://127.0.0.1:5000/ads",
    json={"title": "Продам диван", "owner": "Bob"},
)
print(response.status_code)
print(response.json())

# response = requests.get(
#     "http://127.0.0.1:5000/ads/1",
# )
# print(response.status_code)
# print(response.json())


# response = requests.patch(
#     "http://127.0.0.1:5000/ads/1",
#     json={"title": "Продам дом", "owner": "Rob"},
# )
# print(response.status_code)
# print(response.json())


# response = requests.get(
#     "http://127.0.0.1:5000/ads/144444",
# )
# print(response.status_code)
# print(response.json())

# response = requests.delete(
#     "http://127.0.0.1:5000/ads/2",
# )
# print(response.status_code)
# print(response.json())

