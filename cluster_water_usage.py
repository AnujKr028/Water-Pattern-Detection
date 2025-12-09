import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# -----------------------------------------
# STEP 1 — GENERATE SYNTHETIC WATER USAGE DATA
# -----------------------------------------

def generate_synthetic_data():
    np.random.seed(42)

    households = 200
    days = 30

    data = []

    for h in range(households):
        base = np.random.uniform(150, 450)  # monthly usage
        noise = np.random.normal(0, 20, days)

        daily_usage = base / 30 + noise
        daily_usage = np.clip(daily_usage, 50, 600)  # safe limit

        for d in range(days):
            data.append([h, d + 1, daily_usage[d]])

    df = pd.DataFrame(data, columns=["HouseholdID", "Day", "WaterUsage"])

    df.to_csv("synthetic_water_usage.csv", index=False)
    print("✔ synthetic_water_usage.csv generated successfully!")


# -----------------------------------------
# STEP 2 — CLUSTERING
# -----------------------------------------

def perform_clustering():
    df = pd.read_csv("synthetic_water_usage.csv")

    # Aggregate monthly water usage per household
    grouped = df.groupby("HouseholdID")["WaterUsage"].sum().reset_index()

    # Fit KMeans
    k = 3
    kmeans = KMeans(n_clusters=k, random_state=42)
    grouped["Cluster"] = kmeans.fit_predict(grouped[["WaterUsage"]])

    # Save cluster profiles
    profiles = grouped.groupby("Cluster")["WaterUsage"].mean()
    profiles.to_csv("cluster_profiles.csv")

    print("✔ cluster_profiles.csv saved successfully!")
    print("\nCluster Centers (liters/month):")
    print(profiles)

    # Plot results
    plt.scatter(grouped["HouseholdID"], grouped["WaterUsage"], c=grouped["Cluster"])
    plt.xlabel("Household ID")
    plt.ylabel("Total Monthly Water Usage (liters)")
    plt.title("Smart Water Usage Clustering")
    plt.show()


# -----------------------------------------
# RUN BOTH STEPS
# -----------------------------------------

generate_synthetic_data()
perform_clustering()
