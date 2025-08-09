import requests

def get_free_proxies():
    try:
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
        response.raise_for_status()
        proxies = response.text.splitlines()
        return [p for p in proxies if p.strip()]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching proxies: {e}")
        return []

if __name__ == "__main__":
    proxies = get_free_proxies()
    if proxies:
        print(f"Fetched {len(proxies)} proxies. First 5: {proxies[:5]}")
        with open("free_proxies.txt", "w") as f:
            for proxy in proxies:
                f.write(proxy + "\n")
        print("Proxies saved to free_proxies.txt")
    else:
        print("No proxies fetched.")


