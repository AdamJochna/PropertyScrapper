from bs4 import BeautifulSoup
import requests
import csv
import re
import random
import time
import pandas as pd
import numpy as np
import pickle
import json

random.seed(time.time())


def run_scraping_job(task, offer_sender):
    regs = [reg.strip() for reg in task["regions"].split(',') if len(reg) > 0]
    locs = [loc.strip() for loc in task['localizations'].split(',') if len(loc) > 0]
    locs = [loc.lower() for loc in locs]

    str_mapping = {
        'ą': 'a',
        'ć': 'c',
        'ę': 'e',
        'ł': 'l',
        'ń': 'n',
        'ó': 'o',
        'ś': 's',
        'ź': 'z',
        'ż': 'z',
    }

    def transform_string(x):
        for (k, v) in str_mapping.items():
            x = x.replace(k, v)

        return x

    locs = [transform_string(loc.lower()) for loc in locs]

    regions_mapping = {
        'pl-wlkp': 'wielkopolskie',
        'pl-swtk': 'swietokrzyskie',
        'pl-zpom': 'zachodniopomorskie',
        'pl-slsk': 'slaskie',
        'pl-podk': 'podkarpackie',
        'pl-mzwc': 'mazowieckie',
        'pl-podl': 'podlaskie',
        'pl-lubu': 'lubuskie',
        'pl-ldzk': 'lodzkie',
        'pl-kupm': 'kujawsko-pomorskie',
        'pl-lube': 'lubuskie',
        'pl-opol': 'opolskie',
        'pl-pomo': 'pomorskie',
        'pl-dlns': 'dolnoslaskie',
        'pl-malo': 'malopolskie',
        'pl-warm': 'warminsko-mazurskie',
    }

    regs = [regions_mapping[reg] for reg in regs]
    links = []

    offer_type_mapping = {'sell': 'sprzedaz',
                          'rent': 'wynajem'}

    if task['site'] in ['Only Olx', 'Olx with offers linking to Otodom']:
        for place in regs + locs:
            links.append("https://www.olx.pl/nieruchomosci/mieszkania/{}/q-{}/".format(offer_type_mapping[task['offersType']], place))

    elif task['site'] == 'Only Otodom':
        for place in regs + locs:
            links.append("https://www.otodom.pl/{}/mieszkanie/q-{}/".format(offer_type_mapping[task['offersType']], place))

    all_olx = set()
    all_oto = set()

    for link in links:
        olx_link_offers, oto_link_offers = get_offers(link)
        all_olx = all_olx.union(olx_link_offers)
        all_oto = all_oto.union(oto_link_offers)

    links_to_scrape = set()

    if task['site'] == 'Only Olx':
        links_to_scrape = links_to_scrape.union(all_olx)
    elif task['site'] == 'Only Otodom':
        links_to_scrape = links_to_scrape.union(all_oto)
    elif task['site'] == 'Olx with offers linking to Otodom':
        links_to_scrape = links_to_scrape.union(all_olx)
        links_to_scrape = links_to_scrape.union(all_oto)

    for offer_link in links_to_scrape:
        if 'otodom' in offer_link:
            try:
                print(offer_link)
                offer_sender(scrap_oto_sell_offer(offer_link))
            except Exception as e:
                print('Exception ', e)
        elif 'olx' in offer_link:
            try:
                print(offer_link)
                offer_sender(scrap_olx_sell_offer(offer_link))
            except Exception as e:
                print('Exception ', e)


def get_offers(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    try:
        if 'olx' in link:
            pages_num = int(soup
                            .find("div", {"class": "pager rel clr"})
                            .find("a", {"data-cy": "page-link-last"})
                            .find("span")
                            .text)
        elif 'otodom' in link:
            pages_num = int(soup
                            .find("ul", {"class": "pager"})
                            .find_all("li")[-2]
                            .text)
    except:
        pages_num = 1

    pages_list = list(range(1, pages_num + 1))
    random.shuffle(pages_list)

    all_olx = set()
    all_oto = set()

    for idx, page_idx in enumerate(pages_list):
        time.sleep((random.random() + 1) / 10)

        source = requests.get(link + '/?page={}'.format(page_idx)).text
        soup = BeautifulSoup(source, 'lxml')

        if 'olx' in link:
            soup = soup.find("table", {"fixed offers breakword redesigned"})
        elif 'otodom' in link:
            soup = soup.find("div", {"class": "col-md-content section-listing__row-content"})


        links = [a.get('href') for a in soup.find_all('a', href=True)]
        all_olx = all_olx.union(set([link.split('#')[0] for link in links if 'https://www.olx.pl/oferta/' in link and not ';promoted' in link]))
        all_oto = all_oto.union(set([link for link in links if 'https://www.otodom.pl/oferta/' in link and not ';promoted' in link]))
        print('page: {}/{}, page_num: {}, olx:{}, oto:{}'.format(idx, len(pages_list), page_idx, len(all_olx),len(all_oto)))

    return all_olx, all_oto


def scrap_olx_sell_offer(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    offer = {}
    offer['site'] = 'olx'
    offer['price'] = int(float(soup.find('strong', {'class': 'pricelabel__value'}).text.replace('zł', '').replace(' ', '').replace(',', '.')))
    offer['address'] = soup.find('div', {'class': 'offer-user__address'}).find('address').text
    offer['address'] = offer['address'].split(',')
    offer['address'] = [loc.strip() for loc in offer['address']]
    offer['address'] = '|' + '|'.join(offer['address']) + '|'

    table = soup.find('ul', {'class': 'offer-details'})
    table_item_dict = {}

    for table_item in table.findAll('li', {'class': 'offer-details__item'}):
        str0 = table_item.find('span', {'class': 'offer-details__name'}).text.strip()
        str1 = table_item.find('strong', {'class': 'offer-details__value'}).text.strip()
        table_item_dict[str0] = str1

    offer['level'] = table_item_dict['Poziom']
    offer['size'] = table_item_dict['Powierzchnia'].split(' ')[0].replace(',', '.')
    offer['rooms'] = table_item_dict['Liczba pokoi'].split(' ')[0]
    offer['market'] = table_item_dict['Rynek']
    offer['building_type'] = table_item_dict['Rodzaj zabudowy']

    if offer['level'] == 'Parter':
        offer['level'] = '0'

    if offer['building_type'] == 'Pozostałe':
        offer['building_type'] = None

    offer['price_per_msq'] = str(int(int(offer['price']) / float(offer['size'])))

    for key in offer.keys():
        offer[key] = str(offer[key]).lower()

    return offer


def scrap_oto_sell_offer(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')
    offer = {}
    offer['site'] = 'otodom'
    offer['price'] = soup.find('div', {'class': 'css-1vr19r7'}).text
    offer['price'] = int(float(offer['price'].replace('zł', '').replace(' ', '').replace(',', '.')))
    offer['address'] = soup.find('a', {'class': 'css-12hd9gg'}).text.split('}')[-1]
    offer['address'] = offer['address'].split(',')
    offer['address'] = [loc.strip() for loc in offer['address']]
    offer['address'] = '|' + '|'.join(offer['address']) + '|'



    table = soup.find('div', {'class': 'css-1ci0qpi'})

    mapping = {
        'Piętro': 'level',
        'Powierzchnia': 'size',
        'Liczba pokoi': 'rooms',
        'Rynek': 'market',
        'Rodzaj zabudowy': 'building_type',
    }

    for value in mapping.values():
        offer[value] = None

    for table_item in table.findAll('li'):
        str0 = table_item.text.split(':')[0].strip()
        str1 = table_item.text.split(':')[1].strip()

        if str0 in mapping.keys():
            offer[mapping[str0]] = str1

    if offer['level'] == 'parter':
        offer['level'] = '0'

    if offer['size'] is not None:
        offer['size'] = offer['size'].split(' ')[0].replace(',', '.')

    offer['price_per_msq'] = str(int(int(offer['price'])/float(offer['size'])))

    for key in offer.keys():
        offer[key] = str(offer[key]).lower()

    keys = list(offer.keys())
    
    for key in keys:
        if offer[key] == 'none':
            del offer[key]

    return offer


# if __name__ == '__main__':
#     offer = scrap_oto_sell_offer('https://www.otodom.pl/oferta/dom-gdynia-wzgorze-bernadowo-ID41NUY.html')
#     print(offer)
