import pandas as pd
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. Load data
df = pd.read_csv("synthetic_water_usage.csv")

# 2. Aggregate to get one value per household
monthly = df.groupby("HouseholdID")["WaterUsage"].mean().reset_index()

X = monthly[["WaterUsage"]]

# 3. Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train KMeans with 3 clusters
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

# 5. Save
joblib.dump(kmeans, "kmeans_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model trained on aggregated household usage.")
