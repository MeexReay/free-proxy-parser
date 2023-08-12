import threading
import requests
import urllib3
import random
from bs4 import BeautifulSoup
import logging
import queue
import time
import copy

URL = "http://google.com/"
TIMEOUT = (3.05,27)
THREADS = 100

with open("user-agents.txt","r",encoding="utf8") as f:  
    user_agent_list = f.read().splitlines()

session = requests.Session()
session.headers['User-Agent'] = random.choice(user_agent_list)
session.max_redirects = 300

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def check_proxy_socks5(proxy):
    try:
        proxy = proxy.split('\n',1)[0]
        session = requests.Session()
        session.headers['User-Agent'] = random.choice(user_agent_list)
        session.max_redirects = 300
        session.get(URL, proxies={'http':'socks5://' + proxy,
                                  'https':'socks5://' + proxy}, 
                                  timeout=TIMEOUT, allow_redirects=True)
    except requests.exceptions.ConnectionError as e:
        return False
    except requests.exceptions.ConnectTimeout as e:
        return False
    except requests.exceptions.HTTPError as e:
        return False
    except requests.exceptions.Timeout as e:
        return False
    except requests.exceptions.ChunkedEncodingError as e:
        return False
    except urllib3.exceptions.ProxySchemeUnknown as e:
        return False
    except requests.exceptions.TooManyRedirects as e:
        return False
    logging.info("+ "+proxy)
    return True

def check_proxy(proxy):
    try:
        proxy = proxy.split('\n',1)[0]
        session = requests.Session()
        session.headers['User-Agent'] = random.choice(user_agent_list)
        session.max_redirects = 300
        session.get(URL, proxies={'http':'http://' + proxy,
                                  'https':'https://' + proxy}, 
                                  timeout=TIMEOUT, allow_redirects=True)
    except requests.exceptions.ConnectionError as e:
        return check_proxy_socks5(proxy)
    except requests.exceptions.ConnectTimeout as e:
        return check_proxy_socks5(proxy)
    except requests.exceptions.HTTPError as e:
        return check_proxy_socks5(proxy)
    except requests.exceptions.Timeout as e:
        return check_proxy_socks5(proxy)
    except urllib3.exceptions.ProxySchemeUnknown as e:
        return check_proxy_socks5(proxy)
    except requests.exceptions.ChunkedEncodingError as e:
        return check_proxy_socks5(proxy)
    except requests.exceptions.TooManyRedirects as e:
        return check_proxy_socks5(proxy)
    logging.info("+ "+proxy)
    return True

def clear_proxies(proxies,on_checked=lambda x:None):
    clean_proxies = []
    checked = 0
    chunks = [[] for i in range(THREADS)]

    x = 0
    for v in proxies:
        chunks[x].append(v)
        x += 1
        if x >= THREADS:
            x = 0
    
    def target(chunk):
        nonlocal clean_proxies, checked
        for i in chunk:
            if check_proxy(i):
                clean_proxies.append(i)
                on_checked(i)
            checked += 1

    for i in range(THREADS):
        threading.Thread(target=target,args=(chunks[i],)).start()

    while checked < len(proxies):
        time.sleep(1)
        logging.info(str(checked)+"/"+str(len(proxies)))

    return clean_proxies

def filter(text,symbols="1234567890."):
    new_text = ""
    for i in text:
        if i in symbols:
            new_text += i
    return new_text

def get_proxies():
    proxies = []

    parsed_count = 0

    def a():
        nonlocal proxies, parsed_count
        logging.info("Parsing TheSpeedX/PROXY-List...")
        parsed = session.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt").text.split("\n")
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" TheSpeedX/PROXY-List")
        parsed_count += 1
    threading.Thread(target=a).start()

    def b():
        nonlocal proxies, parsed_count
        logging.info("Parsing monosans/proxy-list...")
        parsed = session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt").text.split("\n")
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" monosans/proxy-list")
        parsed_count += 1
    threading.Thread(target=b).start()

    def c():
        nonlocal proxies, parsed_count
        logging.info("Parsing clarketm/proxy-list...")
        parsed = session.get("https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt").text.split("\n")
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" clarketm/proxy-list")
        parsed_count += 1
    threading.Thread(target=c).start()

    def d():
        nonlocal proxies, parsed_count
        logging.info("Parsing proxylist.geonode.com...")
        parsed = [i["ip"]+":"+i["port"] for i in session.get("https://proxylist.geonode.com/api/proxy-list?sort_by=lastChecked&sort_type=desc&protocols=http,https").json()["data"]]
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" proxylist.geonode.com")
        parsed_count += 1
    threading.Thread(target=d).start()

    def e():
        nonlocal proxies, parsed_count
        logging.info("Parsing vpnoverview.com...")
        parsed = []
        tr = BeautifulSoup(session.get("https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/").text, "lxml").\
            body.find('figure', attrs={'class':'wp-block-table'}).find_all("tr")
        for i in tr[1:]:
            if i == None: continue
            td = i.find_all("td")[:2]
            parsed.append(td[0].find("strong").text+":"+td[1].text)
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" vpnoverview.com")
        parsed_count += 1
    threading.Thread(target=e).start()

    def f():
        nonlocal proxies, parsed_count
        logging.info("Parsing www.proxy-list.download...")
        parsed = []
        tr = BeautifulSoup(session.get("https://www.proxy-list.download/HTTP").text, "lxml").\
            body.find('table', attrs={'id':'example1'}).find_all("tr")
        for i in tr[1:]:
            if i == None: continue
            td = i.find_all("td")[:2]
            parsed.append(filter(td[0].text)+":"+filter(td[1].text))
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" www.proxy-list.download")
        parsed_count += 1
    threading.Thread(target=f).start()

    def g():
        nonlocal proxies, parsed_count
        logging.info("Parsing free-proxy-list.com...")
        parsed = []
        html = BeautifulSoup(session.get("https://free-proxy-list.com/?page=&port=&type%5B%5D=http&type%5B%5D=https&up_time=0&search=Search").text, "lxml")
        pages = int(html.body.find('a',string=">>").attrs["data"])
        pages_collected = 0
        for i in range(pages):
            def x(i):
                nonlocal parsed,pages_collected
                html = BeautifulSoup(session.get(f"https://free-proxy-list.com/?page={i+1}&port=&type%5B%5D=http&typ"\
                                                    "e%5B%5D=https&up_time=0&search=Search").text, "lxml")
                tr = html.body.find('table',attrs={"class":"proxy-list"}).find_all("tr")
                for i in tr[1:]:
                    if i == None: continue
                    td = i.find_all("td")[:3]
                    parsed.append(filter(td[0].find("a").text)+":"+filter(td[2].text))
                pages_collected += 1
            threading.Thread(target=x,args=(int(str(i)),)).start()
            time.sleep(0.2)
        while pages_collected < pages:
            time.sleep(1)
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" free-proxy-list.com")
        parsed_count += 1
    threading.Thread(target=g).start()

    def h():
        nonlocal proxies, parsed_count
        logging.info("Parsing www.us-proxy.org...")
        parsed = []
        tr = BeautifulSoup(session.get("https://www.us-proxy.org/").text, "lxml").\
            body.find('table').find_all("tr")
        for i in tr[1:]:
            if i == None: continue
            td = i.find_all("td")[:2]
            parsed.append(filter(td[0].text)+":"+filter(td[1].text))
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" www.us-proxy.org")
        parsed_count += 1
    threading.Thread(target=h).start()

    def j():
        nonlocal proxies, parsed_count
        logging.info("Parsing free-proxy-list.net...")
        parsed = []
        tr = BeautifulSoup(session.get("https://free-proxy-list.net/").text, "lxml").\
            body.find('table').find_all("tr")
        for i in tr[1:]:
            if i == None: continue
            td = i.find_all("td")[:2]
            parsed.append(filter(td[0].text)+":"+filter(td[1].text))
        proxies += parsed
        logging.info("Parsed "+str(len(parsed))+" free-proxy-list.net")
        parsed_count += 1
    threading.Thread(target=j).start()

    while parsed_count < 9:
        time.sleep(1)

    proxies = list(set(proxies))
    proxies.remove("")
    logging.info("Parsed "+str(len(proxies))+" proxies")
    return proxies

if __name__ == "__main__":
    update_check = filter(input("Update check.txt (0/1): ")) == "1"

    if update_check:
        with open("check.txt","w",encoding="utf8") as f:
            proxies = get_proxies()
            for i in proxies:
                f.write(i+"\n")
                f.flush()
            f.close()
        print("Saved proxy to check")
        time.sleep(5)
    else:
        with open("check.txt","r",encoding="utf8") as f:
            proxies = f.read().splitlines()
            f.close()
        print("Loaded proxy to check")
    print("Proxy is checking...")
    with open("proxies.txt","w",encoding="utf8") as f:
        def on_checked(proxy):
            f.write(proxy+"\n")
            f.flush()
        proxies = clear_proxies(proxies,on_checked)
        f.close()
    print("\n".join(proxies),len(proxies))