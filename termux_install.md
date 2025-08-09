# 🔥 RedTeamAbel's Mobile Proxy Hunter - Termux Installation

## Prerequisites
1. Install **Termux** from F-Droid (NOT Google Play Store)
2. Install **Termux:API** from F-Droid
3. Ensure you have a stable internet connection

## One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/your-repo/mobile-proxy-hunter/main/install.sh | bash
```

## Manual Installation

### Step 1: Update Termux
```bash
pkg update && pkg upgrade -y
```

### Step 2: Install Required Packages
```bash
pkg install -y python python-pip git curl wget nodejs npm termux-api
```

### Step 3: Install Python Dependencies
```bash
pip install requests flask gunicorn
```

### Step 4: Download the Toolkit
```bash
cd ~
git clone https://github.com/your-repo/mobile-proxy-hunter.git
cd mobile-proxy-hunter
```

### Step 5: Make Scripts Executable
```bash
chmod +x *.sh *.py
```

## Quick Start

### Launch the Mobile Proxy Hunter
```bash
cd ~/mobile-proxy-hunter
python3 mobile_proxy_hunter.py
```

### Access the Web Interface
Open your browser and navigate to:
```
http://localhost:8080
```

## Advanced Usage

### Command Line Interface
```bash
# Hunt for fresh proxies
python3 mobile_proxy_hunter.py --hunt

# Test specific proxy
python3 mobile_proxy_hunter.py --test 192.168.1.1:8080

# Filter USA residential only
python3 mobile_proxy_hunter.py --filter-usa-residential

# Export results
python3 mobile_proxy_hunter.py --export results.json
```

### Termux Widget Integration
Create a widget for quick access:
```bash
mkdir -p ~/.shortcuts
echo "cd ~/mobile-proxy-hunter && python3 mobile_proxy_hunter.py" > ~/.shortcuts/ProxyHunter
chmod +x ~/.shortcuts/ProxyHunter
```

## Features

### 🎯 Proxy Discovery
- Multi-source proxy aggregation
- Real-time proxy validation
- Geographic filtering (USA focus)
- Residential vs Datacenter classification

### 🕵️ Stealth Testing
- IP geolocation verification
- ISP/Organization analysis
- Response time measurement
- Anonymity level assessment

### 📱 Mobile Optimized
- Touch-friendly interface
- Responsive design
- Low resource usage
- Offline capability

### 🔧 Advanced Features
- Concurrent proxy testing
- JSON export/import
- Custom proxy lists
- API integration

## Troubleshooting

### Common Issues

**Permission Denied**
```bash
termux-setup-storage
```

**Network Issues**
```bash
# Check internet connectivity
ping -c 4 8.8.8.8

# Reset network
termux-reload-settings
```

**Python Module Errors**
```bash
pip install --upgrade pip
pip install --force-reinstall requests flask
```

### Performance Optimization

**For Low-End Devices**
```bash
# Reduce concurrent threads
export MAX_WORKERS=5

# Limit proxy testing
export MAX_PROXIES=50
```

**For High-End Devices**
```bash
# Increase performance
export MAX_WORKERS=50
export MAX_PROXIES=1000
```

## Security Considerations

### Operational Security (OPSEC)
- Use VPN when hunting proxies
- Rotate testing intervals
- Avoid suspicious patterns
- Monitor for detection

### Legal Compliance
- Only use for authorized testing
- Respect rate limits
- Follow local laws
- Document activities

## One-Liners for Quick Operations

### Hunt and Test in One Command
```bash
python3 mobile_proxy_hunter.py --hunt --test --filter-usa --export
```

### Quick Residential Check
```bash
curl -s "http://localhost:8080/api/stealth-test" -X POST -H "Content-Type: application/json" -d '{"proxy":"IP:PORT"}' | jq .
```

### Export Working Proxies
```bash
curl -s "http://localhost:8080/api/proxies" | jq -r '.proxies[]' > working_proxies.txt
```

## Integration with Other Tools

### Burp Suite
```bash
# Export proxies for Burp
python3 mobile_proxy_hunter.py --export-burp burp_proxies.txt
```

### Metasploit
```bash
# Generate Metasploit resource script
python3 mobile_proxy_hunter.py --export-msf proxies.rc
```

### Custom Scripts
```python
import requests

# Use the API programmatically
response = requests.get("http://localhost:8080/api/proxies")
proxies = response.json()["proxies"]

for proxy in proxies:
    print(f"Testing proxy: {proxy}")
    # Your custom logic here
```

## Support

For issues, feature requests, or contributions:
- GitHub: https://github.com/your-repo/mobile-proxy-hunter
- Telegram: @RedTeamAbel
- Discord: RedTeamAbel#1337

---

**Remember**: This tool is for authorized penetration testing and security research only. Always obtain proper authorization before testing networks you don't own.

🔥 **Happy Hunting, RedTeamAbel!** 🔥

