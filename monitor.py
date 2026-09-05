"""
Overvågningssystem
Tjekker om nogle udvalgte hosts er tilgængelige (ping eller HTTP)
og sender en e-mail, hvis en af dem går ned eller kommer op igen.
"""

import json
import platform
import smtplib
import subprocess
import time
from email.mime.text import MIMEText
from pathlib import Path

import requests
import yaml

STATUS_FILE = Path("status.json")


def load_config():
    """Indlæser hosts, tjekinterval og e-mail-indstillinger fra config.yaml."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ping(address):
    """Sender ét ping til en adresse. Virker på både Windows og Linux."""
    flag = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(
        ["ping", flag, "1", address],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def check_http(url):
    """Tjekker om en webadresse svarer med en gyldig statuskode."""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code < 400
    except requests.RequestException:
        return False


def check_host(host, retries=3):
    """Prøver et par gange, så en enkelt netværksudsving ikke udløser falsk alarm."""
    for _ in range(retries):
        if host["type"] == "ping":
            if ping(host["address"]):
                return True
        else:
            if check_http(host["address"]):
                return True
        time.sleep(3)
    return False


def load_status():
    """Henter sidst kendte status, så vi kan opdage ændringer siden sidst."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {}


def save_status(status):
    """Gemmer den nyeste status, klar til næste gennemløb."""
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def send_email_alert(smtp_config, name, is_up):
    """Sender en e-mail via Gmail, hvis alarmer er slået til i config.yaml."""
    if not smtp_config or not smtp_config.get("enabled"):
        return
    subject = "OPPE: " + name if is_up else "NEDE: " + name
    body = name + " skiftede status til " + ("oppe" if is_up else "nede") + "."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_config["from_address"]
    msg["To"] = smtp_config["to_address"]

    with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
        server.starttls()
        server.login(smtp_config["username"], smtp_config["password"])
        server.send_message(msg)


def main():
    config = load_config()
    status = load_status()

    print("Sa er vi i gang! Holder oje med tingene nu")

    while True:
        for host in config["hosts"]:
            name = host["name"]
            up_now = check_host(host)
            up_before = status.get(name)

            if up_before is not None and up_now != up_before:
                before_text = "oppe" if up_before else "nede"
                now_text = "oppe" if up_now else "nede"
                print("Hov! " + name + " skiftede status: var " + before_text + ", er nu " + now_text)
                send_email_alert(config.get("smtp"), name, up_now)
            else:
                status_text = "oppe og korer" if up_now else "desvarre nede"
                print(name + " er stadig " + status_text)

            status[name] = up_now

        save_status(status)
        time.sleep(config.get("check_interval_seconds", 60))


if __name__ == "__main__":
    main()
    