import configparser
import os

import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    n = int(input("輸入編號:"))

    # 讀取網頁
    URL = "https://www.vpngate.net/"
    URL_CN = "https://www.vpngate.net/cn/"
    vpngate = requests.get(URL_CN)
    soup = BeautifulSoup(vpngate.text, "html.parser")

    # 讀取設定檔
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    # 尋找資料
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

    # 下載檔案
    def get_download_url(links):
        for t in links:
            if "TCP" in t.text:
                return URL + t["href"]

        for t in links:
            if "UDP" in t.text:
                return URL + t["href"]

    openvpn_url = URL_CN + tds[6].a["href"]
    openvpn = requests.get(openvpn_url)
    links = BeautifulSoup(openvpn.text, "html.parser").select("ul.listBigArrow li a")
    download_url = get_download_url(links)
    file = requests.get(download_url)

    # 寫入檔案
    path = config.get("config", "path")
    with open(path, "wb") as fp:
        fp.write(file.content)
        fp.write(
            "route-nopull\ndhcp-option DNS 8.8.8.8\nroute api.konosubafd.jp\nroute static.konosubafd.jp\n".encode()
        )

    print(f"IP:{ip}")
    print(f"已輸出至 {path}")

    os.system("pause")
