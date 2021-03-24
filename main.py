import traceback
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
import urlextract
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
    # options.headless = True

    driver = webdriver.Firefox(
        executable_path=GeckoDriverManager().install(),
        options=options
    )
    driver.set_page_load_timeout(10)
except Exception as e:
    print('Неудачная настройка браузера!')
    print(traceback.format_exc())
    print(input('Press ENTER to close this program'))
    sys.exit()
extractor = urlextract.URLExtract()
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
urls = []
data_without_mail = []
data = []
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
regex_url1 = 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
regex_url2 = 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
actions = webdriver.ActionChains(driver)

try:
    with open('data.txt', mode='r') as f:
        file = f.read().split('\n')
    for i in file:
        if i != '':
            print(f'Парсинг данных со всех запросов из data.txt: {file.index(i) + 1} из {len(file)}')
            try:
                driver.get(f'https://www.youtube.com/results?search_query={i}')
            except TimeoutException:
                continue
            driver.implicitly_wait(5)
            while True:
                break
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
        driver.get(urls[i])
        driver.implicitly_wait(5)
        try:
            more = driver.find_element_by_xpath('//paper-button[@id="more"]')
            more.send_keys(Keys.PAGE_DOWN)
            more.send_keys(Keys.PAGE_DOWN)
            more.click()
        except Exception:
            pass
        description = driver.find_element_by_xpath('//div[@id="description"]').text
        urls1 = re.findall(regex_url1, description)
        urls2 = re.findall(regex_url2, description)
        for j in urls1:
            if 'youtu' not in j and 'https://vk' not in j and 'instagram' not in j and 'https://ok' not in j and\
                    'http://vk' not in j and 'facebook' not in j:
                description_urls.append(j)
        for j in urls2:
            if 'youtu' not in j and 'https://vk' not in j and 'instagram' not in j and 'https://ok' not in j and \
                    'http://vk' not in j and 'facebook' not in j:
                description_urls.append(j)
    for q in range(len(description_urls)):
        print(f'Пытаемся достать почты из сайтов {q + 1} из {len(description_urls)}')
        email = ''
        url = description_urls[q]
        try:
            driver.get(url)
            driver.implicitly_wait(10)
        except Exception:
            continue
        try:
            body = driver.find_element_by_xpath('/html').text.split()
            for i in range(len(body)):
                try:
                    if '@' in body[i]:
                        if (re.search(regex, body[i])):
                            email = body[i]
                            break
                        else:
                            email = ''
                except Exception:
                    email = ''
        except Exception:
            pass
        data.append((url, email))

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
