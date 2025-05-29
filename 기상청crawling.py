import requests
from bs4 import BeautifulSoup

def download_txt_file(url, save_path):
    reponse = requests.get(url)

    text = reponse.content.decode('euc-kr')
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(text)

url = 'https://apihub.kma.go.kr/api/typ01/url/fct_shrt_reg.php?tmfc=0&authKey=Be_01WPVTyav9NVj1a8mBQ'
save_file_path = 'weather.txt'
download_txt_file(url, save_file_path)