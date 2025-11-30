from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="ZFtUgbaxUbTvna51Ypc0"
)

baseURL = 'DataImages/'
# result = CLIENT.infer(baseURL+'cat.jpeg', model_id="sandwich-tqrld/1")
# result = CLIENT.infer(baseURL+'hamSandwich.jpg', model_id="sandwich-tqrld/1")
# result = CLIENT.infer(baseURL+'hotdog.jpeg', model_id="sandwich-tqrld/1")
result = CLIENT.infer(baseURL+'dog.jpeg', model_id="sandwich-tqrld/1")

# Check if any predictions were made
if result['predictions'] and len(result['predictions']) > 0:
    print("THIS IS A SANDWICH")
else:
    print("THIS ISN'T A SANDWICH")