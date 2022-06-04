from time import sleep
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib
from os.path import join, isdir, isfile, abspath, dirname, splitext, basename, split
from telegram import Bot
from os import makedirs
import os
from dotenv import load_dotenv
from telegram.error import RetryAfter

#Components:
# * Get List (x)
# * Compare List to Stored One to See if there are new ones (x)
# * Notify in Telegram (x)
#   * Automatically make a vote for it (x)
#   * Be able to specify only ones in Germany
# * Wrap everything into a continuously running thing in a Container (x)

DEFAULT_PATH="../data/turniere.csv"

def get_page_soup(url):
    '''
    Submits a request and returns the soup of the object;
    if 404, returns False
    '''
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
    response = requests.get(url, headers=ua)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup

def get_turnament_df():
    soup = get_page_soup("https://turniere.jugger.org/")
    turnaments = iter(soup.find(class_="table table-striped table-condensed").find_all("tr"))
    colnames = [i.text if i.text else "Liga" for i in next(turnaments).find_all("th")]
    all_turnaments = {k: [] for k in colnames+["Link", "Land"]}
    for turnament in turnaments:
        elems = [i.text for i in turnament.find_all("td")]
        href = "https://turniere.jugger.org/"+next(turnament.find_all("td")[1].children)["href"]
        country = next(turnament.find_all("td")[2].children)["title"]
        elems[4] = next(turnament.find_all("td")[4].children)["title"] if len(turnament.find_all("td")) >= 5 and len(turnament.find_all("td")[4]) else None
        if elems[0] == "Heute":
            elems[0] = datetime.now().date().strftime("%d.%m.%Y")
        for key, val in zip(all_turnaments.values(), elems+[href,country]):
            key.append(val)
    return pd.DataFrame(all_turnaments)

def save_turnament_df(df, path=DEFAULT_PATH):
    if not isdir(dirname(path)):
        makedirs(dirname(path))
    df.to_csv(path)

def load_turnament_df(path=DEFAULT_PATH):
    if not isdir(dirname(path)):
        makedirs(dirname(path))
    return pd.read_csv(path, index_col=0) if isfile(path) else None


def send_message(text, chat_id, tgram_token, file=None, filename="", reply_markup=None):
    text = text.replace("_", "-")
    text = urllib.parse.quote_plus(text)
    url = f"https://api.telegram.org/bot{tgram_token}/sendMessage?text={text}&chat_id={chat_id}&parse_mode=Markdown"
    if reply_markup: url += "&reply_markup={reply_markup}"
    kwargs = {'files': {'document': (filename, file)}} if filename and file else {}
    response = requests.get(url, **kwargs)
    return response.content.decode("UTF-8")


def poll(bot, chat_id, text="Ja?"):
    questions = ["Jau!", "Maybe", "Mimimimi"]
    for _ in range(10):
        try:
            return bot.send_poll(
                chat_id,
                text,
                questions,
                is_anonymous=False,
                allows_multiple_answers=False,
                timeout=10,
            )
        except RetryAfter as e:
            if e.retry_after < 500:
                print(f"sleeping for {e.retry_after}s")
                sleep(e.retry_after+1)
    raise RetryAfter

def get_new_turnaments(turniere, path=DEFAULT_PATH):
    old_turniere = load_turnament_df(path)
    if old_turniere is None:
        return turniere
    df_all = turniere.merge(old_turniere.drop_duplicates(), on=['Datum', 'Turnier'], how='left', indicator=True)
    df_all = df_all[df_all['_merge'] == 'left_only']
    df_all = df_all.drop(columns=[i for i in df_all.columns if i.endswith("_y")] + ["_merge"])
    df_all = df_all.rename(columns={k: k.replace("_x", "") for k in df_all.columns})
    return df_all

def load_defaults(data_dir):
    if not os.getenv("GROUP_ID") or not os.getenv("TGRAM_TOKEN") and isfile(join(data_dir, ".env")):
        load_dotenv(join(data_dir, ".env"))
    group_id = int(os.environ["GROUP_ID"])
    tgram_token = os.environ["TGRAM_TOKEN"]
    return group_id, tgram_token


def main(data_dir, bot, group_id, tgram_token):
    turniere = get_turnament_df()
    new_turniere = get_new_turnaments(turniere, join(data_dir, "turniere.csv"))
    if len(new_turniere):
        for new_turnier in new_turniere.iterrows():
            message = "\n".join([f"{k}: {v}" for k, v in new_turnier[1].to_dict().items()])
            send_message(message, group_id, tgram_token)
            poll(bot, group_id, text="Dabei?")
        save_turnament_df(turniere, join(data_dir, "turniere.csv"))


if __name__ == "__main__":
    data_dir = join("..", "data")
    group_id, tgram_token = load_defaults(data_dir)
    bot = Bot(tgram_token)
    try:
        main(data_dir, bot, group_id, tgram_token)
    except Exception as e:
        send_message(str(e), group_id, tgram_token)


