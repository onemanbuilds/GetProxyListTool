from sys import stdout
from os import name,system
from random import choice
from threading import Thread,Lock,active_count
from time import sleep
import json
import requests

colors = {'white': "\033[1;37m", 'green': "\033[0;32m", 'red': "\033[0;31m", 'yellow': "\033[1;33m"}
version = 'v1.0.0'

def clear():
    if name == 'posix':
        system('clear')
    elif name in ('ce', 'nt', 'dos'):
        system('cls')
    else:
        print("\n") * 120

def setTitle(title:str):
    if name == 'posix':
        stdout.write(f"\x1b]2;{title}\x07")
    elif name in ('ce', 'nt', 'dos'):
        system(f'title {title}')
    else:
        stdout.write(f"\x1b]2;{title}\x07")

def printText(lock,bracket_color,text_in_bracket_color,text_in_bracket,text):
    lock.acquire()
    stdout.flush()
    text = text.encode('ascii','replace').decode()
    stdout.write(bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
    lock.release()

def readFile(filename,method):
    with open(filename,method,encoding='utf8') as f:
        content = [line.strip('\n') for line in f]
        return content

def readJson(filename,method):
    with open(filename,method) as f:
        return json.load(f)

def getRandomUserAgent():
    useragents = readFile('[Data]/useragents.txt','r')
    return choice(useragents)

def getRandomProxy(use_proxy,proxy_type):
    proxies_file = readFile('[Data]/proxies.txt','r')
    proxies = {}
    if use_proxy == 1:
        proxy = choice(proxies_file)
        if proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(proxy),
                "https":"https://{0}".format(proxy)
            }
        elif proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(proxy),
                "https":"socks4://{0}".format(proxy)
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(proxy),
                "https":"socks5://{0}".format(proxy)
            }
    else:
        proxies = {
                "http":None,
                "https":None
        }
    return proxies

class Main:
    def __init__(self):
        setTitle(f'[OneManBuilds GetProxyList Tool] ^| {version}')
        clear()
        self.title = colors['white'] + """
                          ╔═════════════════════════════════════════════════════════════════════╗
                                             ╔═╗╔═╗╔╦╗╔═╗╦═╗╔═╗═╗ ╦╦ ╦╦  ╦╔═╗╔╦╗
                                             ║ ╦║╣  ║ ╠═╝╠╦╝║ ║╔╩╦╝╚╦╝║  ║╚═╗ ║ 
                                             ╚═╝╚═╝ ╩ ╩  ╩╚═╚═╝╩ ╚═ ╩ ╩═╝╩╚═╝ ╩ 
                          ╚═════════════════════════════════════════════════════════════════════╝                                         
        """
        print(self.title)
        self.lock = Lock()
        self.hits = 0
        self.retries = 0

        config = readJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads = config['threads']
        self.detailed_hits = config['detailed_hits']

        self.session = requests.Session()
    
    def titleUpdate(self):
        while True:
            setTitle(f'[OneManBuilds GetProxyList Tool] ^| {version} ^| HITS: {self.hits} ^| RETRIES: {self.retries} ^| THREADS: {active_count() - 1}')
            sleep(0.1)

    def worker(self):
        try:
            headers = {
                'User-Agent':getRandomUserAgent()
            }
            proxy = getRandomProxy(self.use_proxy,self.proxy_type)
            response = self.session.get('https://api.getproxylist.com/proxy',headers=headers,proxies=proxy)
            if response.json()['cache']['hit'] == 'HIT':
                self.hits += 1
                scraped_proxy = f"{response.json()['ip']}:{response.json()['port']}"
                printText(self.lock,colors['white'],colors['green'],'HIT',scraped_proxy)
                
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(f'{scraped_proxy}\n')

                if self.detailed_hits == 1:
                    country = response.json()['country']
                    protocol = response.json()['protocol']
                    connectTime = response.json()['connectTime']
                    downloadSpeed = response.json()['downloadSpeed']
                    uptime = response.json()['uptime']

                    with open('[Data]/[Results]/detailed_hits.txt','a',encoding='utf8') as f:
                        f.write(f'Proxy: {scraped_proxy} | Country: {country} | Protocol: {protocol} | ConnectTime: {connectTime} | DownloadSpeed: {downloadSpeed} | UpTime: {uptime}\n')
            else:
                self.retries += 1
                self.worker()
        except Exception:
            self.retries += 1
            self.worker()
    
    def start(self):
        Thread(target=self.titleUpdate).start()
        while True:
            if active_count() <= self.threads:
                Thread(target=self.worker).start()


if __name__ == '__main__':
    main = Main()
    main.start()