import random

with open("proxies.txt", "r") as f:
    raw_proxies = [line.strip() for line in f if line.strip()]

def get_random_proxy():
    proxy_line = random.choice(raw_proxies)
    ip, port, user, pwd = proxy_line.split(":")
    proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
    return {
        "http://": proxy_url,
        "https://": proxy_url
    }
