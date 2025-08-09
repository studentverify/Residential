import subprocess
import json

def filter_usa_residential_proxies(input_file, output_file):
    usa_residential_proxies = []
    with open(input_file, 'r') as f_in:
        for line in f_in:
            proxy = line.strip()
            if not proxy:
                continue
            
            ip_address = proxy.split(':')[0]
            
            try:
                # Check country first
                result_country = subprocess.run(
                    ['python3', 'check_proxy_country.py', ip_address],
                    capture_output=True, text=True, check=True
                )
                country_code = result_country.stdout.strip()
                
                if country_code != 'US':
                    print(f"Skipping non-USA proxy: {proxy} (Country: {country_code})")
                    continue

                # If USA, then check IP type
                result_type = subprocess.run(
                    ['python3', 'check_ip_type.py', ip_address],
                    capture_output=True, text=True, check=True
                )
                ip_type_data = json.loads(result_type.stdout.strip())
                
                if ip_type_data.get('is_residential'):
                    usa_residential_proxies.append(proxy)
                    print(f"Found USA residential proxy: {proxy}")
                else:
                    print(f"Skipping non-residential USA proxy: {proxy} (Type: {ip_type_data.get('isp', 'N/A')}/{ip_type_data.get('org', 'N/A')})")

            except subprocess.CalledProcessError as e:
                print(f"Error during subprocess for {ip_address}: {e.stderr}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {ip_address}: {e} - Raw output: {result_type.stdout.strip()}")
            except Exception as e:
                print(f"An unexpected error occurred for {ip_address}: {e}")

    with open(output_file, 'w') as f_out:
        for proxy in usa_residential_proxies:
            f_out.write(proxy + '\n')
    print(f"Filtered USA residential proxies saved to {output_file}")

if __name__ == "__main__":
    filter_usa_residential_proxies('residential_proxies.txt', 'usa_residential_proxies.txt')


