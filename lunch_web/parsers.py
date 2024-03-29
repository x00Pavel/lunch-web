from contextlib import suppress


def parse_na_purkynce(page):
    result = dict()

    for item in page.find_all("div", class_="content"):
        with suppress(AttributeError):
            day = item.find("h2").get_text()
            soup = item.find("tr", class_="soup")
            result[day] = [{"name": soup.find("td", class_="food").get_text().strip(),
                            "price": "Included in menu"}]
            for tr in item.find_all("tr", class_="main"):
                name = tr.find("td", class_="food").get_text().strip()
                price = tr.find("td", class_="prize").get_text()
                result[day].append({"name": name, "price": price})
    return result


def parse_padagali(page):
    result = dict()
    content = page.find("div", {"class": "glf-mor-restaurant-menu-wrapper"})
    content = content.find_all("div", {"class": "glf-mor-restaurant-menu-category"})
    for c in content:
        heading = c.find("h3").get_text(strip=True)
        result[heading] = list()
        menu = c.find_all("div", {"class": "glf-mor-restaurant-menu-item-inner"})
        for m in menu:
            name = m.find("h5", {"class": "glf-mor-restaurant-menu-item-name"}).get_text(strip=True)
            description = m.find("div", {"class": "glf-mor-restaurant-menu-item-description"})
            if description is not None:
                description = description.get_text(strip=True)
                name = f"{name} ({description})"
            price = m.find("span", {"class": "price"}).get_text(strip=True)
            result[heading].append({"name": name, "price": price})
    return result


def parse_u3opic(page):
    result = dict()
    denni = page.find_all("div", {"class": "row menu-items"})[0]
    items = denni.find_all("div", {"class": "menu-item col-sm-12 col-xs-12 starter"})
    for o in range(0, len(items), 5):
        day = items[o].find("h2").text
        if "sobota" in day.lower():
            break
        result[day] = list()
        for i in range(o + 1, o + 5):
            if i <= len(items) - 2:
                item = items[i]
                price = item.find("span", class_="price")
                if price is not None:
                    price = price.get_text(strip=True)
                name = item.find("h4").get_text(strip=True)
                result[day].append({"name": name, "price": price})
    return result


def parse_jp(page):
    result = dict()
    denni = page.find_all("div", class_="denni-menu")[0]
    for n in denni.find_all("h2"):
        day = n.get_text()
        result[day] = list()
        table = n.find_next_siblings()[0]

        for tr in table.find_all("tr"):
            name = tr.find("div", class_="text").get_text().strip()
            price = tr.find("div", class_="price").get_text().strip()
            result[day].append({"name": name, "price": price})
    week_menu = page.find("div", class_="tydenni-menu")
    return (result, str(week_menu))


def parse_portoriko(page):
    result = dict()
    div = page.find("div", class_="print-not")
    for n in div.find_all("h2"):
        day = n.get_text()
        result[day] = list()
        table = n.find_next_siblings()[0]
        for x in table.find_all("td", class_="middle-menu"):
            if len(x.get_text(strip=True)) != 0:
                txt = x.get_text()
                result[day].append(
                    {"name": " ".join(txt.split()[0:-1:1]),
                     "price": txt.split()[-1]})
    return result


def parse_asport(page):
    result = dict()
    days = ("pondeli", 'utery', 'streda', 'ctvrtek', 'patek')
    for day in days:
        section = page.find("section", id=f"menu-{day}")
        h2 = section.find("h2", class_="tydenni-menu").get_text()
        tmp = list()
        table = section.find("table", class_="tydenni-menu")
        for tr in table.find_all('tr'):
            polozka = tr.find('td', class_="polozka").get_text().strip()
            cena = tr.find('td', class_="cena").get_text().strip()
            if polozka != "":
                tmp.append({"name": polozka, "price": cena})
        if tmp:
            result[h2] = tmp
    return result


def parse_nepal(page):
    result = dict()
    table = page.find("div", class_="the_content_wrapper").find_all("table")[2]
    rows = table.find_all("tr")
    day_stack = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "end"]

    week_day = None
    for row in rows:
        for column in row.find_all("td"):
            day = day_stack[0]
            column_text = column.get_text().strip()
            if day in column_text:
                week_day = column_text
                result[week_day] = list()
                day_stack.pop(0)
            elif "" != column_text:
                sibling = column.find_next_siblings()[0]
                price = sibling.get_text()
                result[week_day].append(
                    {"type": None, "name": column_text, "price": price})
                break
    return result


def parse_kanas(pages: dict()):
    result = dict()
    for day, page in pages.items():
        result[day] = list()
        table = page.find("div", {"id": "tab1"}, class_="tab_content")
        polozky = list(table.find_all("div", class_="polozka"))
        for p in polozky:
            name = p.find("span", class_="jidlo").get_text().strip()
            price = p.find("span", class_="cena").get_text().strip()
            result[day].append({"name": name, "price": price})
        
    return result
