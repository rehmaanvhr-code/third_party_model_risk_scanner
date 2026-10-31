from langchain.chains import RetrievalQA
from langchain_community.llms import Cohere
import torch

llm = Cohere(model="command-r")
yolo = torch.hub.load("ultralytics/yolov5", "yolov5s")
