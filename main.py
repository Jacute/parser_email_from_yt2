import traceback
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import re
import time
import os
import csv
import sys


try:
    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")

    options.set_preference("dom.webdriver.enabled", False)
    options.headless = True

    driver = webdriver.Firefox(
        executable_path=GeckoDriverManager().install(),
        options=options
    )
except Exception as e:
    print('Неудачная настройка браузера!')
    print(traceback.format_exc())
    print(input('Press ENTER to close this program'))
    sys.exit()
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
urls = []
data_without_mail = []
data = []
regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
regex_url1 = '(?P<url>https?://[^\s]+)'
regex_url2 = '(?P<url>http?://[^\s]+)'
actions = webdriver.ActionChains(driver)

try:
    with open('data.txt', mode='r') as f:
        file = f.read().split('\n')
    with open('exceptions.txt', mode='r') as f:
        exceptions = f.read().split('\n')
    for i in file:
        if i != '':
            print(f'Парсинг данных со всех запросов из data.txt: {file.index(i) + 1} из {len(file)}')
            driver.get(f'https://www.youtube.com/results?search_query={i}')
            driver.implicitly_wait(5)
            while True:
                scroll_height = 2000
                document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
                driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
                time.sleep(1.5)
                document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
                if document_height_after == document_height_before:
                    break
            videos = driver.find_elements_by_xpath('//a[@id="video-title"]')
            urls.extend([j.get_attribute('href') for j in videos])
    description_urls = []
    for i in range(len(urls)):
        print(f'Парсинг ссылок из описания {i + 1} из {len(urls)}')
        try:
            driver.get(urls[i])
            driver.implicitly_wait(15)
        except Exception:
            continue
        try:
            more = driver.find_element_by_xpath('//paper-button[@id="more"]')
            more.send_keys(Keys.PAGE_DOWN)
            more.send_keys(Keys.PAGE_DOWN)
            more.click()
        except Exception:
            pass
        try:
            description = driver.find_element_by_xpath('//div[@id="description"]').text
        except Exception:
            continue
        urls1 = re.findall(regex_url1, description)
        urls2 = re.findall(regex_url2, description)
        k = urls1 + urls2
        for j in k:
            for q in exceptions:
                if q in j:
                    break
            if q not in j:
                description_urls.append(j)
    driver.set_page_load_timeout(10)
    for q in range(len(description_urls)):
        print(f'Пытаемся достать почты из сайтов {q + 1} из {len(description_urls)}')
        email = ''
        url = description_urls[q]
        try:
            driver.get(url)
            driver.implicitly_wait(15)
        except Exception:
            continue
        try:
            body = driver.find_element_by_xpath('/html').text
            email = re.findall(regex, body)[-1]
        except Exception:
            email = ''
        data.append((url, email))
        driver.implicitly_wait(15)

    with open('result.csv', mode='w', newline='') as f:
        print('Запись в csv...')
        writer = csv.writer(
            f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Ссылка', 'Почта'))
        for i in data:
            writer.writerow((i[0], i[1]))
        print('Запись завершена')
    print('Парсинг завершён!')
except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
finally:
    driver.close()
    driver.quit()
    print(input('Нажмите ENTER, чтобы закрыть это окно'))
