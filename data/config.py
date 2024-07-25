# api id, hash
API_ID = 1488
API_HASH = 'abcde1488'


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

REF_CODE = "4Tw4x9U9R1CxClURchOaxQ"

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = "Dogs soft by https://t.me/artvinee, based on https://t.me/ApeCryptorSoft 's soft"
