from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_ip', methods=['POST'])
def get_ip():
    data = request.get_json() or {}
    proxy_url = data.get('proxy')
    proxies = {
        "http": f"http://{proxy_url}",
        "https": f"http://{proxy_url}",
    } if proxy_url else None
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=5)
        response.raise_for_status()
        return jsonify(ip=response.json()["ip"])
    except requests.exceptions.RequestException as e:
        return jsonify(ip=f"Error: {e}")

@app.route('/get_proxies')
def get_proxies():
    t        with open(\'usa_residential_proxies.txt\', \'r\') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return jsonify(proxies=proxies)
    except FileNotFoundError:
        return jsonify(proxies=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


