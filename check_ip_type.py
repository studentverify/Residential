import requests
import sys
import json

def check_ip_type(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=as,isp,org,query,status")
        response.raise_for_status()
        data = response.json()
        if data and data["status"] == "success":
            asn = data.get("as", "").lower()
            isp = data.get("isp", "").lower()
            org = data.get("org", "").lower()

            # Simple heuristic to determine if it\'s likely residential
            # Look for keywords common in residential ISPs and absence of datacenter/hosting keywords
            is_residential = False
            if any(keyword in isp for keyword in ["telecom", "cable", "broadband", "fiber", "mobile", "wireless"]):
                is_residential = True
            if any(keyword in org for keyword in ["telecom", "cable", "broadband", "fiber", "mobile", "wireless"]):
                is_residential = True

            if any(keyword in asn for keyword in ["hosting", "datacenter", "cloud", "server", "vpn", "proxy"]):
                is_residential = False
            if any(keyword in isp for keyword in ["hosting", "datacenter", "cloud", "server", "vpn", "proxy"]):
                is_residential = False
            if any(keyword in org for keyword in ["hosting", "datacenter", "cloud", "server", "vpn", "proxy"]):
                is_residential = False

            return {"ip": ip_address, "is_residential": is_residential, "asn": asn, "isp": isp, "org": org, "raw_data": data}
        else:
            return {"ip": ip_address, "error": "Failed to get IP info", "raw_data": data}
    except requests.exceptions.RequestException as e:
        return {"ip": ip_address, "error": f"Error checking IP type: {e}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        ip_type_data = check_ip_type(ip)
        print(json.dumps(ip_type_data)) # Output as JSON
    else:
        print("Usage: python3 check_ip_type.py <ip_address>")


