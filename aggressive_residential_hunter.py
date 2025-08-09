#!/usr/bin/env python3
"""
RedTeamAbel's Aggressive Residential Proxy Hunter
Targets paid providers: Oxylabs, Bright Data, SOAX, Webshare, NetNut, etc.
Full red team mode - hitting them where it hurts!
"""

import os
import sys
import time
import json
import random
import requests
import threading
import sqlite3
import re
import base64
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
import socket

app = Flask(__name__)
app.secret_key = 'redteamabel_aggressive_hunter_2025'

class AggressiveResidentialHunter:
    def __init__(self):
        self.proxies = []
        self.residential_proxies = []
        self.premium_provider_proxies = []
        self.db_path = 'aggressive_residential_hunter.db'
        self.init_database()
        
        # Premium Residential Proxy Providers (Our Targets)
        self.premium_providers = {
            "oxylabs": {
                "keywords": ["oxylabs", "oxy labs", "datacenter oxylabs"],
                "priority": 10,
                "type": "premium_residential"
            },
            "bright_data": {
                "keywords": ["bright data", "brightdata", "luminati", "bright data ltd"],
                "priority": 10,
                "type": "premium_residential"
            },
            "soax": {
                "keywords": ["soax", "soax ltd", "soax proxy"],
                "priority": 9,
                "type": "premium_residential"
            },
            "webshare": {
                "keywords": ["webshare", "webshare.io", "webshare proxy"],
                "priority": 9,
                "type": "premium_residential"
            },
            "netnut": {
                "keywords": ["netnut", "net nut", "netnut proxy"],
                "priority": 9,
                "type": "premium_residential"
            },
            "smartproxy": {
                "keywords": ["smartproxy", "smart proxy", "decodo", "smartproxy.com"],
                "priority": 8,
                "type": "premium_residential"
            },
            "rayobyte": {
                "keywords": ["rayobyte", "blazing seo", "blazingseo"],
                "priority": 8,
                "type": "premium_residential"
            },
            "iproyal": {
                "keywords": ["iproyal", "ip royal", "royal proxies"],
                "priority": 8,
                "type": "premium_residential"
            },
            "proxy_seller": {
                "keywords": ["proxy-seller", "proxyseller", "proxy seller"],
                "priority": 7,
                "type": "premium_residential"
            },
            "storm_proxies": {
                "keywords": ["storm proxies", "stormproxies", "storm proxy"],
                "priority": 7,
                "type": "premium_residential"
            },
            "proxy_cheap": {
                "keywords": ["proxy-cheap", "proxycheap", "proxy cheap"],
                "priority": 7,
                "type": "premium_residential"
            },
            "shifter": {
                "keywords": ["shifter", "microleaves", "shifter proxy"],
                "priority": 7,
                "type": "premium_residential"
            }
        }
        
        # US Telecom Providers (High Value Targets)
        self.us_telecoms = {
            "verizon": {"priority": 10, "keywords": ["verizon", "vzw", "cellco", "verizon wireless"]},
            "att": {"priority": 10, "keywords": ["at&t", "att", "cingular", "sbc", "at&t mobility"]},
            "tmobile": {"priority": 10, "keywords": ["t-mobile", "tmobile", "metro pcs", "metropcs"]},
            "sprint": {"priority": 9, "keywords": ["sprint", "boost mobile", "virgin mobile"]},
            "comcast": {"priority": 8, "keywords": ["comcast", "xfinity", "comcast cable"]},
            "charter": {"priority": 8, "keywords": ["charter", "spectrum", "time warner cable"]},
            "cox": {"priority": 7, "keywords": ["cox", "cox communications", "cox cable"]},
            "altice": {"priority": 7, "keywords": ["altice", "optimum", "cablevision"]},
            "frontier": {"priority": 6, "keywords": ["frontier", "frontier communications"]},
            "centurylink": {"priority": 6, "keywords": ["centurylink", "lumen", "qwest"]}
        }
        
    def init_database(self):
        """Initialize aggressive hunting database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS aggressive_proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE,
                ip TEXT,
                country TEXT,
                is_residential BOOLEAN,
                is_premium_provider BOOLEAN,
                is_us_telecom BOOLEAN,
                provider_name TEXT,
                provider_priority INTEGER,
                isp TEXT,
                org TEXT,
                asn TEXT,
                response_time INTEGER,
                success_rate REAL,
                last_tested TIMESTAMP,
                times_tested INTEGER DEFAULT 0,
                times_successful INTEGER DEFAULT 0,
                status TEXT DEFAULT 'untested',
                first_discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_successful TIMESTAMP,
                source_url TEXT,
                discovery_method TEXT
            )
        ''')
        
        # Performance indexes for aggressive hunting
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_aggressive_priority 
            ON aggressive_proxies(is_premium_provider DESC, is_us_telecom DESC, provider_priority DESC, success_rate DESC)
        ''')
        
        self.conn.commit()
    
    def get_aggressive_proxy_sources(self):
        """Get comprehensive list of proxy sources including hidden ones"""
        sources = {
            # Public GitHub repositories
            "github_sources": [
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
                "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
                "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
                "https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
                "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
                "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
                "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
                "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
                "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"
            ],
            
            # Chinese/International sources (often have premium leaks)
            "chinese_sources": [
                "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list",
                "https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt",
                "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
                "https://raw.githubusercontent.com/stamparm/aux/master/fetch-some-list.txt",
                "https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.txt"
            ],
            
            # API endpoints (often leak premium proxies)
            "api_sources": [
                "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=US&format=textplain",
                "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&format=textplain",
                "https://www.proxy-list.download/api/v1/get?type=http",
                "https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
            ],
            
            # Pastebin and similar (often contain leaked premium lists)
            "paste_sources": [
                "https://pastebin.com/raw/7kKQgvzw",
                "https://pastebin.com/raw/kTEWsXWr",
                "https://pastebin.com/raw/Px3mW4jd"
            ],
            
            # Telegram channels and Discord leaks (simulated endpoints)
            "social_sources": [
                "https://t.me/s/proxy_list_channel",
                "https://discord.gg/proxy-leaks"
            ]
        }
        
        return sources
    
    def identify_premium_provider(self, ip_info):
        """Identify if proxy belongs to premium residential provider"""
        if not ip_info:
            return None, 0, False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("as", "").lower()
        
        # Check against premium providers
        for provider, details in self.premium_providers.items():
            for keyword in details["keywords"]:
                if keyword in isp or keyword in org or keyword in asn:
                    return provider, details["priority"], True
        
        # Check against US telecoms
        for provider, details in self.us_telecoms.items():
            for keyword in details["keywords"]:
                if keyword in isp or keyword in org or keyword in asn:
                    return provider, details["priority"], True
        
        return None, 0, False
    
    def is_residential_ip_aggressive(self, ip_info):
        """Aggressive residential IP detection"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        asn = ip_info.get("as", "").lower()
        
        # Premium provider indicators (these are definitely residential)
        premium_indicators = [
            "oxylabs", "bright data", "luminati", "soax", "webshare", "netnut",
            "smartproxy", "rayobyte", "iproyal", "proxy-seller", "storm proxies"
        ]
        
        for indicator in premium_indicators:
            if indicator in isp or indicator in org or indicator in asn:
                return True
        
        # US Telecom indicators (residential)
        telecom_indicators = [
            "verizon", "at&t", "t-mobile", "sprint", "comcast", "charter",
            "cox", "altice", "frontier", "centurylink", "wireless", "mobile",
            "cellular", "cable", "broadband", "fiber", "residential"
        ]
        
        for indicator in telecom_indicators:
            if indicator in isp or indicator in org:
                return True
        
        # Exclude obvious datacenters
        datacenter_keywords = [
            "hosting", "datacenter", "data center", "cloud", "server", "vpn",
            "amazon", "google", "microsoft", "digital ocean", "linode", "vultr"
        ]
        
        for keyword in datacenter_keywords:
            if keyword in isp or keyword in org:
                return False
        
        # If mobile flag is set, it's residential
        if ip_info.get("mobile", False):
            return True
        
        # If not hosting and not proxy, likely residential
        if not ip_info.get("hosting", False) and not ip_info.get("proxy", False):
            return True
        
        return False
    
    def get_comprehensive_ip_info_aggressive(self, ip_address):
        """Get comprehensive IP info with multiple sources"""
        info = {}
        
        # Primary source: ip-api.com (most comprehensive)
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,region,city,isp,org,as,mobile,proxy,hosting,query,status",
                timeout=10
            )
            data = response.json()
            if data["status"] == "success":
                info.update(data)
        except:
            pass
        
        # Secondary source: ipapi.co
        try:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=10)
            data = response.json()
            if not info.get("country"):
                info.update({
                    "country": data.get("country_name", "Unknown"),
                    "countryCode": data.get("country_code", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("org", "Unknown"),
                    "org": data.get("org", "Unknown")
                })
        except:
            pass
        
        # Tertiary source: ipinfo.io
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=10)
            data = response.json()
            if not info.get("org"):
                info.update({
                    "org": data.get("org", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "region": data.get("region", "Unknown")
                })
        except:
            pass
        
        return info if info else None
    
    def aggressive_proxy_test(self, proxy, test_count=3):
        """Aggressive proxy testing with premium provider detection"""
        results = []
        
        for attempt in range(test_count):
            try:
                ip, port = proxy.split(":")
                proxies = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
                
                # Test multiple endpoints aggressively
                test_urls = [
                    "https://api.ipify.org?format=json",
                    "https://httpbin.org/ip",
                    "https://ipapi.co/json/",
                    "https://api.myip.com",
                    "https://ipinfo.io/json"
                ]
                
                for url in test_urls:
                    try:
                        start_time = time.time()
                        response = requests.get(
                            url, 
                            proxies=proxies, 
                            timeout=15,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            }
                        )
                        response_time = int((time.time() - start_time) * 1000)
                        
                        if response.status_code == 200:
                            # Extract IP from different response formats
                            try:
                                data = response.json()
                                proxy_ip = data.get("ip") or data.get("origin") or data.get("query")
                                if not proxy_ip and "origin" in data:
                                    proxy_ip = data["origin"].split(",")[0].strip()
                            except:
                                continue
                            
                            if proxy_ip:
                                ip_info = self.get_comprehensive_ip_info_aggressive(proxy_ip)
                                
                                if ip_info and ip_info.get("countryCode") == "US":
                                    # Identify provider
                                    provider, priority, is_premium = self.identify_premium_provider(ip_info)
                                    is_residential = self.is_residential_ip_aggressive(ip_info)
                                    
                                    if is_residential or is_premium:
                                        results.append({
                                            "success": True,
                                            "proxy": proxy,
                                            "ip": proxy_ip,
                                            "response_time": response_time,
                                            "provider_name": provider,
                                            "provider_priority": priority,
                                            "is_premium_provider": is_premium,
                                            "is_residential": is_residential,
                                            "is_us_telecom": provider in self.us_telecoms if provider else False,
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
    
    def save_aggressive_proxy_to_db(self, proxy_result, source_url="", discovery_method=""):
        """Save aggressive proxy results to database"""
        if not proxy_result["success"]:
            return
            
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO aggressive_proxies 
                (proxy, ip, country, is_residential, is_premium_provider, is_us_telecom,
                 provider_name, provider_priority, isp, org, asn, response_time, success_rate,
                 last_tested, times_tested, times_successful, status, source_url, discovery_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proxy_result["proxy"],
                proxy_result["ip"],
                proxy_result["info"]["country"],
                proxy_result["is_residential"],
                proxy_result["is_premium_provider"],
                proxy_result["is_us_telecom"],
                proxy_result["provider_name"],
                proxy_result["provider_priority"],
                proxy_result["info"]["isp"],
                proxy_result["info"]["org"],
                proxy_result["info"].get("as", ""),
                proxy_result["response_time"],
                proxy_result["success_rate"],
                datetime.now(),
                proxy_result["total_tests"],
                int(proxy_result["total_tests"] * proxy_result["success_rate"]),
                "verified" if proxy_result["success_rate"] > 0.6 else "unstable",
                source_url,
                discovery_method
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
    
    def hunt_aggressive_residential_proxies(self):
        """Aggressive residential proxy hunting from all sources"""
        print("🔥 AGGRESSIVE RESIDENTIAL PROXY HUNTING INITIATED!")
        print("💀 Targeting: Oxylabs, Bright Data, SOAX, Webshare, NetNut, etc.")
        
        sources = self.get_aggressive_proxy_sources()
        all_proxies = set()
        successful_sources = 0
        
        # Hunt from GitHub sources
        print("📂 Hunting GitHub repositories...")
        for source in sources["github_sources"]:
            try:
                response = requests.get(source, timeout=25, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    proxies = self.extract_proxies_from_text(response.text)
                    all_proxies.update(proxies)
                    successful_sources += 1
                    print(f"✅ GitHub: {len(proxies)} proxies from {source}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ GitHub failed: {source}")
                continue
        
        # Hunt from Chinese sources
        print("🇨🇳 Hunting Chinese/International sources...")
        for source in sources["chinese_sources"]:
            try:
                response = requests.get(source, timeout=25)
                if response.status_code == 200:
                    proxies = self.extract_proxies_from_text(response.text)
                    all_proxies.update(proxies)
                    successful_sources += 1
                    print(f"✅ Chinese: {len(proxies)} proxies from {source}")
                time.sleep(1)
            except:
                continue
        
        # Hunt from API sources
        print("🔌 Hunting API endpoints...")
        for source in sources["api_sources"]:
            try:
                response = requests.get(source, timeout=25)
                if response.status_code == 200:
                    proxies = self.extract_proxies_from_text(response.text)
                    all_proxies.update(proxies)
                    successful_sources += 1
                    print(f"✅ API: {len(proxies)} proxies from {source}")
                time.sleep(2)
            except:
                continue
        
        # Store all proxies
        self.proxies = list(all_proxies)
        print(f"🎯 AGGRESSIVE HUNT COMPLETE: {len(self.proxies)} unique proxies from {successful_sources} sources")
        print(f"💀 Ready to identify premium residential providers!")
        
        return len(self.proxies)
    
    def extract_proxies_from_text(self, text):
        """Extract proxies from various text formats"""
        proxies = set()
        
        # Standard IP:PORT format
        ip_port_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}\b'
        matches = re.findall(ip_port_pattern, text)
        
        for match in matches:
            try:
                ip, port = match.split(':')
                if self.is_valid_ip(ip) and self.is_valid_port(port):
                    proxies.add(match)
            except:
                continue
        
        # JSON format extraction
        try:
            if text.strip().startswith('[') or text.strip().startswith('{'):
                data = json.loads(text)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            ip = item.get('ip') or item.get('host')
                            port = item.get('port')
                            if ip and port:
                                proxy = f"{ip}:{port}"
                                if self.is_valid_proxy_format(proxy):
                                    proxies.add(proxy)
        except:
            pass
        
        return proxies
    
    def is_valid_ip(self, ip):
        """Validate IP address"""
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
    
    def is_valid_proxy_format(self, proxy):
        """Validate proxy format"""
        try:
            ip, port = proxy.split(':')
            return self.is_valid_ip(ip) and self.is_valid_port(port)
        except:
            return False
    
    def test_all_aggressive_residential(self, max_workers=20, max_proxies=300):
        """Aggressive testing focused on residential and premium providers"""
        print("💀 AGGRESSIVE RESIDENTIAL TESTING INITIATED!")
        print("🎯 Prioritizing premium providers and US telecoms...")
        
        # Limit proxies for performance but increase for aggressive hunting
        test_proxies = random.sample(self.proxies, min(len(self.proxies), max_proxies))
        
        verified_count = 0
        premium_count = 0
        residential_count = 0
        telecom_count = 0
        provider_breakdown = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.aggressive_proxy_test, proxy): proxy 
                for proxy in test_proxies
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result["success"]:
                    self.save_aggressive_proxy_to_db(result, discovery_method="aggressive_hunt")
                    verified_count += 1
                    
                    if result["is_premium_provider"]:
                        premium_count += 1
                        provider = result["provider_name"]
                        if provider not in provider_breakdown:
                            provider_breakdown[provider] = 0
                        provider_breakdown[provider] += 1
                        
                        # Special logging for premium providers
                        priority_flag = "🔥" if result["provider_priority"] >= 9 else "⭐"
                        provider_flag = "💎" if result["is_premium_provider"] else "📱"
                        print(f"💀 {priority_flag} {provider_flag} PREMIUM HIT: {result['proxy']} - {result['provider_name']} - {result['info']['isp']}")
                    
                    if result["is_residential"]:
                        residential_count += 1
                    
                    if result["is_us_telecom"]:
                        telecom_count += 1
                        telecom_flag = "📱" if result["provider_name"] in ["verizon", "att", "tmobile"] else "🏠"
                        print(f"🇺🇸 {telecom_flag} TELECOM HIT: {result['proxy']} - {result['provider_name']} - {result['info']['isp']}")
        
        print(f"💀 AGGRESSIVE TESTING COMPLETE!")
        print(f"🎯 Results: {verified_count} verified, {premium_count} premium, {residential_count} residential, {telecom_count} telecom")
        print(f"💎 Premium provider breakdown: {provider_breakdown}")
        
        return {
            "tested": len(test_proxies),
            "verified": verified_count,
            "premium": premium_count,
            "residential": residential_count,
            "telecom": telecom_count,
            "providers": provider_breakdown
        }
    
    def get_verified_aggressive_proxies(self, premium_priority=True):
        """Get verified proxies with premium provider priority"""
        query = '''
            SELECT proxy, ip, provider_name, is_premium_provider, is_us_telecom, 
                   isp, response_time, success_rate, provider_priority
            FROM aggressive_proxies 
            WHERE country = 'United States' AND success_rate > 0.5 AND status = 'verified'
            ORDER BY {} DESC, provider_priority DESC, success_rate DESC, response_time ASC
        '''.format("is_premium_provider" if premium_priority else "is_us_telecom")
        
        cursor = self.conn.execute(query)
        return cursor.fetchall()

# Initialize aggressive hunter
aggressive_hunter = AggressiveResidentialHunter()

@app.route('/')
def index():
    return send_file('dashboard.html')

@app.route('/api/stats')
def get_stats():
    cursor = aggressive_hunter.conn.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified,
            SUM(CASE WHEN status = 'verified' AND is_premium_provider = 1 THEN 1 ELSE 0 END) as premium,
            SUM(CASE WHEN status = 'verified' AND is_residential = 1 THEN 1 ELSE 0 END) as residential,
            MAX(last_tested) as last_update
        FROM aggressive_proxies
    ''')
    
    row = cursor.fetchone()
    return jsonify({
        "total": row[0] or 0,
        "verified": row[1] or 0,
        "mobile": row[2] or 0,  # premium count for mobile
        "residential": row[3] or 0,
        "last_update": row[4] or "Never"
    })

@app.route('/api/residential-proxies')
def get_residential_proxies():
    proxies = aggressive_hunter.get_verified_aggressive_proxies()
    proxy_list = []
    
    for row in proxies:
        provider_display = f"💎 {row[2]}" if row[3] else f"📱 {row[2]}" if row[4] else row[2]
        proxy_list.append({
            "proxy": row[0],
            "ip": row[1],
            "isp": f"{provider_display} - {row[5]}",
            "is_mobile": bool(row[3] or row[4]),  # premium or telecom
            "response_time": row[6],
            "success_rate": row[7] or 0,
            "status": "verified"
        })
    
    return jsonify({"proxies": proxy_list})

@app.route('/api/hunt-proxies', methods=['POST'])
def hunt_proxies():
    total = aggressive_hunter.hunt_aggressive_residential_proxies()
    return jsonify({"total": total})

@app.route('/api/validate-all', methods=['POST'])
def validate_all():
    if not aggressive_hunter.proxies:
        aggressive_hunter.hunt_aggressive_residential_proxies()
    
    results = aggressive_hunter.test_all_aggressive_residential()
    return jsonify(results)

@app.route('/api/retest-residential', methods=['POST'])
def retest_residential():
    cursor = aggressive_hunter.conn.execute('''
        SELECT proxy FROM aggressive_proxies 
        WHERE status = 'verified' AND (is_residential = 1 OR is_premium_provider = 1)
        ORDER BY provider_priority DESC
        LIMIT 100
    ''')
    
    proxies_to_test = [row[0] for row in cursor.fetchall()]
    
    if not proxies_to_test:
        return jsonify({"tested": 0, "verified": 0})
    
    verified_count = 0
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_proxy = {
            executor.submit(aggressive_hunter.aggressive_proxy_test, proxy): proxy 
            for proxy in proxies_to_test
        }
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result["success"]:
                aggressive_hunter.save_aggressive_proxy_to_db(result, discovery_method="retest")
                verified_count += 1
    
    return jsonify({"tested": len(proxies_to_test), "verified": verified_count})

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    cursor = aggressive_hunter.conn.execute('''
        DELETE FROM aggressive_proxies 
        WHERE status = 'failed' 
        AND last_tested < datetime('now', '-24 hours')
    ''')
    removed_count = cursor.rowcount
    aggressive_hunter.conn.commit()
    
    return jsonify({"removed": removed_count})

@app.route('/api/test-single', methods=['POST'])
def test_single():
    data = request.get_json()
    proxy = data.get('proxy')
    
    if not proxy:
        return jsonify({"error": "No proxy provided"}), 400
    
    result = aggressive_hunter.aggressive_proxy_test(proxy)
    return jsonify(result)

if __name__ == '__main__':
    print("💀 RedTeamAbel's AGGRESSIVE Residential Proxy Hunter Starting...")
    print("🎯 TARGETING: Oxylabs, Bright Data, SOAX, Webshare, NetNut, Smartproxy, Rayobyte, IPRoyal")
    print("📱 PRIORITY: AT&T, Verizon, T-Mobile, Sprint, Comcast, Charter")
    print("🌐 Access at: http://localhost:8083")
    print("💀 RED TEAM MODE: ACTIVATED!")
    
    app.run(host='0.0.0.0', port=8083, debug=False, threaded=True)

