#!/data/data/com.termux/files/usr/bin/bash

# Termux Residential Proxy Hunter Setup Script
# For Android Red Team Operations

echo "🔥 REDTEAMABEL'S TERMUX PROXY HUNTER SETUP 🔥"
echo "Setting up the ultimate mobile red team toolkit..."

# Update packages
echo "📦 Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install essential packages
echo "🛠️ Installing essential packages..."
pkg install -y python python-pip git curl wget nodejs npm termux-api

# Install Python packages
echo "🐍 Installing Python packages..."
pip install requests flask gunicorn

# Create project directory
echo "📁 Creating project structure..."
mkdir -p ~/redteam-proxy-hunter
cd ~/redteam-proxy-hunter

# Download proxy lists
echo "🎯 Fetching fresh proxy lists..."
curl -s "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt" > raw_proxies.txt

# Create mobile-optimized HTML interface
cat > templates/mobile.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 RedTeamAbel Mobile Proxy Hunter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #00ff00; 
            min-height: 100vh;
            padding: 10px;
        }
        .container { 
            max-width: 100%; 
            margin: 0 auto; 
            background: rgba(0,0,0,0.8); 
            border-radius: 10px; 
            padding: 15px;
            border: 2px solid #00ff00;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
        }
        .header { 
            text-align: center; 
            margin-bottom: 20px; 
            border-bottom: 2px solid #00ff00;
            padding-bottom: 15px;
        }
        .header h1 { 
            color: #ff6b6b; 
            text-shadow: 0 0 10px #ff6b6b;
            font-size: 1.5em;
        }
        .status { 
            background: rgba(0,255,0,0.1); 
            padding: 10px; 
            border-radius: 5px; 
            margin: 10px 0;
            border-left: 4px solid #00ff00;
        }
        .proxy-section { 
            margin: 15px 0; 
            padding: 15px; 
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        select, button, input { 
            width: 100%; 
            padding: 12px; 
            margin: 8px 0; 
            border: 2px solid #00ff00; 
            background: rgba(0,0,0,0.7); 
            color: #00ff00; 
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        button { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white; 
            cursor: pointer; 
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255,107,107,0.4);
        }
        .result { 
            background: rgba(0,0,0,0.9); 
            padding: 15px; 
            border-radius: 5px; 
            margin: 10px 0;
            border: 1px solid #333;
            word-break: break-all;
        }
        .success { color: #00ff00; }
        .error { color: #ff6b6b; }
        .warning { color: #ffa502; }
        .loading { 
            color: #3742fa; 
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .stats { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 10px; 
            margin: 15px 0;
        }
        .stat-box { 
            background: rgba(0,255,0,0.1); 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center;
            border: 1px solid #00ff00;
        }
        .footer { 
            text-align: center; 
            margin-top: 20px; 
            padding-top: 15px; 
            border-top: 1px solid #333;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 RedTeamAbel Mobile Proxy Hunter</h1>
            <p>Ultimate Android Red Team Toolkit</p>
        </div>

        <div class="status">
            <strong>Current IP:</strong> <span id="current-ip" class="loading">Detecting...</span>
        </div>

        <div class="stats">
            <div class="stat-box">
                <div>USA Proxies</div>
                <div id="usa-count">0</div>
            </div>
            <div class="stat-box">
                <div>Residential</div>
                <div id="residential-count">0</div>
            </div>
        </div>

        <div class="proxy-section">
            <h3>🎯 Proxy Hunter Controls</h3>
            <button onclick="huntProxies()">🔍 Hunt Fresh Proxies</button>
            <button onclick="testAllProxies()">⚡ Test All Proxies</button>
            <button onclick="loadProxies()">📋 Load Proxy List</button>
        </div>

        <div class="proxy-section">
            <h3>🕵️ Stealth Test</h3>
            <select id="proxy-select">
                <option value="">-- Select Proxy --</option>
            </select>
            <button onclick="stealthTest()">🥷 Execute Stealth Test</button>
            <div id="stealth-result" class="result"></div>
        </div>

        <div class="proxy-section">
            <h3>📊 Results</h3>
            <div id="results-area" class="result">
                Ready for red team operations...
            </div>
        </div>

        <div class="footer">
            <p>RedTeamAbel © 2025 | Mobile Red Team Operations</p>
        </div>
    </div>

    <script>
        let proxies = [];
        let usaProxies = [];
        let residentialProxies = [];

        // Get current IP on load
        getCurrentIP();

        async function getCurrentIP() {
            try {
                const response = await fetch('/api/current-ip');
                const data = await response.json();
                document.getElementById('current-ip').innerHTML = `<span class="success">${data.ip}</span>`;
            } catch (error) {
                document.getElementById('current-ip').innerHTML = `<span class="error">Error</span>`;
            }
        }

        async function huntProxies() {
            updateResults('🔍 Hunting for fresh proxies...', 'loading');
            try {
                const response = await fetch('/api/hunt-proxies', { method: 'POST' });
                const data = await response.json();
                updateResults(`🎯 Found ${data.total} proxies, ${data.usa} USA, ${data.residential} residential`, 'success');
                loadProxies();
            } catch (error) {
                updateResults('❌ Proxy hunt failed', 'error');
            }
        }

        async function loadProxies() {
            try {
                const response = await fetch('/api/proxies');
                const data = await response.json();
                proxies = data.proxies;
                
                const select = document.getElementById('proxy-select');
                select.innerHTML = '<option value="">-- Select Proxy --</option>';
                
                proxies.forEach(proxy => {
                    const option = document.createElement('option');
                    option.value = proxy;
                    option.textContent = proxy;
                    select.appendChild(option);
                });

                document.getElementById('usa-count').textContent = data.usa_count || 0;
                document.getElementById('residential-count').textContent = data.residential_count || 0;
                
                updateResults(`📋 Loaded ${proxies.length} proxies`, 'success');
            } catch (error) {
                updateResults('❌ Failed to load proxies', 'error');
            }
        }

        async function stealthTest() {
            const selectedProxy = document.getElementById('proxy-select').value;
            if (!selectedProxy) {
                updateResults('⚠️ Select a proxy first', 'warning');
                return;
            }

            document.getElementById('stealth-result').innerHTML = '<span class="loading">🥷 Executing stealth test...</span>';
            
            try {
                const response = await fetch('/api/stealth-test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ proxy: selectedProxy })
                });
                const data = await response.json();
                
                let resultHtml = `
                    <div class="success">✅ Stealth Test Results:</div>
                    <div>🌍 IP: ${data.ip}</div>
                    <div>🇺🇸 Country: ${data.country}</div>
                    <div>🏠 Type: ${data.is_residential ? 'Residential' : 'Datacenter'}</div>
                    <div>🏢 ISP: ${data.isp}</div>
                    <div>⚡ Response Time: ${data.response_time}ms</div>
                `;
                
                if (data.is_residential && data.country === 'US') {
                    resultHtml += '<div class="success">🎯 PERFECT RESIDENTIAL USA PROXY!</div>';
                }
                
                document.getElementById('stealth-result').innerHTML = resultHtml;
            } catch (error) {
                document.getElementById('stealth-result').innerHTML = '<span class="error">❌ Stealth test failed</span>';
            }
        }

        async function testAllProxies() {
            updateResults('⚡ Testing all proxies...', 'loading');
            try {
                const response = await fetch('/api/test-all', { method: 'POST' });
                const data = await response.json();
                updateResults(`⚡ Tested ${data.tested} proxies, ${data.working} working, ${data.residential} residential USA`, 'success');
                loadProxies();
            } catch (error) {
                updateResults('❌ Bulk test failed', 'error');
            }
        }

        function updateResults(message, type) {
            const resultsArea = document.getElementById('results-area');
            const timestamp = new Date().toLocaleTimeString();
            resultsArea.innerHTML = `<span class="${type}">[${timestamp}] ${message}</span>`;
        }

        // Load proxies on page load
        loadProxies();
    </script>
</body>
</html>
EOF

echo "✅ Setup complete! Your mobile red team toolkit is ready."
echo ""
echo "🚀 To start hunting:"
echo "cd ~/redteam-proxy-hunter"
echo "python3 mobile_proxy_hunter.py"
echo ""
echo "Then open your browser to: http://localhost:8080"

