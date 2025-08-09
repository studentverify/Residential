import requests
import sys

def get_ip_country(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status()
        data = response.json()
        if data and data["status"] == "success":
            return data["countryCode"]
        else:
            return "Unknown"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        country_code = get_ip_country(ip)
        print(country_code)
    else:
        print("Usage: python3 check_proxy_country.py <ip_address>")


