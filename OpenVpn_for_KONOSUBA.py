from configparser import ConfigParser
from os import system

from vpngate import VpnGate

if __name__ == "__main__":

    n = int(input("請輸入要下載幾個ip:"))
    target_country = ("Japan",)
    black_list = ("219.100.",)
    ip, file = VpnGate.get_open_vpn(n, target_country, black_list)

    # 讀取設定檔
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")

    # 寫入檔案
    path = config.get("config", "path")
    with open(path, "wb") as fp:
        fp.write(file.content)
        fp.write(
            "route-nopull\ndhcp-option DNS 8.8.8.8\nroute api.konosubafd.jp\nroute static.konosubafd.jp\n".encode()
        )

    print(f"IP:{ip}")
    print(f"已輸出至 {path}")

    system("pause")
