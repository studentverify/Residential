import subprocess

def filter_usa_proxies(input_file, output_file):
    usa_proxies = []
    with open(input_file, 'r') as f_in:
        for line in f_in:
            proxy = line.strip()
            if not proxy:
                continue
            
            ip_address = proxy.split(':')[0]
            
            try:
                # Call the check_proxy_country.py script as a subprocess
                result = subprocess.run(
                    ['python3', 'check_proxy_country.py', ip_address],
                    capture_output=True, text=True, check=True
                )
                country_code = result.stdout.strip()
                
                if country_code == 'US':
                    usa_proxies.append(proxy)
                    print(f"Found USA proxy: {proxy}")
                else:
                    print(f"Skipping non-USA proxy: {proxy} (Country: {country_code})")
            except subprocess.CalledProcessError as e:
                print(f"Error checking country for {ip_address}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred for {ip_address}: {e}")

    with open(output_file, 'w') as f_out:
        for proxy in usa_proxies:
            f_out.write(proxy + '\n')
    print(f"Filtered USA proxies saved to {output_file}")

if __name__ == "__main__":
    filter_usa_proxies('residential_proxies.txt', 'usa_residential_proxies.txt')


