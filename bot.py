import aiohttp
import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# تفعيل مكتبة colorama
init(autoreset=True)

# عرض رسالة الترحيب
welcome_message = f"""
{Fore.YELLOW + Style.BRIGHT}
##########################################
#                                        #
#   Welcome Mokl Farm Script  🔥        #
#                                        #
##########################################
{Fore.CYAN + Style.BRIGHT}
#   Developed by: @Ke4oo                  #
#   Telegram: {Fore.LIGHTBLUE_EX}https://t.me/YOU742         #
##########################################
"""
print(welcome_message)

# دالة لطباعة الرسائل مع التاريخ والوقت
def print_message(message, color=Fore.WHITE):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{current_time}] {message}{Style.RESET_ALL}")

# دالة لقراءة جميع الحسابات من ملف data.txt
def read_accounts(file_path="data.txt"):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print_message(f"Error: File '{file_path}' not found.", Fore.RED)
        return []
async def fetch_id(init_data):
    print_message("Fetching ID...", Fore.YELLOW)

    url = "https://b.mokl.io/api/graphql"
    payload = {
        "variables": {
            "initData": init_data,
            "friendCode": None
        },
         "query": "mutation ($initData: String, $friendCode: String) {\n  initGame(initData: $initData, friendCode: $friendCode) {\n    user {\n      token\n      telegram_id\n      __typename\n    }\n    __typename\n  }\n}"
    }

    headers = {
        'User-Agent': "Mozilla/5.0",
        'Content-Type': "application/json",
        'token': "null"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                user = data.get("data", {}).get("initGame", {}).get("user", {})
                telegram_id = user.get("telegram_id", "Telegram ID not found")
                print_message(f"ID fetched successfully: {telegram_id}", Fore.GREEN)
                return telegram_id
            else:
                print_message(f"Failed to fetch ID. Status code: {response.status}", Fore.RED)
                
# دالة جلب التوكن لحساب معين
async def fetch_token(init_data):
    url = "https://b.mokl.io/api/graphql"
    payload = {
        "variables": {"initData": init_data, "friendCode": None},
        "query": """mutation ($initData: String, $friendCode: String) {
                      initGame(initData: $initData, friendCode: $friendCode) {
                        user { token telegram_id __typename }
                        __typename
                      }
                    }"""
    }
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Content-Type': "application/json",
        'token': "null"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("data", {}).get("initGame", {}).get("user", {}).get("token", "Token not found")
                print_message(f"Token fetched successfully: {token}", Fore.GREEN)
                return token
            else:
                print_message(f"Failed to fetch token. Status code: {response.status}", Fore.RED)
                return None
async def fetch_and_save_ids(token):
    url = "https://b.mokl.io/api/graphql"
    payload = {
        "operationName": "getTasks",
        "variables": {},
        "query": """mutation getTasks {
            loadTasks {
                tasks {
                    type
                    list {
                        id
                        type
                        title
                        reward
                        info {
                            type
                            link
                            amount
                            count
                            sum
                            end_timer
                            __typename
                        }
                        claim
                        period
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }"""
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'sec-ch-ua-mobile': "?1",
        'token': f"{token}",
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://farm.mokl.io",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://farm.mokl.io/",
        'accept-language': "en-US,en;q=0.9"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # استخراج جميع قيم الـ id من TasksListItem
                    ids = []
                    tasks = data.get("data", {}).get("loadTasks", {}).get("tasks", [])
                    for task in tasks:
                        for item in task.get("list", []):
                            if "id" in item:  # تأكد أن الحقل موجود
                                ids.append(item["id"])

                    # حفظ الـ ids في ملف quest.txt
                    with open("quest.txt", "w") as file:
                        for id in ids:
                            file.write(f"{id}\n")

                    print_message(f"Successfully extracted and saved {len(ids)} IDs.", Fore.YELLOW)                   
                else:
                    print_message(f"Request failed with status code: {response.status}")
        except Exception as e:
            print_message(f"An error occurred: {e}")



async def claim_task(token):
    url = "https://b.mokl.io/api/graphql"
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
        'sec-ch-ua-mobile': "?1",
        'token': f"{token}",
        'sec-ch-ua-platform': "\"Android\"",
        'origin': "https://farm.mokl.io",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://farm.mokl.io/",
        'accept-language': "en-US,en;q=0.9"
    }

    try:
        # قراءة القيم من الملف الخارجي
        with open("quest.txt", "r") as file:
            task_ids = [line.strip() for line in file if line.strip()]

        async with aiohttp.ClientSession() as session:
            for task_id in task_ids:
                payload = {
                    "variables": {
                        "tasks_id": int(task_id)
                    },
                    "query": """mutation ($tasks_id: ID) {
                        claimTasks(tasks_id: $tasks_id) {
                            amount
                            tonomo
                            __typename
                        }
                    }"""
                }

                try:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            print_message(f"Task ID: {task_id} | Done",Fore.BLUE)
                        else:
                            print_message(f"Task ID: {task_id} | Request failed with status code: {response.status}",Fore.RED)
                except Exception as e:
                    print_message(f"Task ID: {task_id} | An error occurred: {e}",Fore.RED)

                # تأخير لتجنب الحظر
                time.sleep(5)  # تعديل وقت التأخير حسب الحاجة

    except FileNotFoundError:
        print("The file 'quest.txt' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# دالة تنفيذ الطلبات لكل حساب
async def process_account(init_data):
    print_message(f"Processing account: {init_data}", Fore.CYAN)

    token = await fetch_token(init_data)
    if not token:
        print_message(f"Skipping account {init_data} due to missing token.", Fore.RED)
        return
    await fetch_and_save_ids(token)
    await claim_task(token)
    await claim_free_donation(token)
    await claming_farm(token)
    await start_farming(token)
    await fetch_data(init_data)
    print_message(f"Finished processing account: {init_data}", Fore.MAGENTA)

# دالة إرسال طلب التبرع المجاني
async def claim_free_donation(token):
    url = "https://b.mokl.io/api/graphql"
    payload = {
        "variables": {
            "donation_id": 1
        },
        "query": "mutation ($donation_id: Int) {\n  claimFreeDonation(donation_id: $donation_id) {\n    balance {\n      tonomo\n      vTono\n      __typename\n    }\n    __typename\n  }\n}"
    }
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Content-Type': "application/json",
        'token': token
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                print_message("Free donation claimed successfully ✅", Fore.YELLOW)
            else:
                print_message("Failed to claim donation, try again later.", Fore.RED)

# دالة إرسال طلب حصاد الفارم
async def claming_farm(token):
    url = "https://b.mokl.io/api/graphql"
    payload = {
        "variables": {},
        "query": (
            "mutation ($is_vtono_boost: Boolean, $ton_transaction_unique_boost: String) {\n"
            "  claimFarming(\n"
            "    is_vtono_boost: $is_vtono_boost\n"
            "    ton_transaction_unique_boost: $ton_transaction_unique_boost\n"
            "  ) {\n"
            "    total_amount\n"
            "    league {\n"
            "      place\n"
            "      type\n"
            "      __typename\n"
            "    }\n"
            "    current_balance {\n"
            "      tonomo\n"
            "      vTono\n"
            "      __typename\n"
            "    }\n"
            "    __typename\n"
            "  }\n"
            "}"
        )
    }
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Content-Type': "application/json",
        'token': token
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                print_message("Farming claim successful ✅", Fore.GREEN)
            else:
                print_message("Farming claim failed.", Fore.RED)

# دالة بدء الزراعة
async def start_farming(token):
    url = "https://b.mokl.io/api/graphql"
    payload = {
  "variables": {},
  "query": "mutation ($is_vtono_boost: Boolean, $ton_transaction_unique_boost: String) {\n  startFarming(\n    is_vtono_boost: $is_vtono_boost\n    ton_transaction_unique_boost: $ton_transaction_unique_boost\n  ) {\n    unique\n    wait_time\n    end_timer\n    earn_per_second\n    current_balance {\n      tonomo\n      vTono\n      __typename\n    }\n    __typename\n  }\n}"
}
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Content-Type': "application/json",
        'token': token
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                print_message("Farming started successfully ✅", Fore.CYAN)
            else:
                print_message("Failed to start farming.", Fore.RED)

# دالة مشاهدة الإعلانات
async def fetch_data(init_data):
    token = await fetch_token(init_data)
    url = "https://b.mokl.io//api/adsgram"
    headers = {
        'User-Agent': "Mozilla/5.0",
        'origin': "https://farm.mokl.io",
        'referer': "https://farm.mokl.io/",
        'accept-language': "en-US,en;q=0.9"
    }
    

    async with aiohttp.ClientSession() as session:
        for i in range(10):
            print_message(f"Watching Ad #{i + 1}...", Fore.YELLOW)
            user_id = await fetch_id(init_data)
            params = {
                'userId': f"{user_id}",
                'secret': "6350"
            }
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    print_message(f"Ad #{i + 1} completed successfully ✅", Fore.GREEN)
                else:
                    print_message(f"Failed to watch Ad #{i + 1}.", Fore.RED)
            await asyncio.sleep(5)

# دالة إدارة جميع الحسابات والانتظار 24 ساعة
async def main():
    while True:
        print_message("Starting processing for all accounts...", Fore.MAGENTA)
        
        accounts = read_accounts()
        if not accounts:
            print_message("No accounts found in data.txt!", Fore.RED)
            return

        for account in accounts:
            await process_account(account)
            await asyncio.sleep(5)  # تأخير بين الحسابات لمنع الحظر
        
        print_message("All accounts processed. Waiting 24 hours before restarting...", Fore.YELLOW)
        await asyncio.sleep(86400)  # انتظار 24 ساعة (86400 ثانية)

# تشغيل البرنامج
if __name__ == "__main__":
    asyncio.run(main())