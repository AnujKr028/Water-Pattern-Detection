# file: model_logic.py

import joblib

# load trained model (you should have saved it after training)
kmeans = joblib.load("kmeans_model.pkl")
scaler = joblib.load("scaler.pkl")   # if you used a scaler, else remove

def predict_cluster(monthly_usage: float):
    # build feature vector – right now we are only using monthly_usage
    x = [[monthly_usage]]

    # scale if needed
    # x_scaled = scaler.transform(x)
    # cluster = kmeans.predict(x_scaled)[0]

    cluster = int(kmeans.predict(x)[0])

    # Optional: map cluster → human meaning
    cluster_desc = {
        0: "Low water usage household",
        1: "High water usage household",
        2: "Irregular / abnormal usage pattern"
    }.get(cluster, "Unknown pattern")

    return {
        "cluster": cluster,
        "description": cluster_desc
    }
