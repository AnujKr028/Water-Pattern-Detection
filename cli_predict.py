# file: cli_predict.py

from model_logic import predict_cluster

if __name__ == "__main__":
    monthly_usage = float(input("Enter monthly water usage (liters): "))
    result = predict_cluster(monthly_usage)
    print("Detected cluster:", result["cluster"])
    print("Pattern:", result["description"])
