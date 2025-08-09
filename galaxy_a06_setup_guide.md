# 🔥 RedTeamAbel's Galaxy A06 Proxy Hunter Setup Guide

**The Ultimate Newbie-Friendly Guide for Samsung Galaxy A06**

## 📱 What You'll Need

- Samsung Galaxy A06 (or any Android device)
- Stable internet connection (WiFi or mobile data)
- 30 minutes of your time
- Basic reading skills (that's it!)

## 🚀 Step-by-Step Installation (Foolproof)

### Step 1: Install Termux (The Right Way)

⚠️ **CRITICAL**: Do NOT install Termux from Google Play Store! It's outdated and broken.

1. **Download F-Droid**:
   - Open Chrome/Firefox on your Galaxy A06
   - Go to: `https://f-droid.org`
   - Tap "Download F-Droid"
   - Install the APK (allow "Install from unknown sources" if prompted)

2. **Install Termux from F-Droid**:
   - Open F-Droid app
   - Search for "Termux"
   - Install "Termux" (NOT Termux from Google Play)
   - Also install "Termux:API" while you're at it

### Step 2: Basic Termux Setup

1. **Open Termux** (black terminal app)
2. **Copy and paste this command** (tap and hold to paste):
```bash
pkg update && pkg upgrade -y
```
3. **Wait for it to finish** (might take 5-10 minutes)
4. **Grant storage permission**:
```bash
termux-setup-storage
```
5. **Tap "Allow" when prompted**

### Step 3: Install Required Packages

**Copy and paste each line one by one:**

```bash
pkg install -y python python-pip git curl wget nodejs npm
```

```bash
pip install requests flask gunicorn
```

### Step 4: Download the Proxy Hunter

```bash
cd ~
curl -O https://raw.githubusercontent.com/redteamabel/mobile-proxy-hunter/main/enhanced_mobile_proxy_hunter.py
```

```bash
curl -O https://raw.githubusercontent.com/redteamabel/mobile-proxy-hunter/main/templates/enhanced_mobile.html
```

```bash
mkdir -p templates
mv enhanced_mobile.html templates/
```

### Step 5: Launch the Proxy Hunter

```bash
python enhanced_mobile_proxy_hunter.py
```

**You should see:**
```
🔥 RedTeamAbel's Enhanced Mobile Proxy Hunter Starting...
🚀 Optimized for Samsung Galaxy A06
📱 Mobile ISP Priority Mode Enabled
🔄 Auto-Rotation Every 5 Minutes
🌐 Access at: http://localhost:8080
```

### Step 6: Access the Web Interface

1. **Open Chrome or Firefox** on your Galaxy A06
2. **Go to**: `http://localhost:8080`
3. **You should see the green interface!**

## 🎯 How to Use (Super Simple)

### First Time Setup

1. **Tap "🔍 Hunt Proxies"** - This finds fresh proxies
2. **Wait 30 seconds** - Let it collect proxies
3. **Tap "⚡ Deep Test"** - This tests all proxies thoroughly
4. **Wait 2-3 minutes** - Let it test everything
5. **Tap "📋 Load Verified"** - This loads your working proxies

### Daily Usage

1. **Select a proxy** from the dropdown
2. **Tap "🥷 Execute Stealth Test"** - Test individual proxy
3. **Use "🔄 Auto-Rotate Proxy"** - Get a new proxy automatically

### Auto-Rotation Feature

- **Automatic**: Proxies rotate every 5 minutes
- **Manual**: Tap the blue "🔄 Auto-Rotate Proxy" button
- **Priority**: Mobile ISPs first, then residential

## 🌐 Using Proxies in Chrome/Firefox

### Method 1: Browser Extensions (Easiest)

**For Chrome:**
1. Install "Proxy SwitchyOmega" extension
2. Add your proxy: `IP:PORT` from the app
3. Set to HTTP proxy
4. Enable the proxy profile

**For Firefox:**
1. Go to Settings → Network Settings
2. Select "Manual proxy configuration"
3. Enter HTTP Proxy: `IP` and Port: `PORT`
4. Check "Use this proxy server for all protocols"

### Method 2: Android System Proxy

1. **Go to WiFi Settings**
2. **Long press your WiFi network**
3. **Tap "Modify network"**
4. **Tap "Advanced options"**
5. **Set Proxy to "Manual"**
6. **Enter proxy details from the app**

## 🔧 Troubleshooting (Common Issues)

### "Permission Denied" Error
```bash
termux-setup-storage
chmod +x enhanced_mobile_proxy_hunter.py
```

### "Module Not Found" Error
```bash
pip install --upgrade pip
pip install requests flask gunicorn
```

### "No Proxies Found"
- Check your internet connection
- Try running the hunt again
- Some proxy sources might be down

### App Won't Start
```bash
pkill python
python enhanced_mobile_proxy_hunter.py
```

### Browser Can't Connect
- Make sure the app is running
- Try `http://127.0.0.1:8080` instead
- Restart the app

## 📱 Galaxy A06 Specific Optimizations

### Performance Settings
```bash
# For better performance on Galaxy A06
export MAX_WORKERS=8
export MAX_PROXIES=100
```

### Battery Optimization
1. **Go to Settings → Battery**
2. **Find Termux in app list**
3. **Disable battery optimization for Termux**

### Keep Screen On (Optional)
```bash
# In Termux, run this to keep screen on
termux-wake-lock
```

## 🎯 Advanced Usage

### Command Line Options
```bash
# Hunt only
python enhanced_mobile_proxy_hunter.py --hunt-only

# Test specific proxy
python enhanced_mobile_proxy_hunter.py --test 192.168.1.1:8080

# Export working proxies
python enhanced_mobile_proxy_hunter.py --export
```

### Custom Proxy Lists
```bash
# Add your own proxy list
echo "192.168.1.1:8080" >> custom_proxies.txt
python enhanced_mobile_proxy_hunter.py --import custom_proxies.txt
```

## 🔒 Security & Privacy

### Using with VPN
1. **Connect to VPN first**
2. **Then run proxy hunter**
3. **This adds extra anonymity**

### Clearing Traces
```bash
# Clear proxy database
rm proxy_hunter.db

# Clear logs
rm *.log
```

## 🚀 One-Liner Quick Start

**For the impatient (copy and paste everything at once):**

```bash
pkg update -y && pkg install -y python python-pip curl && pip install requests flask gunicorn && cd ~ && curl -O https://raw.githubusercontent.com/redteamabel/mobile-proxy-hunter/main/enhanced_mobile_proxy_hunter.py && mkdir -p templates && curl -o templates/enhanced_mobile.html https://raw.githubusercontent.com/redteamabel/mobile-proxy-hunter/main/templates/enhanced_mobile.html && python enhanced_mobile_proxy_hunter.py
```

## 📋 Replication Steps for Prosperity

### For Other Devices

**Any Android Device:**
1. Follow the same Termux installation
2. Adjust `MAX_WORKERS` based on device performance
3. Use the same commands

**Different Android Versions:**
- Android 7+: Full compatibility
- Android 6: May need additional permissions
- Android 5: Limited functionality

### For Team Distribution

**Create a setup script:**
```bash
#!/bin/bash
echo "🔥 RedTeamAbel Auto-Setup"
pkg update -y
pkg install -y python python-pip curl git
pip install requests flask gunicorn
cd ~
git clone https://github.com/redteamabel/mobile-proxy-hunter.git
cd mobile-proxy-hunter
python enhanced_mobile_proxy_hunter.py
```

**Share with team:**
```bash
curl -sSL https://your-server.com/setup.sh | bash
```

## 🎯 Success Indicators

**You know it's working when:**
- ✅ Green interface loads in browser
- ✅ "Current IP" shows your real IP
- ✅ "Hunt Proxies" finds 1000+ proxies
- ✅ "Deep Test" finds 10+ verified proxies
- ✅ "Stealth Test" shows proxy details
- ✅ Auto-rotation timer counts down

## 🆘 Emergency Recovery

**If everything breaks:**
```bash
# Nuclear option - start fresh
rm -rf ~/mobile-proxy-hunter
pkg uninstall python
pkg install python python-pip
# Then start from Step 3
```

## 📞 Support

**If you're still stuck:**
- Check the GitHub issues
- Join the Telegram group
- Ask on Discord
- Email support

**Remember**: This tool is for authorized testing only!

---

**🔥 You're now ready to run red team ops from your Galaxy A06! 🔥**

*"Because the best hacks happen from the most unexpected places."*

