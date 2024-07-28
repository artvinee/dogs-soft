import asyncio
import random
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import unquote

import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from loguru import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName

from data import config


class Dog:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        self.query = None
        self.full_query = None
        self.ref_code = None

        self.acc_ref_code = None
        self.id = None
        self.name = None
        self.wallet = None

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        await self.login()

        await asyncio.sleep(0.1)
        age, balance = await self.join()
        await asyncio.sleep(0.1)

        referrals = await self.frens()
        await asyncio.sleep(0.1)
        await self.leaderboard()
        await asyncio.sleep(0.1)
        await self.rewards()
        await asyncio.sleep(0.1)
        await self.tasks()
        await asyncio.sleep(0.1)

        if self.acc_ref_code is not None:
            referral_link = f'https://t.me/dogshouse_bot/join?startapp={self.acc_ref_code}'
        else:
            logger.error(f"Thread {self.thread} | {self.account} | User_id is None")
            referral_link = None

        if self.wallet != '':
            wallet = 'True'
        else:
            wallet = 'False'

        await asyncio.sleep(random.uniform(2, 6))

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, balance, age, referral_link, referrals, wallet, proxy]

    async def join(self):
        try:
            data = self.query
            resp = await self.session.post(f'https://api.onetime.dog/join?invite_hash={self.ref_code}',
                                           data=data)
            if resp.status == 200:
                r = await resp.json()
                age = r['age']
                balance = r['balance']
                self.acc_ref_code = r['reference']
                self.id = r['telegram_id']
                self.wallet = r['wallet']
                return age, balance
            else:
                return None, None
        except Exception as e:
            logger.error(f"Join: {e}")

    async def verify(self, task):
        try:
            resp = await self.session.post(f'https://api.onetime.dog/tasks/verify?task={task}&user_id={self.id}&reference={self.acc_ref_code}')
            if resp.status == 200:
                r = await resp.json()
                return r['success']
            else:
                return False
        except Exception as e:
            logger.error(f"Verify: {e}")

    async def tasks(self):
        try:
            resp = await self.session.get(f'https://api.onetime.dog/tasks?user_id={self.id}&reference={self.acc_ref_code}')
            if resp.status == 200:
                r = await resp.json()
                return r
            else:
                return False
        except Exception as e:
            logger.error(f"Tasks: {e}")

    async def frens(self):
        try:
            data = f"user_id={self.id}&reference={self.acc_ref_code}"
            resp = await self.session.get(f'https://api.onetime.dog/frens?{data}')
            if resp.status == 200:
                r = await resp.json()
                count = int(r['count'])
                return count
            else:
                return False
        except Exception as e:
            logger.error(f"Join: {e}")

    async def leaderboard(self):
        try:
            data = f"user_id={self.id}"
            resp = await self.session.get(f'https://api.onetime.dog/leaderboard?{data}')
            if resp.status == 200:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Join: {e}")

    async def rewards(self):
        try:
            data = f"user_id={self.id}"
            resp = await self.session.get(f'https://api.onetime.dog/rewards?{data}')
            if resp.status == 200:
                r = await resp.json()
                return r['total']
            else:
                return False
        except Exception as e:
            logger.error(f"Join: {e}")

    async def logout(self):
        await self.session.close()

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        self.query, self.full_query = await self.get_tg_web_data()
        await asyncio.sleep(7)
        if self.query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None
        else:
            return True

    async def change_name_with_emoji(self):
        try:
            await self.client.connect()
            me = await self.client.get_me()
            self.name = me.first_name
            if "🦴" in self.name:
                await self.client.disconnect()
                return True, self.name
            new_name = self.name + " 🦴"
            await self.client.update_profile(first_name=new_name)
            await self.client.disconnect()
            return True, new_name
        except Exception as e:
            logger.error(e)
            return False, None

    async def revert_name(self):
        try:
            await self.client.connect()
            me = await self.client.get_me()

            current_name = me.first_name

            new_name = re.sub(r'🦴', '', current_name).strip()

            await self.client.update_profile(first_name=new_name)
            await self.client.disconnect()
            return True, new_name
        except Exception as e:
            logger.error(e)

    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            try:
                await self.client.join_chat('dogs_community')
            except:
                pass
            try:
                await self.client.join_chat('blumcrypto')
            except:
                pass
            try:
                await self.client.join_chat('notcoin')
            except:
                pass
            ref_code = config.REF_CODE
            self.ref_code = ref_code

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('dogshouse_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('dogshouse_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param=ref_code
            ))

            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            full_query = unquote(auth_url)
            return query, full_query

        except Exception as e:
            logger.error(f"Tg Data: {e}")
            return None

    @staticmethod
    def trim_microseconds(iso_time):
        return re.sub(r'\.\d+(?=[+-Z])', '', iso_time)
