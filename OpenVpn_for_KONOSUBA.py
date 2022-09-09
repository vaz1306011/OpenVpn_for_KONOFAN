import configparser
import os

import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    n = int(input("輸入編號:"))

    URL = "https://www.vpngate.net/"
    URL_CN = "https://www.vpngate.net/cn/"
    vpngate = requests.get(URL_CN)
    soup = BeautifulSoup(vpngate.text, "html.parser")
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    count = 0
    rows = soup.select("#vpngate_main_table")[0].find_all("tr")[17:]
    target_country = "Japan"
    black_list = ["219.100."]
    for row in rows:
        tds = row.find_all("td")

        # 檢查國家
        if tds[0].text != target_country:
            continue

        # 檢查 有沒有openvpn
        if "OpenVPN" not in tds[6].text:
            continue

        # 檢查黑名單
        ip = tds[1].find_all("span")[1].text
        if any([ip.startswith(i) for i in black_list]):
            continue

        count += 1
        if count >= n:
            break
    else:
        print("沒有符合的ip")
        exit()

    download_url = URL_CN + tds[6].a["href"]
    openvpn = requests.get(download_url)
    soup = BeautifulSoup(openvpn.text, "html.parser")
    ovpn = soup.select("ul.listBigArrow li a")

    def get_url(ovpn):
        for t in ovpn:
            if "TCP" in str(t.text):
                return URL + t["href"]

        for t in ovpn:
            if "UDP" in str(t.text):
                return URL + t["href"]

    file = requests.get(get_url(ovpn))
    path = config.get("config", "path")
    with open(path, "wb") as fp:
        fp.write(file.content)
        fp.write(
            "route-nopull\ndhcp-option DNS 8.8.8.8\nroute api.konosubafd.jp\nroute static.konosubafd.jp\n".encode()
        )

    print(f"IP:{ip}")
    print(f"已輸出至 {path}")

    os.system("pause")
