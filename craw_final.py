from bs4 import BeautifulSoup
import requests
import threading
import time
import string
import json
import re
import csv
from gensim.summarization import summarize
from gensim.summarization import keywords
import pandas
import pymongo
list_data = [['STT', 'Description', 'Summary_TextRank']]

second_url = ['/Hotels-g298085-Da_Nang-Hotels.html', '/Hotels-g298085-oa30-Da_Nang-Hotels.html',
              '/Hotels-g298085-oa60-Da_Nang-Hotels.html', '/Hotels-g298085-oa90-Da_Nang-Hotels.html',
              '/Hotels-g298085-oa120-Da_Nang-Hotels.html', '/Hotels-g298085-oa150-Da_Nang-Hotels.html',
              '/Hotels-g298085-oa180-Da_Nang-Hotels.html', '/Hotels-g298085-oa210-Da_Nang-Hotels.html',
              '/Hotels-g298085-oa240-Da_Nang-Hotels.html', '/Hotels-g298085-oa270-Da_Nang-Hotels.html']

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TravelComment_DEMO"]
propertyy = mydb["properties"]
destinate = mydb["destinations"]
post = mydb["posts"]
comments = mydb["comments"]

new_value = 1
def craw_url(true_url):
    try:
        page = requests.get(true_url).text

        soup = BeautifulSoup(page, 'lxml')

        # print(soup)
        # list_url = soup.find_all('a')
        # list_url = [a.get('href') for a in list_url]
        result = soup.find_all('a', attrs={"data-clicksource": "HotelName"})

        result = [item.get("href") for item in result]
        list_url = []
        accept_url = ['Hotel_Review']
        for url in result:
            if type(url) is str:
                if url.endswith(".html"):
                    for accept in accept_url:
                        if url.find(accept) != -1:
                            list_url.append(url)
        return list_url
    except BaseException as e:
        print(str(e))


list_Description = []


def craw_page_data(url):
    print(url)

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    # title = soup.get('title')
    id = soup.find(id='HEADING')
    name = id.text
    for des_name in destinate.find():
        if name == des_name['name']:
            return "abcxyz"

    # rate = soup.find('span', attrs={'class': 'ui_bubble_rating'})
    # total_rate = rate.get('class')[1]

    # review = soup.find_all('div', attrs={
    #     'class': 'ssr-init-26f'})
    # description = review[1].get('data-ssrev-handlers')
    # description = json.loads(description)
    #
    # description = description['load'][3]['locationDescription']
    description_first = soup.find_all('div', attrs={
        'class': 'cPQsENeY'})
    # print(description_first[0].text)
    description = description_first[0].text
    span_location = soup.find_all('span', attrs={'class': '_3ErVArsu jke2_wbp'})
    location = span_location[1].text
    proper = soup.find_all('div', attrs={
        'class': '_2rdvbNSg'})
    destination = {"name": name, "type": 'hotel','location': location}
    des = destinate.insert_one(destination)


    for i in range(len(proper)):
        myProper = {"destination_id": des.inserted_id, "name": proper[i].text}
        x = propertyy.insert_one(myProper)
        # print(myProper)
    myDescription = {"destination_id": des.inserted_id, "content": description}
    z = post.insert_one(myDescription)

    x = url.split("-")
    url_comment_first = ''
    for i in range(0, len(x) - 2, 1):
        url_comment_first = url_comment_first + x[i] + '-'
    # print(url_comment_first)
    list_comment_url = []
    page_num = 0
    for i in range(0, 7, 1):
        if page_num == 0:
            new_url = url_comment_first + x[len(x) - 2] + "-" + x[len(x) - 1]
            list_comment_url.append(new_url)
            page_num = page_num + 5

        else:
            new_url = url_comment_first + 'or' + str(page_num) + '-' + x[len(x) - 2] + "-" + x[len(x) - 1]
            list_comment_url.append(new_url)
            page_num = page_num + 5
    for i in list_comment_url:
        page_comment = requests.get(i).text
        soup_comment = BeautifulSoup(page_comment, 'html.parser')
        comment = soup_comment.find_all('div', attrs={
            'class': 'oETBfkHU'})
        # print(comment[2].text   cPQsENeY   )
        for i in range(0, len(comment), 1):
            true_comment = comment[i].find('q', attrs={'class': 'IRsGHoPm'})
            rate = comment[i].find('span', attrs={'class': 'ui_bubble_rating'})
            # for i in range(1,len(comment), 1):
            #     print(comment[i].text)
            total_rate = rate.get('class')[1]
            total_rate = total_rate.split('_')
            # print(true_comment.text)
            # print(total_rate[1])
            myComment = {"destination_id": des.inserted_id, "content": true_comment.text, "rating": total_rate[1]}
            z = comments.insert_one(myComment)

    return description

data = {'Description': [], 'Summary': []}
if __name__ == '__main__':
    root_url = 'https://www.tripadvisor.com'
    first_url = '/Hotels-g298085'
    third_url = '-Da_Nang-Hotels.html'
    handle_url = '-oa'
    number = 30
    blabla = 1
    while True:
        # main_url = second_url[num_url]
        true_url = root_url+first_url+handle_url+str(number)+third_url
        print(true_url)
        list_url = craw_url(true_url)
        # print(list_url)

        if len(data['Description']) == 50:
            break
        for item in list_url:
            try:
                if len(data['Description']) == 700:
                    break

                url_craw = root_url + item
                description = craw_page_data(url_craw)
                # print(description)
                # summary = summarize(description, word_count=50)
                # print(summary)
                if description != "abcxyz":
                    data['Description'].append(description)
                    # data['Summary'].append(summary)
                    # print(len(data['Description']))
                    print(blabla)
                    blabla = blabla + 1
                else:
                    print("Trung hotel")
            except BaseException as b:
                print(str(b))
                pass
        number = number + 30

    # df = pandas.DataFrame(data, columns=['Description', 'Summary'])
    # df.to_csv('Description.csv', index=False, header=True)
    # print("alo alo")
    # print(len(data['Description']))
