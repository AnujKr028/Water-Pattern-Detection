import pandas as pd
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load your dataset
df = pd.read_csv("synthetic_water_usage.csv")

# Use the actual correct column from your CSV
X = df[["WaterUsage"]]

# Scale the feature
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train KMeans
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

# Save model files
joblib.dump(kmeans, "kmeans_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model trained successfully!")
print("Files created: kmeans_model.pkl, scaler.pkl")
