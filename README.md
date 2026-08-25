# 🌊 DDoS Tool - Advanced Proxy Rotation Edition

[![Version](https://img.shields.io/badge/version-2026.0-red.svg)](https://github.com/dmon56460-oss/ddos-tools)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Advanced Layer 7 DDoS Testing Tool with Automatic Proxy Rotation & IP Spoofing**

---

## ⚠️ IMPORTANT DISCLAIMER

**THIS TOOL IS FOR EDUCATIONAL AND AUTHORIZED SECURITY TESTING PURPOSES ONLY!**

- ❌ **DO NOT** use against any system without explicit written permission
- ❌ **DO NOT** use for illegal or malicious purposes
- ✅ **ONLY** use on systems you own or have permission to test
- ⚖️ The user assumes all responsibility for any misuse

---

## 📌 Features

- 🚀 **Multi-threaded HTTP Flood** - High concurrent request generation
- 🔄 **Automatic Proxy Rotation** - Uses proxies from multiple sources
- 🕵️ **IP Spoofing** - X-Forwarded-For header rotation
- 📱 **Random User-Agent Rotation** - Simulates different browsers/devices
- 🎯 **Custom Port Support** - Target any port
- ⏱️ **Rate Limiting Control** - Adjust requests per second
- ⏰ **Timeout Configuration** - Customizable request timeouts
- 🌐 **Proxy List Fetching** - From 10+ sources
- 📊 **Real-time Statistics** - Success/Failure rates
- 🎨 **Colorful Output** - Beautiful terminal interface

---

## 🚀 Quick Installation

### Clone & Run

```bash
# Clone the repository
git clone https://github.com/dmon56460-oss/ddos-tools.git

# Enter the project directory
cd ddos-tools

# Install required dependencies
pip3 install -r requirements.txt

# Run the tool
python3 ddos-tool.py --url https://example.com
