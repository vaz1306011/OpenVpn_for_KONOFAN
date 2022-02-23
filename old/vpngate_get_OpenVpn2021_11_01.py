import requests
from bs4 import BeautifulSoup
import os
import configparser


def main():
    try:
        vpngate = requests.get('https://www.vpngate.net/cn/')
        soup = BeautifulSoup(vpngate.text, 'html.parser')
        n = int(input('輸入編號:'))

        if n % 2:
            n = (n-1)//2
            vpn_download_url = soup.select("td.vg_table_row_1 a")
        else:
            n = n//2-1
            vpn_download_url = soup.select("td.vg_table_row_0 a")

        def find_ip(href: str):
            start = href.find('&ip=')+4
            end = href.find('&', start)
            return href[start:end]

        for t in vpn_download_url:
            if t.text == 'OpenVPN配置文件':
                if n == 0:
                    ip = find_ip(t['href'])
                    if ip.startswith('219.100.'):
                        continue
                    url = 'https://www.vpngate.net/cn/' + t['href']
                    break
                n -= 1
        print(ip)

        openvpn = requests.get(url)
        soup = BeautifulSoup(openvpn.text, 'html.parser')
        ovpn = soup.select("ul.listBigArrow li a")

        def get_url(ovpn):
            for t in ovpn:
                if 'TCP' in str(t.strong):
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

    except:
        print('輸出錯誤')
    os.system("pause")


if __name__ == "__main__":
    main()
