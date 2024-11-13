import aiohttp
import asyncio
import json
import uuid
import time
from loguru import logger
import requests
from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

# Display ASCII banner and credits
def display_banner():
    banner = """
     █████╗ ██╗██████╗ ██████╗ ██████╗  ██████╗ ██████╗ 
    ██╔══██╗██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
    ███████║██║██████╔╝██║  ██║██████╔╝██║   ██║██████╔╝
    ██╔══██║██║██╔══██╗██║  ██║██╔══██╗██║   ██║██╔═══╝ 
    ██║  ██║██║██║  ██║██████╔╝██║  ██║╚██████╔╝██║     
    ╚═╝  ╚═╝╚═╝╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     

    ██╗███╗   ██╗███████╗██╗██████╗ ███████╗██████╗     
    ██║████╗  ██║██╔════╝██║██╔══██╗██╔════╝██╔══██╗    
    ██║██╔██╗ ██║███████╗██║██║  ██║█████╗  ██████╔╝    
    ██║██║╚██╗██║╚════██║██║██║  ██║██╔══╝  ██╔══██╗    
    ██║██║ ╚████║███████║██║██████╔╝███████╗██║  ██║    
    ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝   
    """
    credits = "Join Our Channel - https://t.me/AirdropInsiderID"
    credits2 = "AirdropInsiderID | © 2024"
    print(banner)
    print(credits)
    print(credits2)
    print("\n" + "="*60 + "\n")

# Call the display_banner function at the start
display_banner()

# Function to read proxies from the local file
def load_proxies(file_path='proxies.txt'):
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        return proxies
    except FileNotFoundError:
        logger.warning("Proxy file not found.")
        return []

# Function to load token from data.txt
def load_token(file_path='data.txt'):
    with open(file_path, 'r') as f:
        return f.read().strip()

# Function to get the UID using the provided token
def get_uid(token):
    url = "https://api.aigaea.net/api/auth/session"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://app.aigaea.net",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(url, headers=headers)
        response_data = response.json()
        logger.info(f"Session response: {response_data}")
        uid = response_data.get('data', {}).get('uid')
        if not uid:
            logger.error("Failed to retrieve UID. Check your token.")
        return uid
    except Exception as e:
        logger.error(f"Error while retrieving UID: {str(e)}")
        return None

# Function to connect to the API with or without a proxy
async def connect_to_http(uid, token, device_id, proxy=None):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    logger.info(f"Using proxy: {proxy if proxy else 'No proxy'}")

    async with aiohttp.ClientSession(
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": random_user_agent, "Connection": "keep-alive"},
        timeout=ClientTimeout(total=None, connect=10),
    ) as session:
        try:
            uri = "https://api.aigaea.net/api/network/ping"
            logger.info(f"Browser Id : {device_id}")
            logger.info(f"Connecting to {uri} using proxy: {proxy if proxy else 'No proxy'}...")

            # Data to send in the POST request
            data = {
                "uid": uid,
                "browser_id": device_id,
                "timestamp": int(time.time()),
                "version": "1.0.0",
            }
            logger.info(f"Data being sent: {data}")

            # Conditionally add proxy to request
            async with session.post(uri, json=data, proxy=proxy if proxy else None) as response:
                response_data = await response.json()
                logger.info(f"Response Status: {response.status}")
                logger.info(f"Response Content: {response_data}")

                if response.status == 401:
                    logger.error("Authorization failed. Check your token or UID.")
                elif response.status != 200:
                    logger.error(f"Request failed with status {response.status}")
                else:
                    # Successful response, check the points
                    await get_earn_points(session, token, proxy)

        except Exception as e:
            logger.error(f"Error using proxy {proxy}: {str(e)}")

# Function to run all proxies or without proxy concurrently
async def run_all_proxies(uid, token, proxy_device_map):
    tasks = []
    for proxy, device_id in proxy_device_map.items():
        task = asyncio.create_task(connect_to_http(uid, token, device_id, proxy if proxy else None))
        tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Function to loop through proxies continuously
async def loop_proxies(uid, token, proxies, base_browser_id, delays, loop_count=None):
    # Create a fixed mapping of proxies to unique device IDs, or set to None if no proxies available
    proxy_device_map = {proxy if proxies else None: f"{base_browser_id}-{uuid.uuid4().hex[:16]}" for proxy in proxies or [None]}

    count = 0
    while True:
        logger.info(f"Starting loop {count + 1}...")
        await run_all_proxies(uid, token, proxy_device_map)

        logger.info(f"Cycle {count + 1} completed. Waiting before next cycle in {delays} seconds...")
        await asyncio.sleep(delays)  # Delay between cycles (in seconds)

        count += 1
        if loop_count and count >= loop_count:
            logger.info(f"Completed {loop_count} loops. Exiting.")
            break

# For testing the function
async def main():
    # Prompt the user for the browser ID
    base_browser_id = input("Please enter your browser ID: ")

    delays = int(input('Input Delay Second Per Looping: '))
    tokenid = load_token()  # Load token from data.txt
    proxies = load_proxies()  # Load proxies from the local file

    uid = get_uid(tokenid)
    if not uid:
        logger.error("Unable to proceed without a valid UID.")
        return

    loop_count = None  # Set a specific number of loops, or None for infinite looping
    await loop_proxies(uid, tokenid, proxies, base_browser_id, delays, loop_count)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
