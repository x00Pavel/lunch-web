from lunch_web import (links, names)


def parse_pages(data):
    menus = list()
    for rest in data:
        short_name = rest["name"]
        result = dict()
        result["menu"] = dict()
        result['name'] = names[short_name]
        result['short_name'] = short_name
        result['url'] = links[short_name]

        if short_name == "portoriko":
            result["menu"] = __parse_portoriko(rest["page"])
        elif short_name == "jp":
            result["menu"], result["week_menu"] = __parse_jp(rest["page"])
        # elif rest["name"] == "asport":
        #     mils = __parse_asport(rest["page"])

        menus.append(result)
    return menus


def __parse_jp(page):
    result = dict()
    denni = page.find_all("div", class_="denni-menu")[0]
    for n in denni.find_all("h2"):
        day = n.get_text()
        result[day] = list()
        table = n.find_next_siblings()[0]

        for tr in table.find_all("tr"):
            name = tr.find("div", class_="text").get_text()
            price = tr.find("div", class_="price").get_text()
            result[day].append(f"{name} {price}")
    week_menu = page.find("div", class_="tydenni-menu")
    return (result, week_menu)


def __parse_portoriko(page):
    result = dict()
    div = page.find("div", class_="print-not")
    for n in div.find_all("h2"):
        day = n.get_text()
        result[day] = list()
        table = n.find_next_siblings()[0]
        for x in table.find_all("td", class_="middle-menu"):
            if len(x.get_text(strip=True)) != 0:
                result[day].append(x.get_text())

    return result


def __parse_asport(page):
    return []
