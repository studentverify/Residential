#!/data/data/com.termux/files/usr/bin/bash

# RedTeamAbel's Auto-Refresh Daemon Stop Script

echo "🛑 Stopping Auto-Refresh Daemon..."

# Kill daemon by PID if exists
if [ -f daemon.pid ]; then
    PID=$(cat daemon.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Daemon stopped (PID: $PID)"
        rm daemon.pid
    else
        echo "⚠️  Daemon not running (stale PID file)"
        rm daemon.pid
    fi
else
    # Fallback: kill by process name
    if pgrep -f "auto_refresh_daemon.py" > /dev/null; then
        pkill -f "auto_refresh_daemon.py"
        echo "✅ Daemon stopped (by process name)"
    else
        echo "ℹ️  Daemon not running"
    fi
fi

echo "🔥 Auto-refresh daemon stopped"

