import subprocess
import json
import requests
import os

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
RESTART_THRESHOLD = 5  # your pod already has 29, so this will trigger

def get_pods():
    result = subprocess.run(
        ["kubectl", "get", "pods", "-A", "-o", "json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def send_slack_alert(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK, json=payload)
    print("Slack response:", response.text)

def check_restarts():
    data = get_pods()

    for item in data["items"]:
        namespace = item["metadata"]["namespace"]
        pod_name = item["metadata"]["name"]

        for container in item["status"].get("containerStatuses", []):
            restart_count = container.get("restartCount", 0)

            if restart_count >= RESTART_THRESHOLD:
                message = f"""
🚨 Kubernetes Restart Alert
Namespace: {namespace}
Pod: {pod_name}
Restart Count: {restart_count}
"""
                send_slack_alert(message)

if __name__ == "__main__":
    check_restarts()
