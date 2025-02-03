# Scrapy-autosteklo
Crawler для парсинга автомобильных стекол autosteklo.ru

# Описание и особенности:
Crawler собирает все характеристики товаров для каждого предложенного на сайте автомобиля и записывает в xlsx.
Главная особенность - скачивание чертежей стекол в отдельную папку и автоматическое указание локальной ссылки напротив конкретной строки в таблице.

```
git clone https://github.com/tetch201/Scrapy-autosteklo
cd Scrapy-autosteklo
python -m venv venv
venv/scripts/activate
```
# После установки библиотек и фреймворка:

```
cd scrap_glass/spiders
scrapy crawl autosteklo
```
