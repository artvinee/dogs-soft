# api id, hash
API_ID = 
API_HASH = ''


DELAYS = {
    'ACCOUNT': [1, 2],  # delay between connections to accounts (the more accounts, the longer the delay)
    'REPEAT': [1, 2],
    'MAX_ATTEMPTS': 2
}

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "socks5",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "socks5"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

REMOVE_BONE_AFTER_COMPLETE = True #  remove emoji bone from name after complete task
REF_CODE = "4Tw4x9U9R1CxClURchOaxQ"
TASKS_BLACKLIST = [   #  do not change, i'll let you know if i need to make any changes.
            "make-transaction",
            "send-bone"
        ]

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 60

SOFT_INFO = "Dogs soft by https://t.me/artvinee, based on https://t.me/ApeCryptorSoft 's soft"
