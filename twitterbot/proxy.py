import requests, json
from lxml.html import fromstring


def get_proxies():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath("//tbody/tr"):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join(
                [i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]]
            )
            try:
                requests.get("https://www.gocovid.gq/", proxies={"https": f"{proxy}"}, timeout=1)
                proxies.add(proxy)
            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ProxyError,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.SSLError):
                pass
            if len(proxies) >= 5:
                break
    return list(proxies)


def get_proxy():
    url = "http://pubproxy.com/api/proxy?https=true&speed=10"
    response = requests.get(url=url)
    for x in range(5):
        try:
            resp_dict = eval(response.content.decode('utf-8'))
        except:
            resp_dict = json.dumps(response.content.decode('utf-8'))
        ip_port = resp_dict['data'][0]['ipPort']

        try:
            requests.get("https://www.google.com/", proxies={"https": f"{ip_port}"}, timeout=5)
            return ip_port
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ProxyError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError):
            pass

    return None
