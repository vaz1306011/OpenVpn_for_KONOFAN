import requests
from bs4 import BeautifulSoup
import os
import configparser


def main():
    print("正在載入數據...", end='')
    target_country = 'Japan'
    vpngate = requests.get('https://www.vpngate.net/cn/')
    soup = BeautifulSoup(vpngate.text, 'html.parser')
    os.system("cls")
    n = int(input('輸入編號:'))

    def get_countries(html):
        countries = []
        for i in range(30, len(html), 10):
            countries.append(html[i].text)
        return tuple(countries)

    if n % 2:
        n = (n-1)//2
        vpn_download_url = soup.select("td.vg_table_row_1 a")
        country = get_countries(soup.select("td.vg_table_row_1"))
    else:
        n = n//2-1
        vpn_download_url = soup.select("td.vg_table_row_0 a")
        country = get_countries(soup.select("td.vg_table_row_0"))

    def find_ip(href: str):
        start = href.find('&ip=')+4
        end = href.find('&', start)
        return href[start:end]

    column = -1  # 行
    conform = -1  # 配對成功次數
    for t in vpn_download_url:
        if t.text == 'OpenVPN配置文件':
            column += 1
            ip = find_ip(t['href'])
            if ip.startswith('219.100.') or country[column] != target_country:
                continue
            conform += 1
            if conform == n:
                url = 'https://www.vpngate.net/cn/' + t['href']
                break
    print(f"IP:{ip}")

    openvpn = requests.get(url)
    soup = BeautifulSoup(openvpn.text, 'html.parser')
    ovpn = soup.select("ul.listBigArrow li a")

    def get_url(ovpn):
        for t in ovpn:
            if 'TCP' in str(t.strong):
                return 'https://www.vpngate.net/'+t['href']
        else:
            for t in ovpn:
                if 'UDP' in str(t.strong):
                    return 'https://www.vpngate.net/'+t['href']

    url = get_url(ovpn)
    file = requests.get(url)
    config = configparser.ConfigParser()
    config.read('address.ini', encoding='utf-8')
    address = config['address']['address']
    with open(address, 'wb') as fp:
        fp.write(file.content)
        fp.write(
            'route-nopull\ndhcp-option DNS 8.8.8.8\nroute api.konosubafd.jp\nroute static.konosubafd.jp'.encode())
    print(f'已輸出至 {address}')

    os.system("pause")


if __name__ == "__main__":
    main()
