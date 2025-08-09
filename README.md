# 🦸‍♂️ RedTeamAbel's Ultimate Proxy Arsenal

**The Most Advanced Mobile Proxy Hunting & Tunneling Suite**  
**Bypassing Premium Provider Paywalls Since 2025**

![Ultimate Proxy Arsenal](https://img.shields.io/badge/Platform-Android%20Termux-green) ![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![License](https://img.shields.io/badge/License-MIT-red) ![Premium Bypass](https://img.shields.io/badge/Premium-Bypass-red) ![Grandma Friendly](https://img.shields.io/badge/Grandma-Friendly-pink)

## 🎯 Overview

RedTeamAbel's Mobile Proxy Hunter is a comprehensive toolkit designed specifically for Android devices running Termux. This tool enables red team operators to discover, test, and utilize residential proxies directly from their mobile devices - perfect for field operations where stealth and mobility are crucial.

### Key Features

- 🔍 **Multi-Source Proxy Discovery**: Aggregates proxies from multiple GitHub repositories and public sources
- 🇺🇸 **USA-Focused Filtering**: Specifically targets USA-based residential proxies
- 🏠 **Residential Detection**: Advanced heuristics to identify genuine residential IPs
- 📱 **Mobile-Optimized Interface**: Touch-friendly web interface designed for smartphones
- ⚡ **Concurrent Testing**: Multi-threaded proxy validation for speed
- 🕵️ **Stealth Analysis**: Comprehensive IP reputation and geolocation checks
- 🎯 **One-Click Operations**: Simplified workflow for rapid deployment

## 🚀 Quick Start

### Installation

1. **Install Termux** (from F-Droid, NOT Google Play Store)
2. **Run the one-liner**:
```bash
curl -sSL https://raw.githubusercontent.com/redteamabel/mobile-proxy-hunter/main/install.sh | bash
```

### Launch
```bash
cd ~/mobile-proxy-hunter
python3 mobile_proxy_hunter.py
```

Open your browser to: `http://localhost:8080`

## 📱 Mobile Interface

The web interface is specifically designed for mobile devices with:

- **Touch-optimized controls**
- **Responsive design** that works on any screen size
- **Dark theme** for OPSEC-friendly operations
- **Real-time status updates**
- **Minimal data usage**

### Main Features

#### 🎯 Proxy Hunter Controls
- **Hunt Fresh Proxies**: Discovers new proxies from multiple sources
- **Test All Proxies**: Validates proxy functionality and location
- **Load Proxy List**: Refreshes the available proxy dropdown

#### 🕵️ Stealth Test
- **Individual Proxy Testing**: Detailed analysis of selected proxies
- **Geolocation Verification**: Confirms USA location
- **Residential Classification**: Identifies genuine residential IPs
- **Response Time Measurement**: Performance metrics

#### 📊 Real-Time Statistics
- **USA Proxy Count**: Number of verified USA proxies
- **Residential Count**: Confirmed residential proxies
- **Current IP Display**: Shows your current public IP

## 🛠️ Technical Details

### Architecture

```
Mobile Proxy Hunter
├── mobile_proxy_hunter.py    # Main Flask application
├── templates/
│   └── mobile.html           # Mobile-optimized interface
├── termux_setup.sh          # Automated setup script
├── termux_install.md        # Detailed installation guide
└── README.md               # This file
```

### Proxy Discovery Sources

1. **TheSpeedX/PROXY-List** - High-volume proxy aggregation
2. **proxifly/free-proxy-list** - Curated proxy collection
3. **clarketm/proxy-list** - Additional proxy sources

### Filtering Algorithm

```python
def is_residential_ip(ip_info):
    # Residential indicators
    residential_keywords = [
        "telecom", "cable", "broadband", "fiber", 
        "mobile", "wireless", "internet", "communications"
    ]
    
    # Datacenter exclusions
    datacenter_keywords = [
        "hosting", "datacenter", "cloud", "server", 
        "vpn", "proxy", "amazon", "google", "microsoft"
    ]
    
    # Advanced heuristic analysis...
```

## 🔧 Advanced Usage

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

### API Endpoints

- `GET /api/current-ip` - Get current public IP
- `POST /api/hunt-proxies` - Discover new proxies
- `GET /api/proxies` - List available proxies
- `POST /api/stealth-test` - Test individual proxy
- `POST /api/test-all` - Bulk proxy testing

### Integration Examples

#### Burp Suite Integration
```bash
# Export proxies for Burp Suite
curl -s "http://localhost:8080/api/proxies" | jq -r '.proxies[]' > burp_proxies.txt
```

#### Python Script Integration
```python
import requests

# Get working residential proxies
response = requests.get("http://localhost:8080/api/proxies")
proxies = response.json()["proxies"]

for proxy in proxies:
    # Use proxy in your scripts
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    # Make requests through proxy...
```

## 🔒 Security & OPSEC

### Operational Security
- **VPN Recommended**: Use VPN when hunting proxies
- **Rate Limiting**: Built-in delays to avoid detection
- **Randomization**: Randomized testing patterns
- **Stealth Mode**: Minimal fingerprinting

### Legal Considerations
- **Authorization Required**: Only use on networks you own or have permission to test
- **Compliance**: Follow local laws and regulations
- **Documentation**: Maintain proper testing documentation
- **Responsible Disclosure**: Report vulnerabilities appropriately

## 📊 Performance Metrics

### Tested Environments
- **Samsung Galaxy A06**: Excellent performance
- **OnePlus devices**: Optimal performance
- **Budget Android devices**: Good performance with reduced thread count

### Resource Usage
- **RAM**: ~50MB typical usage
- **CPU**: Low impact with threading optimization
- **Network**: Minimal bandwidth usage
- **Battery**: Efficient power consumption

## 🐛 Troubleshooting

### Common Issues

**Termux Permission Issues**
```bash
termux-setup-storage
pkg update && pkg upgrade
```

**Python Module Errors**
```bash
pip install --upgrade pip
pip install --force-reinstall requests flask
```

**Network Connectivity**
```bash
# Test connectivity
ping -c 4 8.8.8.8

# Reset Termux
termux-reload-settings
```

### Performance Optimization

**Low-End Devices**
```bash
export MAX_WORKERS=5
export MAX_PROXIES=50
```

**High-End Devices**
```bash
export MAX_WORKERS=50
export MAX_PROXIES=1000
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/redteamabel/mobile-proxy-hunter.git
cd mobile-proxy-hunter
pip install -r requirements.txt
python3 mobile_proxy_hunter.py --dev
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for authorized penetration testing and security research only. Users are responsible for ensuring they have proper authorization before testing any networks. The authors are not responsible for any misuse of this tool.

## 🔗 Links

- **GitHub**: https://github.com/redteamabel/mobile-proxy-hunter
- **Documentation**: https://redteamabel.github.io/mobile-proxy-hunter
- **Issues**: https://github.com/redteamabel/mobile-proxy-hunter/issues
- **Telegram**: @RedTeamAbel
- **Discord**: RedTeamAbel#1337

---

**🔥 Built with ❤️ by RedTeamAbel for the Red Team Community 🔥**

*"Because sometimes the best red team operations happen from a phone in a coffee shop."*

