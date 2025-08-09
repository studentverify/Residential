#!/data/data/com.termux/files/usr/bin/bash

# RedTeamAbel's Auto-Refresh Daemon Startup Script
# Keeps your proxy arsenal fresh 24/7

echo "🔥 RedTeamAbel's Auto-Refresh Daemon"
echo "Starting background proxy hunter..."

# Check if daemon is already running
if pgrep -f "auto_refresh_daemon.py" > /dev/null; then
    echo "⚠️  Daemon already running!"
    echo "Use 'pkill -f auto_refresh_daemon.py' to stop it first"
    exit 1
fi

# Install required packages if missing
echo "📦 Checking dependencies..."
pip install requests schedule > /dev/null 2>&1

# Make sure we're in the right directory
cd ~/mobile-proxy-hunter 2>/dev/null || cd ~

# Start the daemon in background
echo "🚀 Starting auto-refresh daemon..."
nohup python3 auto_refresh_daemon.py > daemon.log 2>&1 &

# Get the PID
DAEMON_PID=$!
echo "✅ Daemon started with PID: $DAEMON_PID"

# Save PID for later management
echo $DAEMON_PID > daemon.pid

echo ""
echo "🎯 Daemon Status:"
echo "   - Hunts fresh proxies every hour"
echo "   - Validates existing proxies every 30 minutes"
echo "   - Cleans database every 2 hours"
echo "   - Logs to: daemon.log"
echo ""
echo "📊 Check stats: python3 auto_refresh_daemon.py --stats"
echo "🛑 Stop daemon: ./stop_daemon.sh"
echo "📋 View logs: tail -f daemon.log"
echo ""
echo "🔥 Your proxy arsenal is now self-sustaining!"

