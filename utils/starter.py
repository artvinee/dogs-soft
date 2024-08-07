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
    global frens
    try:
        for attempt in range(max_retries + 1):
            age, balance = await dog.join()
            if age is not None and balance is not None:
                logger.success(f"Thread {thread} | {account} | Balance: {balance} points. Account is {age} years old.")
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
            if frens is not False:
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
        tasks = await dog.tasks()
        black = config.TASKS_BLACKLIST
        if tasks:
            for task in tasks:
                name = task['slug']
                if name not in black:
                    reward = task['reward']
                    completed = task['complete']
                    for attempt in range(1, max_retries + 1):
                        try:
                            if completed is False:
                                if name == 'invite-frens':
                                    if frens >= 5:
                                        verify = await dog.verify(name)
                                        if verify is True:
                                            logger.success(
                                                f"Thread {thread} | {account} | Task {name} was successfully completed. +{reward} points!")
                                            break
                                        else:
                                            if attempt < max_retries:
                                                logger.error(f"Thread {thread} | {account} | Task {name} was failed. Try again..")
                                                await asyncio.sleep(
                                                    random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                                                continue
                                            else:
                                                logger.error(
                                                    f"Thread {thread} | {account} | Task {name} was finally failed.")
                                                break
                                    else:
                                        break
                                elif name == "add-bone-telegram":
                                    status, new_name = await dog.change_name_with_emoji()
                                    await asyncio.sleep(random.uniform(1.5, 2.5))
                                    if status is True:
                                        logger.success(
                                            f"Thread {thread} | {account} | Name was successfully chamged to {new_name}.")
                                        await asyncio.sleep(random.uniform(1.5, 2.5))
                                        verify = await dog.verify(name)
                                        if verify is True:
                                            logger.success(
                                                f"Thread {thread} | {account} | Task {name} was successfully completed. +{reward} points!")
                                            await asyncio.sleep(random.uniform(1.5, 2.5))
                                            if config.REMOVE_BONE_AFTER_COMPLETE is True:
                                                status, old_name = await dog.revert_name()
                                                if status is True:
                                                    logger.success(
                                                        f"Thread {thread} | {account} | Name was successfully changed to {old_name}.")
                                                    break
                                            break
                                        else:
                                            if attempt < max_retries:
                                                logger.error(f"Thread {thread} | {account} | Task {name} was failed. Try again..")
                                                await asyncio.sleep(
                                                    random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                                                continue
                                            else:
                                                logger.error(
                                                    f"Thread {thread} | {account} | Task {name} was finally failed.")
                                                break
                                else:
                                    verify = await dog.verify(name)
                                    if verify is True:
                                        logger.success(
                                            f"Thread {thread} | {account} | Task {name} was successfully completed. +{reward} points!")
                                        break
                                    else:
                                        if attempt < max_retries:
                                            logger.error(f"Thread {thread} | {account} | Task {name} was failed. Try again..")
                                            await asyncio.sleep(
                                                random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                                            continue
                                        else:
                                            logger.error(f"Thread {thread} | {account} | Task {name} was finally failed.")
                                            break
                        except Exception as e:
                            logger.error(f"Thread {thread} | {account} | {e}")
                            await dog.revert_name()
                await asyncio.sleep(random.uniform(0.5, 1.2))
        else:
            logger.error(f"Thread {thread} | {account} | Failed to get tasks.")
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
    columns = ['Phone number', 'Name', 'Balance', 'Age', 'Referral link', 'Referrals', 'Wallet', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")


async def inf_stats():
    while True:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(
                Dog(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

        data = await asyncio.gather(*tasks)

        path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        columns = ['Phone number', 'Name', 'Balance', 'Age', 'Referral link', 'Referrals', 'Wallet', 'Proxy (login:password@ip:port)']

        if not os.path.exists('statistics'): os.mkdir('statistics')
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(path, index=False, encoding='utf-8-sig')

        logger.success(f"Saved statistics to {path}")
        sleep = 60 * 60 * 24 + random.randint(100, 450)
        logger.info(f"Sleep {sleep} seconds..")
        await asyncio.sleep(sleep)
