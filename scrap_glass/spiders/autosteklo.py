from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import requests
import os
import autoflake
import pandas as pd

user_agent = UserAgent().random
data = []
class Spider1Spider(CrawlSpider):
    name = "autosteklo"
    allowed_domains = ["autosteklo.ru"]
    start_urls = ["https://autosteklo.ru/st-petersburg/"]

    rules = (
        Rule(LinkExtractor(allow=(r'autosteklo.ru/st-petersburg/steklo/', r'autosteklo.ru/st-petersburg/glass-types/', r'autosteklo.ru/st-petersburg/offer/'), deny=()), callback='parse', follow=True),
    )

    async def parse(self, response):
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        if 'filter' in query_params and any(param in query_params['filter'] for param in ['front', 'side', 'back']):
            await self.parse_details(response)

    def download_image(self, image_url):
        if image_url and image_url.startswith('https:'):
            response = requests.get(image_url)
            if response.status_code == 200:
                folder_path = 'images'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                filename = os.path.join(folder_path, os.path.basename(image_url))

                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        return None

    def parse_details(self, response):

        print(response.url)

        model = response.xpath('/html/body/main/div[1]/section/div[2]/h2/text()').get()
        if model:
            match = re.match(r'^(.*?)\s+(.*)$', model)
            if match:
                brand = match.group(1)
                model = match.group(2)
                print("Brand:", brand)
                print("Model:", model)
        else:
            print("Model not found")
    
        glass = response.xpath('/html/body/main/div[2]/section/div/div[2]/header/h2/a/text()').get()
        print(glass)

        art = response.xpath('/html/body/main/div[2]/section/div/div[2]/header/div/div[1]/text()').get()
        print(art)

        style_glass = response.xpath('/html/body/main/section/ul/li[5]/text()').get()
        print(style_glass)

        years = response.xpath('/html/body/main/div[1]/section/div[2]/div/div[2]/strong/text()').get()
        print(years)

        brand_logo = response.xpath('//div[@class="brand"]/img/@alt').get()
        if brand_logo is None:
            brand_logo = response.xpath('//div[@class="brand"]/img/@src').get()

        pictures_url = response.xpath('//img[@alt="Изображения стекла"]/@src').get()
        print(pictures_url)

        country = response.xpath('/html/body/main/div[2]/section/div/div[2]/header/div/div[2]/text()').get()
        print(country)

        price = response.xpath('/html/body/main/div[2]/section/div/div[2]/div[1]/div[2]/div[1]/span[2]/text()').get()
        price_mod = price.strip()
        print(price_mod)

        ustanovka = response.xpath('/html/body/main/div[2]/section/div/div[2]/div[1]/div[2]/div[2]/span[2]/text()').get()
        ustanovka_mod = ustanovka.strip()
        print(ustanovka_mod)

        local_image_path = self.download_image(pictures_url)

        tree = BeautifulSoup(response.text, 'lxml')
        params = tree.find('div', class_="tech-info")
        row = params.find_all('div', class_="row")

        row_data = {}

        for i in row:
            key = i.find('div', class_="col key")
            key = key.text.strip()

            value = i.find('div', class_="col val")
            value = value.text.strip()

            print(f"{key}: {value}")
            row_data[key] = f'{key}: {value}'


        data.append({
                'URL': response.url,
                'Название': glass,
                'Артикул': art,
                'Тип': style_glass,
                'Марка': brand,
                'Модель': model,
                'Года': years,
                'Лого': brand_logo,
                'Ссылка на картинку': pictures_url,
                'Картинка': local_image_path,
                'Страна': country,
                'Цена': price_mod,
                'Установка': ustanovka_mod,
                **row_data
        })

    def close(self, reason):
        try:
            df = pd.DataFrame(data)
            with pd.ExcelWriter('data.xlsx', mode='w', engine='openpyxl') as writer:
                df.to_excel(writer, index=False, header=False)
                print("Data appended.")
        except Exception as e:
            print("An error occurred:", str(e))