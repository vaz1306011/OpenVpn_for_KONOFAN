from typing import Iterable

import requests
from bs4 import BeautifulSoup


class VpnGate:
    """
    從vpngate網站獲取vpn
    """

    URL = "https://www.vpngate.net/"
    URL_CN = "https://www.vpngate.net/cn/"

    @staticmethod
    def get_open_vpn(
        n: int, countrys: Iterable[str] = None, black_list: Iterable[str] = None
    ) -> tuple[str, requests.Response] | None:
        """獲取從vpngate抓取的OpenVpn檔案

        Args:
            n (int): 第幾個ip
            countrys (Iterable[str], optional): 國家. 預設為None.
            black_list (Iterable[str], optional): 黑名單(開頭和黑名單內容一樣的會被跳過). 預設為None

        Returns:
            tuple[str, requests.Response] | None: 回傳符合條件的 [ip, 檔案], 沒有則回傳None
        """

        # 讀取網頁
        vpngate = requests.get(VpnGate.URL_CN)
        soup = BeautifulSoup(vpngate.text, "html.parser")

        # 尋找資料
        count = 0
        rows = soup.select("#vpngate_main_table")[0].find_all("tr")[17:]
        for row in rows:
            tds = row.find_all("td")

            # 檢查國家
            if tds[0].text not in countrys:
                continue

            # 檢查黑名單
            if black_list:
                ip = tds[1].find_all("span")[1].text
                if any([ip.startswith(i) for i in black_list]):
                    continue

            # 檢查有沒有openvpn
            if "OpenVPN" not in tds[6].text:
                continue

            count += 1
            if count >= n:
                break
        else:
            return None

        # 下載檔案
        def get_download_url(links):
            for t in links:
                if "TCP" in t.text:
                    return VpnGate.URL + t["href"]

            for t in links:
                if "UDP" in t.text:
                    return VpnGate.URL + t["href"]

        openvpn_url = VpnGate.URL_CN + tds[6].a["href"]
        openvpn = requests.get(openvpn_url)
        links = BeautifulSoup(openvpn.text, "html.parser").select(
            "ul.listBigArrow li a"
        )
        download_url = get_download_url(links)
        file = requests.get(download_url)

        return (ip, file)
