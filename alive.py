import argparse
import requests
import concurrent.futures
import random
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Random User-Agents to bypass WAF
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/96.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
]


def random_user_agent():
    return random.choice(USER_AGENTS)


def normalize_urls(domain):
    """Ensure correct URL format"""
    domain = domain.replace("http://", "").replace("https://", "").strip("/")
    return [
        f"https://{domain}",
        f"http://{domain}",
        f"https://www.{domain}",
        f"http://www.{domain}",
    ]


def check_alive(domain):
    """Check if domain is alive"""
    headers = {"User-Agent": random_user_agent()}

    for url in normalize_urls(domain):
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
            if response.status_code == 200:
                return url  # Return first working URL
        except requests.RequestException:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description="Check alive domains.")
    parser.add_argument("-u", "--url", help="Check a single URL")
    parser.add_argument("-l", "--list", help="Check a list of URLs from a file")
    parser.add_argument("-s", "--save", help="Save results to a file")

    args = parser.parse_args()

    print(r"""
 _______        _____ _    _ _______
 |_____| |        |    \  /  |______
 |     | |_____ __|__   \/   |______

GitHub - https://github.com/yogsec
Donate ❤️‍🩹 - https://buymeacoffee.com/yogsec
""")

    alive_urls = []

    if args.url:
        result = check_alive(args.url)
        if result:
            print(result)
            alive_urls.append(result)

    if args.list:
        with open(args.list, "r") as file:
            domains = [line.strip() for line in file.readlines()]

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(check_alive, domains)

        for result in results:
            if result:
                print(result)
                alive_urls.append(result)

    if args.save and alive_urls:
        with open(args.save, "w") as f:
            f.write("\n".join(alive_urls))
        print(f"Results saved to: {args.save}")


if __name__ == "__main__":
    main()
