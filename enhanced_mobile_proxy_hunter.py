#!/usr/bin/env python3
"""
RedTeamAbel's Enhanced Mobile Proxy Hunter
Ultimate Android Red Team Toolkit with Auto-Rotation & Thorough Testing
Optimized for Samsung Galaxy A06 and mobile ISPs
"""

import os
import sys
import time
import json
import random
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

app = Flask(__name__)
app.secret_key = 'redteamabel_mobile_hunter_2025'

class EnhancedMobileProxyHunter:
    def __init__(self):
        self.proxies = []
        self.verified_residential_proxies = []
        self.mobile_isp_proxies = []
        self.current_proxy_index = 0
        self.rotation_interval = 300  # 5 minutes
        self.last_rotation = time.time()
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for proxy management"""
        self.conn = sqlite3.connect('proxy_hunter.db', check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE,
                ip TEXT,
                country TEXT,
                is_residential BOOLEAN,
                is_mobile_isp BOOLEAN,
                isp TEXT,
                org TEXT,
                response_time INTEGER,
                success_rate REAL,
                last_tested TIMESTAMP,
                times_tested INTEGER DEFAULT 0,
                times_successful INTEGER DEFAULT 0,
                status TEXT DEFAULT 'untested'
            )
        ''')
        self.conn.commit()
    
    def get_current_ip(self):
        """Get current IP address with multiple fallbacks"""
        services = [
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip",
            "https://api.myip.com",
            "https://ipapi.co/json/"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if service == "https://api.ipify.org?format=json":
                    return response.json()["ip"]
                elif service == "https://httpbin.org/ip":
                    return response.json()["origin"]
                elif service == "https://api.myip.com":
                    return response.json()["ip"]
                elif service == "https://ipapi.co/json/":
                    return response.json()["ip"]
            except:
                continue
        return "Unknown"
    
    def get_comprehensive_ip_info(self, ip_address):
        """Get comprehensive IP information from multiple sources"""
        info = {}
        
        # Primary source: ip-api.com
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,region,city,isp,org,as,mobile,proxy,hosting,query,status", timeout=10)
            data = response.json()
            if data["status"] == "success":
                info.update({
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("countryCode", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "asn": data.get("as", "Unknown"),
                    "is_mobile": data.get("mobile", False),
                    "is_proxy": data.get("proxy", False),
                    "is_hosting": data.get("hosting", False)
                })
        except:
            pass
        
        # Secondary source: ipapi.co
        try:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=10)
            data = response.json()
            if not info.get("country"):
                info.update({
                    "country": data.get("country_name", "Unknown"),
                    "country_code": data.get("country_code", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("org", "Unknown")
                })
        except:
            pass
        
        return info if info else None
    
    def is_mobile_isp(self, ip_info):
        """Enhanced detection for mobile ISPs in the USA"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("asn", "").lower()
        
        # Major US mobile carriers
        mobile_carriers = [
            "verizon", "t-mobile", "at&t", "att", "sprint", "boost mobile",
            "cricket", "metro pcs", "tracfone", "straight talk", "mint mobile",
            "visible", "xfinity mobile", "spectrum mobile", "us cellular",
            "consumer cellular", "republic wireless", "google fi", "ting",
            "red pocket", "simple mobile", "total wireless", "net10",
            "page plus", "pure talk", "h2o wireless", "lycamobile"
        ]
        
        # Mobile ISP indicators
        mobile_keywords = [
            "wireless", "mobile", "cellular", "lte", "5g", "4g", "gsm", "cdma",
            "telecommunications", "telecom", "communications", "phone"
        ]
        
        # Check for mobile carriers
        for carrier in mobile_carriers:
            if carrier in isp or carrier in org:
                return True
        
        # Check for mobile keywords
        for keyword in mobile_keywords:
            if keyword in isp or keyword in org:
                return True
        
        # Check API mobile flag
        if ip_info.get("is_mobile"):
            return True
            
        return False
    
    def is_residential_ip(self, ip_info):
        """Enhanced residential IP detection with mobile priority"""
        if not ip_info:
            return False
            
        # If it's mobile, it's likely residential
        if self.is_mobile_isp(ip_info):
            return True
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("asn", "").lower()
        
        # Residential ISP indicators
        residential_keywords = [
            "cable", "broadband", "fiber", "internet", "communications",
            "telecom", "residential", "home", "dsl", "fios"
        ]
        
        # Major US residential ISPs
        residential_isps = [
            "comcast", "charter", "cox", "altice", "frontier", "centurylink",
            "windstream", "mediacom", "sparklight", "optimum", "xfinity",
            "spectrum", "time warner", "bright house", "suddenlink",
            "cablevision", "rcn", "wow", "atlantic broadband"
        ]
        
        # Datacenter/hosting exclusions
        datacenter_keywords = [
            "hosting", "datacenter", "data center", "cloud", "server", "vpn", 
            "proxy", "amazon", "google", "microsoft", "digital ocean", "linode",
            "vultr", "ovh", "hetzner", "dedicated", "colocation", "colo"
        ]
        
        # Check for datacenter keywords (disqualifies)
        for keyword in datacenter_keywords:
            if keyword in isp or keyword in org or keyword in asn:
                return False
        
        # Check for residential ISPs
        for residential_isp in residential_isps:
            if residential_isp in isp or residential_isp in org:
                return True
        
        # Check for residential keywords
        for keyword in residential_keywords:
            if keyword in isp or keyword in org:
                return True
        
        # Check API flags
        if ip_info.get("is_hosting") or ip_info.get("is_proxy"):
            return False
            
        return False
    
    def comprehensive_proxy_test(self, proxy, test_count=3):
        """Comprehensive proxy testing with multiple attempts"""
        results = []
        
        for attempt in range(test_count):
            try:
                ip, port = proxy.split(":")
                proxies = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
                
                # Test multiple endpoints
                test_urls = [
                    "https://api.ipify.org?format=json",
                    "https://httpbin.org/ip",
                    "https://ipapi.co/json/"
                ]
                
                for url in test_urls:
                    try:
                        start_time = time.time()
                        response = requests.get(url, proxies=proxies, timeout=15)
                        response_time = int((time.time() - start_time) * 1000)
                        
                        if response.status_code == 200:
                            if url == "https://api.ipify.org?format=json":
                                proxy_ip = response.json()["ip"]
                            elif url == "https://httpbin.org/ip":
                                proxy_ip = response.json()["origin"]
                            elif url == "https://ipapi.co/json/":
                                proxy_ip = response.json()["ip"]
                            
                            ip_info = self.get_comprehensive_ip_info(proxy_ip)
                            
                            if ip_info and ip_info.get("country_code") == "US":
                                is_residential = self.is_residential_ip(ip_info)
                                is_mobile = self.is_mobile_isp(ip_info)
                                
                                results.append({
                                    "success": True,
                                    "proxy": proxy,
                                    "ip": proxy_ip,
                                    "response_time": response_time,
                                    "is_residential": is_residential,
                                    "is_mobile": is_mobile,
                                    "info": ip_info,
                                    "test_url": url
                                })
                                break
                    except:
                        continue
                        
                if results and results[-1]["success"]:
                    break
                    
            except:
                continue
        
        # Calculate success rate
        success_count = len([r for r in results if r["success"]])
        success_rate = success_count / test_count if test_count > 0 else 0
        
        if results:
            best_result = min(results, key=lambda x: x["response_time"])
            best_result["success_rate"] = success_rate
            best_result["total_tests"] = test_count
            return best_result
        
        return {"success": False, "proxy": proxy, "success_rate": 0}
    
    def save_proxy_to_db(self, proxy_result):
        """Save proxy test results to database"""
        if not proxy_result["success"]:
            return
            
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO proxies 
                (proxy, ip, country, is_residential, is_mobile_isp, isp, org, 
                 response_time, success_rate, last_tested, times_tested, times_successful, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proxy_result["proxy"],
                proxy_result["ip"],
                proxy_result["info"]["country"],
                proxy_result["is_residential"],
                proxy_result["is_mobile"],
                proxy_result["info"]["isp"],
                proxy_result["info"]["org"],
                proxy_result["response_time"],
                proxy_result["success_rate"],
                datetime.now(),
                proxy_result["total_tests"],
                int(proxy_result["total_tests"] * proxy_result["success_rate"]),
                "verified" if proxy_result["success_rate"] > 0.6 else "unstable"
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
    
    def get_verified_proxies(self, mobile_priority=True):
        """Get verified proxies from database with mobile priority"""
        query = '''
            SELECT proxy, ip, is_residential, is_mobile_isp, isp, response_time, success_rate
            FROM proxies 
            WHERE country = 'United States' AND success_rate > 0.5 AND status = 'verified'
            ORDER BY {} DESC, success_rate DESC, response_time ASC
        '''.format("is_mobile_isp" if mobile_priority else "is_residential")
        
        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def auto_rotate_proxy(self):
        """Automatically rotate to next best proxy"""
        if time.time() - self.last_rotation < self.rotation_interval:
            return None
            
        verified_proxies = self.get_verified_proxies()
        if not verified_proxies:
            return None
            
        # Rotate to next proxy
        self.current_proxy_index = (self.current_proxy_index + 1) % len(verified_proxies)
        self.last_rotation = time.time()
        
        current_proxy = verified_proxies[self.current_proxy_index]
        return {
            "proxy": current_proxy[0],
            "ip": current_proxy[1],
            "is_residential": current_proxy[2],
            "is_mobile": current_proxy[3],
            "isp": current_proxy[4],
            "response_time": current_proxy[5],
            "success_rate": current_proxy[6]
        }
    
    def hunt_proxies_enhanced(self):
        """Enhanced proxy hunting from multiple sources"""
        print("🔍 Enhanced proxy hunting initiated...")
        
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
        ]
        
        all_proxies = set()
        
        for source in sources:
            try:
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    proxies = [p.strip() for p in response.text.splitlines() 
                             if p.strip() and ':' in p.strip()]
                    all_proxies.update(proxies)
                    print(f"✅ Fetched {len(proxies)} proxies from {source}")
            except Exception as e:
                print(f"❌ Failed to fetch from {source}: {e}")
        
        self.proxies = list(all_proxies)
        print(f"🎯 Total unique proxies collected: {len(self.proxies)}")
        
        return len(self.proxies)
    
    def test_all_proxies_enhanced(self, max_workers=10, max_proxies=200):
        """Enhanced proxy testing with database storage"""
        print("⚡ Enhanced proxy testing initiated...")
        
        # Limit proxies for mobile device performance
        test_proxies = random.sample(self.proxies, min(len(self.proxies), max_proxies))
        
        verified_count = 0
        mobile_count = 0
        residential_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.comprehensive_proxy_test, proxy): proxy 
                for proxy in test_proxies
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result["success"]:
                    self.save_proxy_to_db(result)
                    verified_count += 1
                    
                    if result["is_mobile"]:
                        mobile_count += 1
                    if result["is_residential"]:
                        residential_count += 1
                    
                    print(f"✅ Verified: {result['proxy']} - {result['info']['isp']} - Mobile: {result['is_mobile']}")
        
        print(f"🎯 Testing complete: {verified_count} verified, {mobile_count} mobile, {residential_count} residential")
        
        return {
            "tested": len(test_proxies),
            "verified": verified_count,
            "mobile": mobile_count,
            "residential": residential_count
        }

# Initialize enhanced hunter
hunter = EnhancedMobileProxyHunter()

@app.route('/')
def index():
    return render_template('enhanced_mobile.html')

@app.route('/api/current-ip')
def current_ip():
    return jsonify({"ip": hunter.get_current_ip()})

@app.route('/api/hunt-proxies', methods=['POST'])
def hunt_proxies():
    total = hunter.hunt_proxies_enhanced()
    return jsonify({"total": total})

@app.route('/api/test-all', methods=['POST'])
def test_all():
    if not hunter.proxies:
        hunter.hunt_proxies_enhanced()
    
    results = hunter.test_all_proxies_enhanced()
    return jsonify(results)

@app.route('/api/verified-proxies')
def get_verified_proxies():
    proxies = hunter.get_verified_proxies()
    return jsonify({
        "proxies": [{"proxy": p[0], "ip": p[1], "is_mobile": p[3], "isp": p[4]} for p in proxies],
        "count": len(proxies)
    })

@app.route('/api/auto-rotate', methods=['POST'])
def auto_rotate():
    rotated_proxy = hunter.auto_rotate_proxy()
    if rotated_proxy:
        return jsonify(rotated_proxy)
    else:
        return jsonify({"error": "No proxies available for rotation"}), 400

@app.route('/api/stealth-test', methods=['POST'])
def stealth_test():
    data = request.get_json()
    proxy = data.get('proxy')
    
    if not proxy:
        return jsonify({"error": "No proxy provided"}), 400
    
    result = hunter.comprehensive_proxy_test(proxy)
    
    if result["success"]:
        return jsonify({
            "ip": result["ip"],
            "country": result["info"]["country"],
            "is_residential": result["is_residential"],
            "is_mobile": result["is_mobile"],
            "isp": result["info"]["isp"],
            "response_time": result["response_time"],
            "success_rate": result["success_rate"]
        })
    else:
        return jsonify({"error": "Proxy test failed"}), 400

if __name__ == '__main__':
    print("🔥 RedTeamAbel's Enhanced Mobile Proxy Hunter Starting...")
    print("🚀 Optimized for Samsung Galaxy A06")
    print("📱 Mobile ISP Priority Mode Enabled")
    print("🔄 Auto-Rotation Every 5 Minutes")
    print("🌐 Access at: http://localhost:8080")
    
    os.makedirs("templates", exist_ok=True)
    
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

