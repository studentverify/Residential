#!/usr/bin/env python3
"""
RedTeamAbel's Dashboard Server
Dedicated server for the live proxy dashboard
"""

import os
import sys
import time
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

class DashboardServer:
    def __init__(self):
        self.db_path = 'proxy_hunter.db'
        self.init_database()
        
    def init_database(self):
        """Initialize database if it doesn't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
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
                status TEXT DEFAULT 'untested',
                first_discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_successful TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def get_stats(self):
        """Get current proxy statistics"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified,
                SUM(CASE WHEN status = 'verified' AND is_mobile_isp = 1 THEN 1 ELSE 0 END) as mobile,
                SUM(CASE WHEN status = 'verified' AND is_residential = 1 THEN 1 ELSE 0 END) as residential,
                MAX(last_tested) as last_update
            FROM proxies
        ''')
        
        row = cursor.fetchone()
        return {
            "total": row[0] or 0,
            "verified": row[1] or 0,
            "mobile": row[2] or 0,
            "residential": row[3] or 0,
            "last_update": row[4] or "Never"
        }
    
    def get_residential_proxies(self, limit=50):
        """Get verified residential proxies"""
        cursor = self.conn.execute('''
            SELECT proxy, ip, isp, is_mobile_isp, response_time, success_rate, status, last_tested
            FROM proxies 
            WHERE status = 'verified' AND country = 'United States' AND is_residential = 1
            ORDER BY success_rate DESC, response_time ASC
            LIMIT ?
        ''', (limit,))
        
        proxies = []
        for row in cursor.fetchall():
            proxies.append({
                "proxy": row[0],
                "ip": row[1],
                "isp": row[2],
                "is_mobile": bool(row[3]),
                "response_time": row[4],
                "success_rate": row[5] or 0,
                "status": row[6],
                "last_tested": row[7]
            })
        
        return proxies
    
    def hunt_fresh_proxies(self):
        """Hunt for fresh proxies"""
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
        ]
        
        new_proxies = set()
        
        for source in sources:
            try:
                response = requests.get(source, timeout=20)
                if response.status_code == 200:
                    proxies = [p.strip() for p in response.text.splitlines() 
                             if p.strip() and ':' in p.strip()]
                    new_proxies.update(proxies)
            except:
                continue
        
        # Store new proxies
        stored_count = 0
        for proxy in new_proxies:
            try:
                self.conn.execute('''
                    INSERT OR IGNORE INTO proxies (proxy, status) VALUES (?, 'untested')
                ''', (proxy,))
                stored_count += 1
            except:
                continue
        
        self.conn.commit()
        return {"total": len(new_proxies), "stored": stored_count}
    
    def get_ip_info(self, ip_address):
        """Get IP information"""
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,isp,org,as,mobile,proxy,hosting",
                timeout=10
            )
            data = response.json()
            if data["status"] == "success":
                return data
        except:
            pass
        return None
    
    def is_mobile_isp(self, ip_info):
        """Check if IP is from mobile ISP"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        
        mobile_carriers = ["verizon", "t-mobile", "at&t", "sprint", "cricket"]
        mobile_keywords = ["wireless", "mobile", "cellular"]
        
        for carrier in mobile_carriers:
            if carrier in isp or carrier in org:
                return True
        
        for keyword in mobile_keywords:
            if keyword in isp or keyword in org:
                return True
        
        return ip_info.get("mobile", False)
    
    def is_residential_ip(self, ip_info):
        """Check if IP is residential"""
        if not ip_info:
            return False
            
        if self.is_mobile_isp(ip_info):
            return True
            
        isp = ip_info.get("isp", "").lower()
        datacenter_keywords = ["hosting", "datacenter", "cloud", "server"]
        
        for keyword in datacenter_keywords:
            if keyword in isp:
                return False
        
        return not ip_info.get("hosting", False)
    
    def test_proxy(self, proxy):
        """Test a single proxy"""
        try:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            
            start_time = time.time()
            response = requests.get("https://api.ipify.org?format=json", 
                                  proxies=proxies, timeout=15)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                proxy_ip = response.json()["ip"]
                ip_info = self.get_ip_info(proxy_ip)
                
                if ip_info and ip_info.get("countryCode") == "US":
                    return {
                        "success": True,
                        "proxy": proxy,
                        "ip": proxy_ip,
                        "response_time": response_time,
                        "is_residential": self.is_residential_ip(ip_info),
                        "is_mobile": self.is_mobile_isp(ip_info),
                        "info": ip_info
                    }
        except:
            pass
        
        return {"success": False, "proxy": proxy}
    
    def validate_all_proxies(self, max_workers=15):
        """Validate all untested proxies"""
        cursor = self.conn.execute('''
            SELECT proxy FROM proxies 
            WHERE status = 'untested'
            LIMIT 100
        ''')
        
        proxies_to_test = [row[0] for row in cursor.fetchall()]
        
        if not proxies_to_test:
            return {"tested": 0, "verified": 0, "residential": 0}
        
        verified_count = 0
        residential_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies_to_test
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                proxy = result["proxy"]
                
                if result["success"]:
                    self.conn.execute('''
                        UPDATE proxies SET
                            ip = ?, country = ?, is_residential = ?, is_mobile_isp = ?,
                            isp = ?, org = ?, response_time = ?, last_tested = ?,
                            times_tested = times_tested + 1,
                            times_successful = times_successful + 1,
                            status = 'verified',
                            last_successful = ?
                        WHERE proxy = ?
                    ''', (
                        result["ip"], result["info"]["country"], result["is_residential"],
                        result["is_mobile"], result["info"]["isp"], result["info"]["org"],
                        result["response_time"], datetime.now(), datetime.now(), proxy
                    ))
                    
                    verified_count += 1
                    if result["is_residential"]:
                        residential_count += 1
                else:
                    self.conn.execute('''
                        UPDATE proxies SET
                            last_tested = ?, times_tested = times_tested + 1,
                            status = 'failed'
                        WHERE proxy = ?
                    ''', (datetime.now(), proxy))
        
        self.conn.commit()
        
        return {
            "tested": len(proxies_to_test),
            "verified": verified_count,
            "residential": residential_count
        }
    
    def retest_residential_proxies(self):
        """Retest existing residential proxies"""
        cursor = self.conn.execute('''
            SELECT proxy FROM proxies 
            WHERE status = 'verified' AND is_residential = 1
        ''')
        
        proxies_to_test = [row[0] for row in cursor.fetchall()]
        
        if not proxies_to_test:
            return {"tested": 0, "verified": 0}
        
        verified_count = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies_to_test
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                proxy = result["proxy"]
                
                if result["success"]:
                    self.conn.execute('''
                        UPDATE proxies SET
                            response_time = ?, last_tested = ?,
                            times_tested = times_tested + 1,
                            times_successful = times_successful + 1,
                            last_successful = ?
                        WHERE proxy = ?
                    ''', (result["response_time"], datetime.now(), datetime.now(), proxy))
                    verified_count += 1
                else:
                    self.conn.execute('''
                        UPDATE proxies SET
                            last_tested = ?, times_tested = times_tested + 1,
                            status = 'failed'
                        WHERE proxy = ?
                    ''', (datetime.now(), proxy))
        
        self.conn.commit()
        
        return {"tested": len(proxies_to_test), "verified": verified_count}
    
    def cleanup_database(self):
        """Clean up old and failed proxies"""
        cursor = self.conn.execute('''
            DELETE FROM proxies 
            WHERE status = 'failed' 
            AND last_tested < datetime('now', '-24 hours')
        ''')
        removed_count = cursor.rowcount
        
        self.conn.commit()
        return {"removed": removed_count}

# Initialize dashboard server
dashboard = DashboardServer()

@app.route('/')
def index():
    return send_file('dashboard.html')

@app.route('/api/stats')
def get_stats():
    return jsonify(dashboard.get_stats())

@app.route('/api/residential-proxies')
def get_residential_proxies():
    proxies = dashboard.get_residential_proxies()
    return jsonify({"proxies": proxies})

@app.route('/api/hunt-proxies', methods=['POST'])
def hunt_proxies():
    result = dashboard.hunt_fresh_proxies()
    return jsonify(result)

@app.route('/api/validate-all', methods=['POST'])
def validate_all():
    result = dashboard.validate_all_proxies()
    return jsonify(result)

@app.route('/api/retest-residential', methods=['POST'])
def retest_residential():
    result = dashboard.retest_residential_proxies()
    return jsonify(result)

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    result = dashboard.cleanup_database()
    return jsonify(result)

@app.route('/api/test-single', methods=['POST'])
def test_single():
    data = request.get_json()
    proxy = data.get('proxy')
    
    if not proxy:
        return jsonify({"error": "No proxy provided"}), 400
    
    result = dashboard.test_proxy(proxy)
    return jsonify(result)

if __name__ == '__main__':
    print("🔥 RedTeamAbel's Dashboard Server Starting...")
    print("🌐 Access dashboard at: http://localhost:8081")
    print("📊 Real-time proxy intelligence ready!")
    
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)

