#!/usr/bin/env python3
"""
RedTeamAbel's Auto-Refresh Daemon
Continuously hunts and validates proxies in the background
Keeps your proxy arsenal fresh 24/7
"""

import os
import sys
import time
import json
import random
import sqlite3
import requests
import threading
import schedule
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

class AutoRefreshDaemon:
    def __init__(self):
        self.db_path = 'proxy_hunter.db'
        self.running = True
        self.last_hunt = 0
        self.last_validation = 0
        self.hunt_interval = 3600  # 1 hour
        self.validation_interval = 1800  # 30 minutes
        self.cleanup_interval = 7200  # 2 hours
        self.max_workers = 15  # Optimized for mobile
        self.init_database()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for daemon operations"""
        self.log_file = 'auto_refresh.log'
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")
        except:
            pass
    
    def init_database(self):
        """Initialize SQLite database"""
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
        
        # Add performance index
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_status_success 
            ON proxies(status, success_rate, response_time)
        ''')
        
        self.conn.commit()
    
    def get_proxy_sources(self):
        """Get list of proxy sources with rotation"""
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
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt"
        ]
        
        # Randomize source order to distribute load
        random.shuffle(sources)
        return sources
    
    def hunt_fresh_proxies(self):
        """Hunt for fresh proxies from multiple sources"""
        self.log("🔍 Starting fresh proxy hunt...")
        
        sources = self.get_proxy_sources()
        new_proxies = set()
        successful_sources = 0
        
        for source in sources:
            try:
                self.log(f"Fetching from: {source}")
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
                    
                    new_proxies.update(valid_proxies)
                    successful_sources += 1
                    self.log(f"✅ Fetched {len(valid_proxies)} valid proxies from source")
                    
                    # Small delay to be respectful
                    time.sleep(2)
                    
            except Exception as e:
                self.log(f"❌ Failed to fetch from {source}: {e}", "ERROR")
                continue
        
        # Store new proxies in database
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
        self.last_hunt = time.time()
        
        self.log(f"🎯 Hunt complete: {len(new_proxies)} unique proxies from {successful_sources} sources")
        self.log(f"📦 Stored {stored_count} new proxies in database")
        
        return len(new_proxies)
    
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
    
    def get_ip_info(self, ip_address):
        """Get IP information with fallbacks"""
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=country,countryCode,region,city,isp,org,as,mobile,proxy,hosting,query,status",
                timeout=10
            )
            data = response.json()
            if data["status"] == "success":
                return {
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
                }
        except:
            pass
        return None
    
    def is_mobile_isp(self, ip_info):
        """Check if IP belongs to mobile ISP"""
        if not ip_info:
            return False
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        
        mobile_carriers = [
            "verizon", "t-mobile", "at&t", "att", "sprint", "boost mobile",
            "cricket", "metro pcs", "tracfone", "straight talk", "mint mobile",
            "visible", "xfinity mobile", "spectrum mobile", "us cellular"
        ]
        
        mobile_keywords = ["wireless", "mobile", "cellular", "lte", "5g", "4g"]
        
        for carrier in mobile_carriers:
            if carrier in isp or carrier in org:
                return True
        
        for keyword in mobile_keywords:
            if keyword in isp or keyword in org:
                return True
        
        return ip_info.get("is_mobile", False)
    
    def is_residential_ip(self, ip_info):
        """Check if IP is residential"""
        if not ip_info:
            return False
            
        if self.is_mobile_isp(ip_info):
            return True
            
        isp = ip_info.get("isp", "").lower()
        org = ip_info.get("org", "").lower()
        
        residential_isps = [
            "comcast", "charter", "cox", "altice", "frontier", "centurylink",
            "windstream", "mediacom", "sparklight", "optimum", "xfinity", "spectrum"
        ]
        
        datacenter_keywords = [
            "hosting", "datacenter", "cloud", "server", "vpn", "proxy",
            "amazon", "google", "microsoft", "digital ocean"
        ]
        
        for keyword in datacenter_keywords:
            if keyword in isp or keyword in org:
                return False
        
        for residential_isp in residential_isps:
            if residential_isp in isp or residential_isp in org:
                return True
        
        return not ip_info.get("is_hosting", False) and not ip_info.get("is_proxy", False)
    
    def test_proxy(self, proxy):
        """Test a single proxy comprehensively"""
        try:
            ip, port = proxy.split(":")
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            start_time = time.time()
            response = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=15,
                headers={'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0'}
            )
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                proxy_ip = response.json()["ip"]
                ip_info = self.get_ip_info(proxy_ip)
                
                if ip_info and ip_info.get("country_code") == "US":
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
    
    def validate_existing_proxies(self):
        """Validate existing proxies in database"""
        self.log("⚡ Starting proxy validation...")
        
        # Get proxies that need validation (untested or old)
        cursor = self.conn.execute('''
            SELECT proxy FROM proxies 
            WHERE status IN ('untested', 'verified', 'unstable') 
            AND (last_tested IS NULL OR last_tested < datetime('now', '-1 hour'))
            ORDER BY 
                CASE WHEN status = 'verified' THEN 1 
                     WHEN status = 'unstable' THEN 2 
                     ELSE 3 END,
                last_tested ASC
            LIMIT 100
        ''')
        
        proxies_to_test = [row[0] for row in cursor.fetchall()]
        
        if not proxies_to_test:
            self.log("No proxies need validation")
            return
        
        self.log(f"Testing {len(proxies_to_test)} proxies...")
        
        verified_count = 0
        mobile_count = 0
        residential_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies_to_test
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                proxy = result["proxy"]
                
                # Update database
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
                    if result["is_mobile"]:
                        mobile_count += 1
                    if result["is_residential"]:
                        residential_count += 1
                        
                else:
                    self.conn.execute('''
                        UPDATE proxies SET
                            last_tested = ?, times_tested = times_tested + 1,
                            status = CASE 
                                WHEN times_tested > 3 THEN 'failed'
                                ELSE 'unstable'
                            END
                        WHERE proxy = ?
                    ''', (datetime.now(), proxy))
        
        self.conn.commit()
        self.last_validation = time.time()
        
        self.log(f"✅ Validation complete: {verified_count} verified, {mobile_count} mobile, {residential_count} residential")
    
    def cleanup_database(self):
        """Clean up old and failed proxies"""
        self.log("🧹 Starting database cleanup...")
        
        # Remove old failed proxies
        cursor = self.conn.execute('''
            DELETE FROM proxies 
            WHERE status = 'failed' 
            AND last_tested < datetime('now', '-24 hours')
        ''')
        deleted_failed = cursor.rowcount
        
        # Remove very old untested proxies
        cursor = self.conn.execute('''
            DELETE FROM proxies 
            WHERE status = 'untested' 
            AND first_discovered < datetime('now', '-48 hours')
        ''')
        deleted_untested = cursor.rowcount
        
        # Update success rates
        self.conn.execute('''
            UPDATE proxies 
            SET success_rate = CAST(times_successful AS REAL) / times_tested
            WHERE times_tested > 0
        ''')
        
        self.conn.commit()
        
        self.log(f"🧹 Cleanup complete: removed {deleted_failed} failed, {deleted_untested} old untested proxies")
    
    def get_stats(self):
        """Get current database statistics"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified,
                SUM(CASE WHEN status = 'verified' AND is_mobile_isp = 1 THEN 1 ELSE 0 END) as mobile,
                SUM(CASE WHEN status = 'verified' AND is_residential = 1 THEN 1 ELSE 0 END) as residential
            FROM proxies
        ''')
        
        return cursor.fetchone()
    
    def run_cycle(self):
        """Run one complete cycle of operations"""
        current_time = time.time()
        
        # Hunt for new proxies
        if current_time - self.last_hunt > self.hunt_interval:
            try:
                self.hunt_fresh_proxies()
            except Exception as e:
                self.log(f"Hunt failed: {e}", "ERROR")
        
        # Validate existing proxies
        if current_time - self.last_validation > self.validation_interval:
            try:
                self.validate_existing_proxies()
            except Exception as e:
                self.log(f"Validation failed: {e}", "ERROR")
        
        # Cleanup database
        if current_time % self.cleanup_interval < 60:  # Run cleanup roughly every 2 hours
            try:
                self.cleanup_database()
            except Exception as e:
                self.log(f"Cleanup failed: {e}", "ERROR")
        
        # Log current stats
        stats = self.get_stats()
        self.log(f"📊 Current stats: {stats[0]} total, {stats[1]} verified, {stats[2]} mobile, {stats[3]} residential")
    
    def run_daemon(self):
        """Main daemon loop"""
        self.log("🚀 Auto-Refresh Daemon started")
        self.log(f"Hunt interval: {self.hunt_interval}s, Validation interval: {self.validation_interval}s")
        
        # Initial hunt and validation
        try:
            self.hunt_fresh_proxies()
            time.sleep(30)  # Brief pause
            self.validate_existing_proxies()
        except Exception as e:
            self.log(f"Initial setup failed: {e}", "ERROR")
        
        # Main loop
        while self.running:
            try:
                self.run_cycle()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.log("Daemon stopped by user")
                break
            except Exception as e:
                self.log(f"Daemon error: {e}", "ERROR")
                time.sleep(60)
        
        self.log("🛑 Auto-Refresh Daemon stopped")

def main():
    daemon = AutoRefreshDaemon()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            stats = daemon.get_stats()
            print(f"Total: {stats[0]}, Verified: {stats[1]}, Mobile: {stats[2]}, Residential: {stats[3]}")
            return
        elif sys.argv[1] == "--hunt":
            daemon.hunt_fresh_proxies()
            return
        elif sys.argv[1] == "--validate":
            daemon.validate_existing_proxies()
            return
        elif sys.argv[1] == "--cleanup":
            daemon.cleanup_database()
            return
    
    # Run as daemon
    daemon.run_daemon()

if __name__ == "__main__":
    main()

