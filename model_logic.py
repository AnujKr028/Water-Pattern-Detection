# file: model_logic.py

def predict_cluster(usage: float):
    """
    Rule-based clustering:
    - Cluster 0: Low / efficient usage
    - Cluster 1: Normal / balanced usage
    - Cluster 2: High / irregular / abnormal usage
    """

    usage = float(usage)

    if usage < 60:
        cluster = 0
        desc = "Low / efficient usage pattern."
    elif usage < 120:
        cluster = 1
        desc = "Normal / balanced usage pattern."
    else:
        cluster = 2
        desc = "High / irregular / abnormal usage pattern."

    return {
        "cluster": cluster,
        "description": desc
    }
