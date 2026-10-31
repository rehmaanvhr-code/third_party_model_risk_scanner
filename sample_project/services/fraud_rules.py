import pickle
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

with open("models/fraud_gbm_v3.pkl", "rb") as f:
    fraud_model = pickle.load(f)


def score(tx):
    return fraud_model.predict_proba([tx])[0][1]


def explain(tx):
    body = {"prompt": "explain this transaction"}
    return bedrock.invoke_model(modelId="anthropic.claude-3-haiku-20240307-v1:0", body=str(body))
