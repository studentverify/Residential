import requests

def get_ip_with_proxy(proxy_url=None):
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    } if proxy_url else None
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["ip"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("Testing direct IP:")
    print(get_ip_with_proxy())

    # Example of testing with a placeholder proxy. This will need to be replaced with actual proxies.
    # print("\nTesting with a proxy (example.com:8080):")
    # print(get_ip_with_proxy("http://example.com:8080"))


