import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ----------------------------
# 1. TRAIN THE CLUSTERING MODEL
# ----------------------------
def train_model(csv_path="synthetic_water_usage.csv"):
    """
    Train KMeans on total monthly water usage per household.
    Returns: scaler, kmeans
    """
    # Load your existing dataset
    df = pd.read_csv(csv_path)

    # We assume columns: HouseholdID, Day, WaterUsage
    grouped = (
        df.groupby("HouseholdID")["WaterUsage"]
        .sum()
        .reset_index()
        .rename(columns={"WaterUsage": "total_monthly_usage"})
    )

    # Features for training (here we use only 1 feature for simplicity)
    X = grouped[["total_monthly_usage"]].values

    # Scale the data (important for KMeans)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train KMeans
    kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
    kmeans.fit(X_scaled)

    print("Model trained on existing households.")
    print("Example total usages (first 5):")
    print(grouped.head(), "\n")

    return scaler, kmeans


# ----------------------------
# 2. ASK USER FOR INPUT & PREDICT
# ----------------------------
def predict_for_user(scaler, kmeans):
    """
    Ask the user for 30 daily usage values and detect usage pattern.
    """
    print("\n--- Smart Water Usage Pattern Detector (CLI) ---")
    print("Enter your daily water usage (in liters) for 30 days.")
    print("Example: 120, 130, 110, 95, ...")

    raw = input("\nEnter 30 values (comma separated):\n> ")

    # Parse input into numbers
    try:
        values = [float(x.strip()) for x in raw.split(",") if x.strip() != ""]
    except ValueError:
        print("❌ Could not parse your input. Please enter only numbers separated by commas.")
        return

    if len(values) != 30:
        print(f"❌ You entered {len(values)} values, but we need exactly 30 days.")
        return

    total_monthly = sum(values)
    print(f"\n✅ Total monthly usage from your input = {total_monthly:.1f} liters")

    # Prepare for model
    X_new = np.array([[total_monthly]])
    X_new_scaled = scaler.transform(X_new)

    # Predict cluster
    cluster_id = int(kmeans.predict(X_new_scaled)[0])

    # Make cluster labels human-readable (low / medium / high)
    centers = kmeans.cluster_centers_.ravel()
    order = np.argsort(centers)  # from lowest to highest center

    labels = {}
    labels[order[0]] = "Low usage pattern"
    labels[order[1]] = "Medium usage pattern"
    labels[order[2]] = "High usage pattern"

    print(f"\n🔍 Detected pattern:")
    print(f"   → Cluster {cluster_id} → {labels[cluster_id]}")


# ----------------------------
# 3. MAIN ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    scaler, kmeans = train_model()
    predict_for_user(scaler, kmeans)
