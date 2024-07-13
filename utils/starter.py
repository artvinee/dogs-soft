import os
import random

from utils.dog import Dog
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio

max_retries = config.DELAYS['MAX_ATTEMPTS']


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    dog = Dog(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await dog.login():
        logger.success(f"Thread {thread} | {account} | Login")
        await task(dog, thread, account)
    else:
        logger.error(f"Thread {thread} | {account} | Failed to login")
        await dog.logout()


async def task(dog, thread, account):
    try:
        for attempt in range(max_retries + 1):
            age, balance = await dog.join()
            if age is not None and balance is not None:
                logger.success(f"Thread {thread} | {account} | Successfully claimed {balance} tokens. Account is {age} years old.")
                break
            else:
                logger.error(f"Thread {thread} | {account} | Failed to check allocation.")
                if attempt < max_retries + 1:
                    await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                    continue
                else:
                    break
        for attempt in range(max_retries + 1):
            frens = await dog.frens()
            if frens is True:
                break
            else:
                if attempt < max_retries + 1:
                    await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                    continue
                else:
                    break
        for attempt in range(max_retries + 1):
            leaderboard = await dog.leaderboard()
            if leaderboard is True:
                break
            else:
                if attempt < max_retries + 1:
                    await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                    continue
                else:
                    break
        for attempt in range(max_retries + 1):
            rewards = await dog.rewards()
            if rewards is True:
                break
            else:
                if attempt < max_retries + 1:
                    await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                    continue
                else:
                    break
        await dog.logout()
    except Exception as e:
        logger.error(f"Thread {thread} | {account} | Error: {e}")

async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(
            Dog(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Balance', 'Age', 'Referral link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")