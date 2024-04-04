import threading
import requests
import urllib3
import random
from bs4 import BeautifulSoup
import keyboard
import logging
import time
import csv
import sys
import signal
import os

TIMEOUT = (3.05,27)
THREADS = 200

user_agent_list = requests.get("https://pastebin.com/raw/uQsyjWZY").text.splitlines()

session = requests.Session()
session.headers['User-Agent'] = random.choice(user_agent_list)
session.max_redirects = 300

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def check_proxy(proxy, proxy_type="all"):
	if proxy_type == "all":
		for pt in ["http","socks5","socks4"]:
			res = check_proxy(proxy, pt)
			if res: return res
		return False
	
	try:
		proxy = proxy.split('\n',1)[0]
		session = requests.Session()
		session.headers['User-Agent'] = random.choice(user_agent_list)
		session.max_redirects = 300
		start_ping = time.time()
		session.get("http://google.com/", 
					proxies={'http':proxy_type+'://' + proxy,
							 'https':proxy_type+'://' + proxy}, 
								  timeout=TIMEOUT, allow_redirects=True)
	except (requests.exceptions.ConnectionError,
			requests.exceptions.ConnectTimeout,
			requests.exceptions.HTTPError,
			requests.exceptions.Timeout,
			urllib3.exceptions.ProxySchemeUnknown,
			requests.exceptions.ChunkedEncodingError,
			requests.exceptions.TooManyRedirects,
			requests.exceptions.InvalidProxyURL,
			requests.exceptions.InvalidURL) as e:
		return False
	latency = round(time.time()-start_ping,3)
	logging.info("+ "+proxy_type.upper()+" "+proxy+" "+str(latency)+"ms")
	return (proxy_type+"://"+proxy,latency)

def filter(text,symbols="1234567890."):
	new_text = ""
	for i in text:
		if i in symbols:
			new_text += i
	return new_text

args = ["".join(i.split("\r")) for i in sys.argv[1:]]

input(str(args))

only = "all"
if "--only-socks5" in args:
	only = "socks5"
if "--only-http" in args:
	only = "http"

proxies = []

tried_parse = 0
must_tried_parse = 0

socks5_count = 0
socks4_count = 0
http_count = 0

proxies_file = open('proxies.csv', 'w', newline='')
proxies_writer = csv.writer(proxies_file)
proxies_writer.writerow(['IP:PORT', 'TYPE', 'LATENCY'])

def add_proxy(p):
	global must_tried_parse
	must_tried_parse += 1
	def g(p):
		try:
			global proxies,proxies_writer,socks5_count,http_count,socks4_count,tried_parse,only
			if p not in proxies and p != "":
				p = check_proxy(p,only)
				if p:
					proxies.append(p[0])
					if p[0].startswith("socks5://"):
						socks5_count += 1
						proxies_writer.writerow([p[0][9:], 'SOCKS5', str(p[1])])
						proxies_file.flush()
					elif p[0].startswith("http://"):
						http_count += 1
						proxies_writer.writerow([p[0][7:], 'HTTP', str(p[1])])
						proxies_file.flush()
					elif p[0].startswith("socks4://"):
						socks4_count += 1
						proxies_writer.writerow([p[0][9:], 'SOCKS4', str(p[1])])
						proxies_file.flush()
		except: pass
		tried_parse += 1
	threading.Thread(target=g,args=(p,)).start()

parsed_count = 0

def a():
	try:
		global proxies, parsed_count
		parsed = session.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt").text.split("\n")
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" TheSpeedX/PROXY-List")
	parsed_count += 1
threading.Thread(target=a).start()

def a1():
	try:
		global proxies, parsed_count
		parsed = session.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt").text.split("\n")
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" TheSpeedX/PROXY-List socks5")
	parsed_count += 1
threading.Thread(target=a1).start()

def b():
	try:
		global proxies, parsed_count
		parsed = session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt").text.split("\n")
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" monosans/proxy-list")
	parsed_count += 1
threading.Thread(target=b).start()

def b1():
	try:
		global proxies, parsed_count
		parsed = session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt").text.split("\n")
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" monosans/proxy-list socks5")
	parsed_count += 1
threading.Thread(target=b1).start()

def c():
	try:
		global proxies, parsed_count
		parsed = session.get("https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt").text.split("\n")
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" clarketm/proxy-list")
	parsed_count += 1
threading.Thread(target=c).start()

def d():
	try:
		global proxies, parsed_count
		parsed = [i["ip"]+":"+i["port"] for i in session.get("https://proxylist.geonode.com/api/proxy-list?sort_by=lastChecked&sort_type=desc").json()["data"]]
		for i in parsed: add_proxy(i)
	except: pass
	logging.info("Parsed "+str(len(parsed))+" proxylist.geonode.com")
	parsed_count += 1
threading.Thread(target=d).start()

def e():
	try:
		global proxies, parsed_count
		tr = BeautifulSoup(session.get("https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/").text, "lxml").\
			body.find('figure', attrs={'class':'wp-block-table'}).find_all("tr")
		for i in tr[1:]:
			if i == None: continue
			td = i.find_all("td")[:2]
			p = td[0].find("strong").text+":"+td[1].text
			add_proxy(p)
	except: pass
	logging.info("Parsed vpnoverview.com")
	parsed_count += 1
threading.Thread(target=e).start()

def f():
	try:
		global proxies, parsed_count
		tr = BeautifulSoup(session.get("https://www.proxy-list.download/HTTP").text, "lxml").\
			body.find('table', attrs={'id':'example1'}).find_all("tr")
		for i in tr[1:]:
			if i == None: continue
			td = i.find_all("td")[:2]
			p = filter(td[0].text)+":"+filter(td[1].text)
			add_proxy(p)
	except: pass
	logging.info("Parsed www.proxy-list.download")
	parsed_count += 1
threading.Thread(target=f).start()

def g():
	try:
		global proxies, parsed_count
		html = BeautifulSoup(session.get("https://free-proxy-list.com/?page=&up_time=0&search=Search").text, "lxml")
		pages = int(html.body.find('a',string=">>").attrs["data"])
		pages_collected = 0
		for i in range(pages):
			def x(i):
				nonlocal pages_collected
				global proxies
				html = BeautifulSoup(session.get(f"https://free-proxy-list.com/?page={i+1}&up_time=0&search=Search").text, "lxml")
				tr = html.body.find('table',attrs={"class":"proxy-list"}).find_all("tr")
				for i in tr[1:]:
					if i == None: continue
					td = i.find_all("td")[:3]
					p = filter(td[0].find("a").text)+":"+filter(td[2].text)
					add_proxy(p)
				pages_collected += 1
			threading.Thread(target=x,args=(int(str(i)),)).start()
			time.sleep(0.2)
		while pages_collected < pages:
			time.sleep(1)
	except: pass    
	logging.info("Parsed free-proxy-list.com")
	parsed_count += 1
threading.Thread(target=g).start()

def h():
	try:
		global proxies, parsed_count
		tr = BeautifulSoup(session.get("https://www.us-proxy.org/").text, "lxml").\
			body.find('table').find_all("tr")
		for i in tr[1:]:
			if i == None: continue
			td = i.find_all("td")[:2]
			p = filter(td[0].text)+":"+filter(td[1].text)
			add_proxy(p)
	except: pass
	logging.info("Parsed www.us-proxy.org")
	parsed_count += 1
threading.Thread(target=h).start()

def j():
	try:
		global proxies, parsed_count
		tr = BeautifulSoup(session.get("https://free-proxy-list.net/").text, "lxml").\
			body.find('table').find_all("tr")
		for i in tr[1:]:
			if i == None: continue
			td = i.find_all("td")[:2]
			p = filter(td[0].text)+":"+filter(td[1].text)
			add_proxy(p)
	except: pass
	logging.info("Parsed free-proxy-list.net")
	parsed_count += 1
threading.Thread(target=j).start()

while parsed_count < 11 or tried_parse < must_tried_parse:
	time.sleep(1)
	logging.info(f"Parsed: {parsed_count}/11 {tried_parse}/{must_tried_parse}")

logging.info("Parsed "+str(len(proxies))+" proxies")

print("Proxy count:",len(proxies))
print("SOCKS5 count:",socks5_count)
print("SOCKS4 count:",socks4_count)
print("HTTP count:",http_count)
