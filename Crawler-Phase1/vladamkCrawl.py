import requests as req
from bs4 import BeautifulSoup
import datetime
import csv
import re
import pandas as pd

mk_numbers_string = ['едно', 'прв', 'еден', 'една', 'два', 'две', 'двајца', 'три', 'тројца', 'четири', 'четворица',
                     'пет',
                     'петмина', 'шест',
                     'седум', 'осум', 'девет', 'десет', 'единаесет']
mk_numbers_int = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10, 11]
fatalKey = ['почина', 'починаa', 'починаа', 'починати', 'починато', 'смртен', 'починале', 'починало', 'починат',
            'почината',
            'починал', 'починала']
recoveryKey = ['оздравени', 'оздравено', 'оздравен', 'излекувани', 'излечени', 'испишани', 'заминуваат']
infectedBeforeKey = ['дијагностицирани', 'потврдени']
infected_after_number_key = ['нови случаи', 'нов случај', 'нови пациенти', 'позитивни']
infected_separate_keys = ['нови', 'нов', 'позитивни']
testing = ['тестирања']
total = ['вкупно', 'вкупната']
Covid = ['КОВИД-19', 'коронавирус']
stop_keys = ['инфективната клиника', 'клиниката за инфективни', '8 септември']
dates_input = []
post_number_start = 20635
post_number_end = 21400
base_url = "https://vlada.mk/node/"
column_names = ['Date', 'Infected', 'Fatal', 'Cured']
df = pd.DataFrame(columns=column_names)


def check_if_string_is_number(string):
    return string.isnumeric()


def is_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def get_date(string_dates):
    for date in string_dates:
        parts = date.text.split(' ')
        for part in parts:
            if is_date(part):
                return part


def check_word_in_sentences(text, key_word):
    sentences = re.split(r'[.\n]+', text)
    for sentence in sentences:
        if sentence.lower().find(key_word.lower()) != -1:
            return sentence.lower()


def get_sentences_with_words(text, key_words):
    sentences = []
    for div in text:
        for i in range(0, len(key_words)):
            sentences_with_words = check_word_in_sentences(div.text, key_words[i])
            if sentences_with_words is not None:
                sentences.append(sentences_with_words)
    return sentences


def get_data_for(text, keys, keys_for_sentences):
    sentences = get_sentences_with_words(text, keys_for_sentences)
    for sentence in sentences:
        sub_sentences = re.split(r'[,\n]+', sentence)
        for sub_sentence in sub_sentences:
            words = sub_sentence.split(' ')
            words = ["asd", "asd"] + words + ["asd", "asd"]
            for k in range(2, len(words) - 2):
                for i in range(0, len(keys)):
                    if (words[k + 1] == keys[i] and check_if_string_is_number(words[k])) \
                            or (words[k - 1] == keys[i] and check_if_string_is_number(words[k])) \
                            or (words[k + 1] == keys[i] and words[k] in mk_numbers_string) \
                            or (words[k - 1] == keys[i] and words[k] in mk_numbers_string) \
                            or (words[k + 2] == keys[i] and check_if_string_is_number(words[k])) \
                            or (words[k + 2] == keys[i] and words[k] in mk_numbers_string) \
                            or (words[k - 2] == keys[i] and words[k] in mk_numbers_string) \
                            or (words[k - 2] == keys[i] and check_if_string_is_number(words[k])):
                        if words[k] in mk_numbers_string:
                            index = mk_numbers_string.index(words[k])
                            return mk_numbers_int[index]
                        return int(words[k])
    return 0


def covid_post(post):
    sentences = get_sentences_with_words(post, Covid)
    if not sentences:
        return False
    else:
        return True


def get_info_about_post(article, dates):
    global df
    date = get_date(dates)
    infected = get_data_for(article, infected_separate_keys, infected_after_number_key)
    fatal = get_data_for(article, fatalKey, fatalKey)
    if fatal > 10:
        fatal = 0
    cured = get_data_for(article, recoveryKey, recoveryKey)
    if date not in dates_input and infected != 0:
        dates_input.append(date)
        df = df.append({'Date': date, 'Infected': infected, 'Fatal': fatal, 'Cured': cured}, ignore_index=True)
        print("Written to DataFrame: Date {0}, Infected {1}, Fatal {2}, Cured {3}".format(date, infected, fatal, cured))


def soup(url):
    for j in range(post_number_start, post_number_end):
        if j % 100 == 0:
            print(j)
        post_url = url + str(j)
        res = req.get(post_url)
        soup = BeautifulSoup(res.text, "lxml")
        dates = soup.find_all('div', {'class': 'submitted_date'})
        article = soup.find_all("section", {'id': 'main'})
        if covid_post(article):
            get_info_about_post(article, dates)
    df.to_csv('dataVlada.csv')


if __name__ == "__main__":
    soup(base_url)
    # Testing one post
    # res = req.get(base_url + "20986")
    # soup = BeautifulSoup(res.text, "lxml")
    # dates = soup.find_all('div', {'class': 'submitted_date'})
    # article = soup.find_all("section", {'id': 'main'})
    # if covid_post(article):
    #     get_info_about_post(article, dates)

# OUTPUT
# Written to DataFrame: Date 21.03.2020, Infected 9, Fatal 0, Cured 0
# Written to DataFrame: Date 22.03.2020, Infected 29, Fatal 1, Cured 0
# Written to DataFrame: Date 23.03.2020, Infected 22, Fatal 0, Cured 0
# Written to DataFrame: Date 24.03.2020, Infected 12, Fatal 2, Cured 0
# 20700
# Written to DataFrame: Date 25.03.2020, Infected 29, Fatal 1, Cured 0
# Written to DataFrame: Date 26.03.2020, Infected 24, Fatal 3, Cured 3
# Written to DataFrame: Date 27.03.2020, Infected 18, Fatal 3, Cured 3
# Written to DataFrame: Date 29.03.2020, Infected 18, Fatal 2, Cured 0
# 20800
# Written to DataFrame: Date 30.03.2020, Infected 26, Fatal 1, Cured 9
# Written to DataFrame: Date 31.03.2020, Infected 44, Fatal 2, Cured 0
# Written to DataFrame: Date 01.04.2020, Infected 25, Fatal 1, Cured 5
# Written to DataFrame: Date 02.04.2020, Infected 30, Fatal 0, Cured 0
# Written to DataFrame: Date 03.04.2020, Infected 46, Fatal 2, Cured 3
# Written to DataFrame: Date 05.04.2020, Infected 72, Fatal 0, Cured 3
# Written to DataFrame: Date 06.04.2020, Infected 15, Fatal 3, Cured 4
# 20900
# Written to DataFrame: Date 07.04.2020, Infected 29, Fatal 5, Cured 0
# Written to DataFrame: Date 08.04.2020, Infected 18, Fatal 2, Cured 5
# Written to DataFrame: Date 09.04.2020, Infected 46, Fatal 0, Cured 0
# Written to DataFrame: Date 10.04.2020, Infected 48, Fatal 0, Cured 3
# 21000
# Written to DataFrame: Date 12.04.2020, Infected 68, Fatal 0, Cured 0
# Written to DataFrame: Date 13.04.2020, Infected 26, Fatal 4, Cured 3
# Written to DataFrame: Date 14.04.2020, Infected 54, Fatal 6, Cured 42
# Written to DataFrame: Date 15.04.2020, Infected 66, Fatal 1, Cured 12
# Written to DataFrame: Date 16.04.2020, Infected 107, Fatal 1, Cured 1
# Written to DataFrame: Date 17.04.2020, Infected 36, Fatal 3, Cured 18
# Written to DataFrame: Date 18.04.2020, Infected 53, Fatal 0, Cured 25
# 21100
# Written to DataFrame: Date 19.04.2020, Infected 37, Fatal 2, Cured 15
# Written to DataFrame: Date 20.04.2020, Infected 18, Fatal 3, Cured 21
# Written to DataFrame: Date 21.04.2020, Infected 7, Fatal 1, Cured 24
# Written to DataFrame: Date 22.04.2020, Infected 28, Fatal 1, Cured 48
# Written to DataFrame: Date 23.04.2020, Infected 41, Fatal 0, Cured 29
# Written to DataFrame: Date 24.04.2020, Infected 26, Fatal 1, Cured 36
# Written to DataFrame: Date 25.04.2020, Infected 41, Fatal 2, Cured 37
# Written to DataFrame: Date 26.04.2020, Infected 19, Fatal 2, Cured 126
# Written to DataFrame: Date 27.04.2020, Infected 13, Fatal 4, Cured 53
# Written to DataFrame: Date 28.04.2020, Infected 22, Fatal 6, Cured 36
# 21200
# Written to DataFrame: Date 29.04.2020, Infected 21, Fatal 2, Cured 38
# Written to DataFrame: Date 30.04.2020, Infected 23, Fatal 4, Cured 111
# Written to DataFrame: Date 01.05.2020, Infected 29, Fatal 4, Cured 69
# Written to DataFrame: Date 02.05.2020, Infected 15, Fatal 1, Cured 45
# Written to DataFrame: Date 03.05.2020, Infected 5, Fatal 2, Cured 95
# Written to DataFrame: Date 04.05.2020, Infected 7, Fatal 1, Cured 47
# Written to DataFrame: Date 05.05.2020, Infected 8, Fatal 1, Cured 21
# 21300
# Written to DataFrame: Date 06.05.2020, Infected 13, Fatal 2, Cured 44
# Written to DataFrame: Date 07.05.2020, Infected 33, Fatal 0, Cured 22
# Written to DataFrame: Date 08.05.2020, Infected 14, Fatal 1, Cured 20
# Written to DataFrame: Date 09.05.2020, Infected 36, Fatal 1, Cured 13
# Written to DataFrame: Date 11.05.2020, Infected 22, Fatal 0, Cured 64
# Written to DataFrame: Date 12.05.2020, Infected 10, Fatal 1, Cured 5
#
# Process finished with exit code 0
