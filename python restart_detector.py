import subprocess
import json
import requests
import os

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
RESTART_THRESHOLD = 5

def get_pods():
    result = subprocess.run(
        ["kubectl", "get", "pods", "-A", "-o", "json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def send_slack_alert(namespace, pod_name, restart_count):
    payload = {
        "text": f" *Kubernetes Restart Alert*\n"
                f"*Namespace:* {namespace}\n"
                f"*Pod:* {pod_name}\n"
                f"*Restart Count:* {restart_count}"
    }

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
                send_slack_alert(namespace, pod_name, restart_count)

if __name__ == "__main__":
    check_restarts()
