from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model_logic import predict_cluster

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Smart Water Clustering API is Running!"}

@app.post("/predict")
def predict(data: dict):
    usage = data["usage"]
    cluster = predict_cluster(usage)
    return {"cluster": cluster}
