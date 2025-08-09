#!/usr/bin/env python3
"""
RedTeamAbel's Enhanced Mobile Proxy Hunter - Telecom Priority Edition
Prioritizes AT&T, Verizon, T-Mobile, and other US telecom providers
Optimized for Termux deployment from Kenya
"""

import os
import sys
import time
import json
import random
import requests
import threading
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
app.secret_key = 'redteamabel_telecom_hunter_2025'

class TelecomPriorityProxyHunter:
    def __init__(self):
        self.proxies = []
        self.verified_telecom_proxies = []
        self.db_path = 'telecom_proxy_hunter.db'
        self.init_database()
        
        # US Telecom Providers Priority List
        self.priority_telecoms = {
            # Major Wireless Carriers (Highest Priority)
            "verizon": {"priority": 10, "type": "wireless", "keywords": ["verizon", "vzw", "cellco"]},
            "at&t": {"priority": 10, "type": "wireless", "keywords": ["at&t", "att", "cingular", "sbc"]},
            "t-mobile": {"priority": 10, "type": "wireless", "keywords": ["t-mobile", "tmobile", "metro pcs", "metropcs"]},
            "sprint": {"priority": 9, "type": "wireless", "keywords": ["sprint", "boost mobile", "virgin mobile"]},
            
            # Regional Wireless Carriers
            "us cellular": {"priority": 8, "type": "wireless", "keywords": ["us cellular", "uscellular"]},
            "cricket": {"priority": 8, "type": "wireless", "keywords": ["cricket", "aio wireless"]},
            "tracfone": {"priority": 7, "type": "wireless", "keywords": ["tracfone", "straight talk", "net10", "total wireless"]},
            "mint mobile": {"priority": 7, "type": "wireless", "keywords": ["mint mobile", "ultra mobile"]},
            "visible": {"priority": 7, "type": "wireless", "keywords": ["visible", "verizon wireless"]},
            
            # Cable/Telecom ISPs (Secondary Priority)
            "comcast": {"priority": 6, "type": "cable", "keywords": ["comcast", "xfinity", "cable"]},
            "charter": {"priority": 6, "type": "cable", "keywords": ["charter", "spectrum", "time warner"]},
            "cox": {"priority": 5, "type": "cable", "keywords": ["cox", "cox communications"]},
            "altice": {"priority": 5, "type": "cable", "keywords": ["altice", "optimum", "cablevision"]},
            "frontier": {"priority": 5, "type": "telecom", "keywords": ["frontier", "frontier communications"]},
            "centurylink": {"priority": 5, "type": "telecom", "keywords": ["centurylink", "lumen", "qwest"]},
        }
        
    def init_database(self):
        """Initialize SQLite database for telecom proxy management"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS telecom_proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE,
                ip TEXT,
                country TEXT,
                is_telecom BOOLEAN,
                is_wireless BOOLEAN,
                telecom_provider TEXT,
                telecom_priority INTEGER,
                isp TEXT,
                org TEXT,
                response_time INTEGER,
                success_rate REAL,
                last_tested TIMESTAMP,
                times_tested INTEGER DEFAULT 0,
                times_successful INTEGER DEFAULT 0,
                status TEXT DEFAULT 'untested',
                first_discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_successful TIMESTAMP
            )
        ''')
        
        # Performance indexes
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_telecom_priority 
            ON telecom_proxies(is_telecom, telecom_priority DESC, success_rate DESC)
        ''')
        
        self.conn.commit()
    
    def identify_telecom_provider(self, ip_info):
        """Identify and prioritize telecom providers"""
        if not ip_info:
            return None, 0, False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("as", "").lower()
        
        # Check against priority telecom list
        for provider, details in self.priority_telecoms.items():
            for keyword in details["keywords"]:
                if keyword in isp or keyword in org or keyword in asn:
                    is_wireless = details["type"] == "wireless"
                    return provider, details["priority"], is_wireless
        
        # Check for other wireless indicators
        wireless_keywords = [
            "wireless", "mobile", "cellular", "lte", "5g", "4g", "gsm", "cdma",
            "telecommunications", "telecom", "communications", "phone"
        ]
        
        for keyword in wireless_keywords:
            if keyword in isp or keyword in org:
                return "unknown_wireless", 3, True
        
        # Check for cable/telecom indicators
        telecom_keywords = [
            "cable", "broadband", "fiber", "internet", "communications",
            "telecom", "residential", "home", "dsl", "fios"
        ]
        
        for keyword in telecom_keywords:
            if keyword in isp or keyword in org:
                return "unknown_telecom", 2, False
        
        return None, 0, False
    
    def is_datacenter_ip(self, ip_info):
        """Check if IP is from datacenter (to exclude)"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        
        datacenter_keywords = [
            "hosting", "datacenter", "data center", "cloud", "server", "vpn", 
            "proxy", "amazon", "google", "microsoft", "digital ocean", "linode",
            "vultr", "ovh", "hetzner", "dedicated", "colocation", "colo"
        ]
        
        for keyword in datacenter_keywords:
            if keyword in isp or keyword in org:
                return True
        
        return ip_info.get("hosting", False)
    
    def get_comprehensive_ip_info(self, ip_address):
        """Get comprehensive IP information"""
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,region,city,isp,org,as,mobile,proxy,hosting,query,status",
                timeout=10
            )
            data = response.json()
            if data["status"] == "success":
                return data
        except:
            pass
        return None
    
    def comprehensive_telecom_test(self, proxy, test_count=3):
        """Comprehensive proxy testing with telecom prioritization"""
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
                            
                            if ip_info and ip_info.get("countryCode") == "US":
                                # Check if it's datacenter (exclude)
                                if self.is_datacenter_ip(ip_info):
                                    continue
                                
                                # Identify telecom provider
                                provider, priority, is_wireless = self.identify_telecom_provider(ip_info)
                                
                                if provider:  # Only accept telecom/wireless providers
                                    results.append({
                                        "success": True,
                                        "proxy": proxy,
                                        "ip": proxy_ip,
                                        "response_time": response_time,
                                        "telecom_provider": provider,
                                        "telecom_priority": priority,
                                        "is_wireless": is_wireless,
                                        "is_telecom": True,
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
    
    def save_telecom_proxy_to_db(self, proxy_result):
        """Save telecom proxy test results to database"""
        if not proxy_result["success"]:
            return
            
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO telecom_proxies 
                (proxy, ip, country, is_telecom, is_wireless, telecom_provider, telecom_priority,
                 isp, org, response_time, success_rate, last_tested, times_tested, times_successful, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proxy_result["proxy"],
                proxy_result["ip"],
                proxy_result["info"]["country"],
                proxy_result["is_telecom"],
                proxy_result["is_wireless"],
                proxy_result["telecom_provider"],
                proxy_result["telecom_priority"],
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
    
    def get_verified_telecom_proxies(self, wireless_priority=True):
        """Get verified telecom proxies with wireless priority"""
        query = '''
            SELECT proxy, ip, telecom_provider, is_wireless, isp, response_time, success_rate, telecom_priority
            FROM telecom_proxies 
            WHERE country = 'United States' AND success_rate > 0.5 AND status = 'verified' AND is_telecom = 1
            ORDER BY {} DESC, telecom_priority DESC, success_rate DESC, response_time ASC
        '''.format("is_wireless" if wireless_priority else "telecom_priority")
        
        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def hunt_telecom_proxies_enhanced(self):
        """Enhanced proxy hunting focused on telecom sources"""
        print("🔍 Enhanced telecom proxy hunting initiated...")
        
        # Enhanced sources with more proxy lists
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt"
        ]
        
        all_proxies = set()
        
        for source in sources:
            try:
                response = requests.get(source, timeout=20, headers={
                    'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0'
                })
                if response.status_code == 200:
                    proxies = [p.strip() for p in response.text.splitlines() 
                             if p.strip() and ':' in p.strip() and len(p.strip().split(':')) == 2]
                    
                    # Validate proxy format
                    valid_proxies = []
                    for proxy in proxies:
                        try:
                            ip, port = proxy.split(':')
                            if self.is_valid_ip(ip) and self.is_valid_port(port):
                                valid_proxies.append(proxy)
                        except:
                            continue
                    
                    all_proxies.update(valid_proxies)
                    print(f"✅ Fetched {len(valid_proxies)} valid proxies from source")
                    
                    # Small delay to be respectful
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Failed to fetch from {source}: {e}")
                continue
        
        self.proxies = list(all_proxies)
        print(f"🎯 Total unique proxies collected: {len(self.proxies)}")
        
        return len(self.proxies)
    
    def is_valid_ip(self, ip):
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    def is_valid_port(self, port):
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except:
            return False
    
    def test_all_telecom_proxies(self, max_workers=12, max_proxies=150):
        """Enhanced telecom proxy testing"""
        print("⚡ Enhanced telecom proxy testing initiated...")
        
        # Limit proxies for mobile device performance
        test_proxies = random.sample(self.proxies, min(len(self.proxies), max_proxies))
        
        verified_count = 0
        wireless_count = 0
        telecom_count = 0
        priority_providers = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.comprehensive_telecom_test, proxy): proxy 
                for proxy in test_proxies
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result["success"]:
                    self.save_telecom_proxy_to_db(result)
                    verified_count += 1
                    
                    if result["is_wireless"]:
                        wireless_count += 1
                    if result["is_telecom"]:
                        telecom_count += 1
                    
                    provider = result["telecom_provider"]
                    if provider not in priority_providers:
                        priority_providers[provider] = 0
                    priority_providers[provider] += 1
                    
                    wireless_flag = "📱" if result["is_wireless"] else "🏠"
                    priority_flag = "🔥" if result["telecom_priority"] >= 8 else "⭐"
                    print(f"✅ {priority_flag} {wireless_flag} {result['proxy']} - {result['telecom_provider']} - {result['info']['isp']}")
        
        print(f"🎯 Testing complete: {verified_count} verified, {wireless_count} wireless, {telecom_count} telecom")
        print(f"📊 Provider breakdown: {priority_providers}")
        
        return {
            "tested": len(test_proxies),
            "verified": verified_count,
            "wireless": wireless_count,
            "telecom": telecom_count,
            "providers": priority_providers
        }

# Initialize telecom hunter
telecom_hunter = TelecomPriorityProxyHunter()

@app.route('/')
def index():
    return send_file('dashboard.html')

@app.route('/api/stats')
def get_stats():
    cursor = telecom_hunter.conn.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified,
            SUM(CASE WHEN status = 'verified' AND is_wireless = 1 THEN 1 ELSE 0 END) as wireless,
            SUM(CASE WHEN status = 'verified' AND is_telecom = 1 THEN 1 ELSE 0 END) as telecom,
            MAX(last_tested) as last_update
        FROM telecom_proxies
    ''')
    
    row = cursor.fetchone()
    return jsonify({
        "total": row[0] or 0,
        "verified": row[1] or 0,
        "mobile": row[2] or 0,  # wireless count for mobile
        "residential": row[3] or 0,  # telecom count for residential
        "last_update": row[4] or "Never"
    })

@app.route('/api/residential-proxies')
def get_residential_proxies():
    proxies = telecom_hunter.get_verified_telecom_proxies()
    proxy_list = []
    
    for row in proxies:
        proxy_list.append({
            "proxy": row[0],
            "ip": row[1],
            "isp": f"{row[2]} - {row[4]}",
            "is_mobile": bool(row[3]),
            "response_time": row[5],
            "success_rate": row[6] or 0,
            "status": "verified"
        })
    
    return jsonify({"proxies": proxy_list})

@app.route('/api/hunt-proxies', methods=['POST'])
def hunt_proxies():
    total = telecom_hunter.hunt_telecom_proxies_enhanced()
    return jsonify({"total": total})

@app.route('/api/validate-all', methods=['POST'])
def validate_all():
    if not telecom_hunter.proxies:
        telecom_hunter.hunt_telecom_proxies_enhanced()
    
    results = telecom_hunter.test_all_telecom_proxies()
    return jsonify(results)

@app.route('/api/retest-residential', methods=['POST'])
def retest_residential():
    # Get existing telecom proxies for retesting
    cursor = telecom_hunter.conn.execute('''
        SELECT proxy FROM telecom_proxies 
        WHERE status = 'verified' AND is_telecom = 1
    ''')
    
    proxies_to_test = [row[0] for row in cursor.fetchall()]
    
    if not proxies_to_test:
        return jsonify({"tested": 0, "verified": 0})
    
    verified_count = 0
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_proxy = {
            executor.submit(telecom_hunter.comprehensive_telecom_test, proxy): proxy 
            for proxy in proxies_to_test[:50]  # Limit for performance
        }
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result["success"]:
                telecom_hunter.save_telecom_proxy_to_db(result)
                verified_count += 1
    
    return jsonify({"tested": len(proxies_to_test), "verified": verified_count})

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    cursor = telecom_hunter.conn.execute('''
        DELETE FROM telecom_proxies 
        WHERE status = 'failed' 
        AND last_tested < datetime('now', '-24 hours')
    ''')
    removed_count = cursor.rowcount
    telecom_hunter.conn.commit()
    
    return jsonify({"removed": removed_count})

@app.route('/api/test-single', methods=['POST'])
def test_single():
    data = request.get_json()
    proxy = data.get('proxy')
    
    if not proxy:
        return jsonify({"error": "No proxy provided"}), 400
    
    result = telecom_hunter.comprehensive_telecom_test(proxy)
    return jsonify(result)

if __name__ == '__main__':
    print("🔥 RedTeamAbel's Telecom Priority Proxy Hunter Starting...")
    print("📱 Prioritizing AT&T, Verizon, T-Mobile, and US Telecoms")
    print("🌐 Access at: http://localhost:8082")
    
    app.run(host='0.0.0.0', port=8082, debug=False, threaded=True)

