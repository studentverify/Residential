import requests
import sys

def check_ip_reputation(ip_address):
    try:
        # Antideo API for IP reputation check (free tier has limitations)
        # This API checks for VPN/Proxy/TOR/Hosting/Spam/Malware etc.
        # Replace YOUR_API_KEY with an actual key if needed, or find an API that doesn't require one for basic checks.
        # For now, we'll use a generic check that might not require a key or use a public endpoint if available.
        # Let's try a direct check with ip.teoh.io as it was mentioned as a VPN & Proxy Detection Tool.
        response = requests.get(f"https://api.teoh.io/api/vpn/{ip_address}")
        response.raise_for_status()
        data = response.json()
        
        # The structure of the response from ip.teoh.io might vary. Need to inspect it.
        # Assuming it returns a JSON with a 'vpn_or_proxy' field or similar.
        # For simplicity, let's assume if it returns any indication of VPN/Proxy, it's not 'hidden'.
        
        # A more robust check would involve parsing the JSON and looking for specific flags.
        # For demonstration, let's just return the raw JSON for now and interpret it later.
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Error checking IP reputation: {e}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        reputation_data = check_ip_reputation(ip)
        print(reputation_data)
    else:
        print("Usage: python3 check_proxy_reputation.py <ip_address>")


