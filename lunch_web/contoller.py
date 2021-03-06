from os import unlink
from os.path import exists, abspath, dirname
from lunch_web import parsers, log, TIME_FORMAT
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from json import load

# FIXME: set absolute path to files in the root of the module
MENUS_JSON = "menus.json"
RESTAURANTS_JSON = f"{dirname(abspath(__file__))}/restaurants.json"


def thread_work(vals):
    """Worker for parsing menu from one restaurant

    :param vals: values for the restaurant (short name, link, full name)
    :type vals: list
    :return: parsed page
    :rtype: dict
    """
    name = vals[0]
    url = vals[1]["url"]
    content = requests.get(url)
    result = {'short_name': name, "name": vals[1]["full_name"]}

    # U 3 Opic has specific encoding, so need to decode in specific way.
    # Encoding is set manually based on charset of original site
    if name == "u3opic":
        content.encoding = "windows-1250"
    page = BeautifulSoup(content.text, "html.parser",
                            from_encoding=content.encoding)
    if name == "portoriko":
        result["menu"] = parsers.parse_portoriko(page)
    elif name == "jp":
        result["menu"], result["week_menu"] = parsers.parse_jp(page)
    elif name == "asport":
        result["menu"] = parsers.parse_asport(page)
    elif name == "nepal":
        result["menu"] = parsers.parse_nepal(page)
    elif name == "u3opic":
        result["menu"] = parsers.parse_u3opic(page)
    elif name == "padagali":
        result["menu"] = parsers.parse_padagali(page)

    return result


def get_menu(date):
    cache = True
    results = load_menu(date)
    if results is None:
        cache = False
        with open(RESTAURANTS_JSON, "r") as f:
            rests = load(f)

        with ThreadPoolExecutor(max_workers=len(rests.keys())) as exec:
            results = list(exec.map(thread_work, list(rests.items())))
        update_menu(results, date)

    # FIXME: change return type of this function to remove
    return (results, cache)


def load_menu(date):
    if not exists(MENUS_JSON):
        log.warning("Menus cache doesn't exists")
        return None
    with open(MENUS_JSON, "r") as f:
        cache = json.load(f)

    start = datetime.strptime(cache["start"], TIME_FORMAT)
    end = datetime.strptime(cache["end"], TIME_FORMAT)
    if start <= date <= end:
        log.info("Menus are loaded from the cache")
        return cache["menus"]

    log.warning("Menus cache is outdated. Need to create a new one")
    return None


def update_menu(menus, date):
    start = date.strftime(TIME_FORMAT)
    end = date + timedelta(days=(6 - date.weekday()))
    end = end.strftime(TIME_FORMAT)
    cache = {"start": start, "end": end, "menus": menus}
    try:
        with open(MENUS_JSON, "w") as f:
            json.dump(cache, f)
        log.info("Cache is updated")
    except:
        if exists(MENUS_JSON):
            unlink(MENUS_JSON)
        log.error("Cache is not updated")
        raise
