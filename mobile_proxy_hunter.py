#!/usr/bin/env python3
"""
RedTeamAbel's Mobile Proxy Hunter
Ultimate Android Red Team Toolkit for Residential Proxy Discovery
"""

import os
import sys
import time
import json
import requests
import subprocess
from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

class MobileProxyHunter:
    def __init__(self):
        self.proxies = []
        self.usa_proxies = []
        self.residential_proxies = []
        self.working_proxies = []
        
    def get_current_ip(self):
        """Get current IP address"""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            return response.json()["ip"]
        except:
            return "Unknown"
    
    def get_ip_info(self, ip_address):
        """Get detailed IP information"""
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,isp,org,as,query,status", timeout=5)
            data = response.json()
            if data["status"] == "success":
                return {
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("countryCode", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "asn": data.get("as", "Unknown")
                }
        except:
            pass
        return None
    
    def is_residential_ip(self, ip_info):
        """Determine if IP is residential based on ISP/ORG info"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("asn", "").lower()
        
        # Residential indicators
        residential_keywords = ["telecom", "cable", "broadband", "fiber", "mobile", "wireless", "internet", "communications"]
        datacenter_keywords = ["hosting", "datacenter", "cloud", "server", "vpn", "proxy", "amazon", "google", "microsoft", "digital ocean"]
        
        # Check for datacenter keywords (disqualifies)
        for keyword in datacenter_keywords:
            if keyword in isp or keyword in org or keyword in asn:
                return False
        
        # Check for residential keywords
        for keyword in residential_keywords:
            if keyword in isp or keyword in org:
                return True
                
        return False
    
    def test_proxy(self, proxy):
        """Test a single proxy"""
        try:
            ip, port = proxy.split(":")
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            start_time = time.time()
            response = requests.get("https://api.ipify.org?format=json", 
                                  proxies=proxies, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                proxy_ip = response.json()["ip"]
                ip_info = self.get_ip_info(proxy_ip)
                
                if ip_info and ip_info["country_code"] == "US":
                    is_residential = self.is_residential_ip(ip_info)
                    return {
                        "proxy": proxy,
                        "ip": proxy_ip,
                        "working": True,
                        "usa": True,
                        "residential": is_residential,
                        "response_time": response_time,
                        "info": ip_info
                    }
        except:
            pass
        
        return {"proxy": proxy, "working": False}
    
    def hunt_proxies(self):
        """Hunt for fresh proxies from multiple sources"""
        print("🔍 Hunting for fresh proxies...")
        
        # Fetch from multiple sources
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
        ]
        
        all_proxies = set()
        
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = [p.strip() for p in response.text.splitlines() if p.strip()]
                    all_proxies.update(proxies)
                    print(f"✅ Fetched {len(proxies)} proxies from {source}")
            except Exception as e:
                print(f"❌ Failed to fetch from {source}: {e}")
        
        self.proxies = list(all_proxies)
        print(f"🎯 Total unique proxies collected: {len(self.proxies)}")
        
        # Save to file
        with open("raw_proxies.txt", "w") as f:
            for proxy in self.proxies:
                f.write(proxy + "\n")
        
        return len(self.proxies)
    
    def test_all_proxies(self, max_workers=20):
        """Test all proxies with threading"""
        print("⚡ Testing all proxies...")
        
        working_proxies = []
        usa_proxies = []
        residential_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(self.test_proxy, proxy): proxy 
                             for proxy in self.proxies[:100]}  # Limit for mobile
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result["working"]:
                    working_proxies.append(result)
                    if result.get("usa"):
                        usa_proxies.append(result)
                        if result.get("residential"):
                            residential_proxies.append(result)
        
        self.working_proxies = working_proxies
        self.usa_proxies = usa_proxies
        self.residential_proxies = residential_proxies
        
        # Save results
        with open("working_proxies.json", "w") as f:
            json.dump(working_proxies, f, indent=2)
        
        with open("usa_residential_proxies.txt", "w") as f:
            for proxy in residential_proxies:
                f.write(proxy["proxy"] + "\n")
        
        print(f"✅ Testing complete: {len(working_proxies)} working, {len(usa_proxies)} USA, {len(residential_proxies)} residential")
        
        return {
            "tested": len(self.proxies),
            "working": len(working_proxies),
            "usa": len(usa_proxies),
            "residential": len(residential_proxies)
        }

# Initialize hunter
hunter = MobileProxyHunter()

@app.route('/')
def index():
    return render_template('mobile.html')

@app.route('/api/current-ip')
def current_ip():
    return jsonify({"ip": hunter.get_current_ip()})

@app.route('/api/hunt-proxies', methods=['POST'])
def hunt_proxies():
    total = hunter.hunt_proxies()
    return jsonify({
        "total": total,
        "usa": len(hunter.usa_proxies),
        "residential": len(hunter.residential_proxies)
    })

@app.route('/api/proxies')
def get_proxies():
    # Load from file if exists
    try:
        with open("usa_residential_proxies.txt", "r") as f:
            residential_proxies = [line.strip() for line in f if line.strip()]
    except:
        residential_proxies = []
    
    return jsonify({
        "proxies": residential_proxies,
        "usa_count": len(hunter.usa_proxies),
        "residential_count": len(residential_proxies)
    })

@app.route('/api/stealth-test', methods=['POST'])
def stealth_test():
    data = request.get_json()
    proxy = data.get('proxy')
    
    if not proxy:
        return jsonify({"error": "No proxy provided"}), 400
    
    result = hunter.test_proxy(proxy)
    
    if result["working"]:
        return jsonify({
            "ip": result["ip"],
            "country": result["info"]["country"],
            "country_code": result["info"]["country_code"],
            "is_residential": result["residential"],
            "isp": result["info"]["isp"],
            "response_time": result["response_time"]
        })
    else:
        return jsonify({"error": "Proxy test failed"}), 400

@app.route('/api/test-all', methods=['POST'])
def test_all():
    # Load proxies if not already loaded
    if not hunter.proxies:
        try:
            with open("raw_proxies.txt", "r") as f:
                hunter.proxies = [line.strip() for line in f if line.strip()]
        except:
            return jsonify({"error": "No proxies to test"}), 400
    
    results = hunter.test_all_proxies()
    return jsonify(results)

if __name__ == '__main__':
    print("🔥 RedTeamAbel's Mobile Proxy Hunter Starting...")
    print("🚀 Access at: http://localhost:8080")
    
    # Create templates directory
    os.makedirs("templates", exist_ok=True)
    
    # Hunt for initial proxies
    hunter.hunt_proxies()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)

