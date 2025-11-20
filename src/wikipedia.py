import polars as pl
from bs4 import BeautifulSoup
import requests
import re
import time
import numpy as np
from functools import reduce


MAIN_LINK = "https://it.wikipedia.org/wiki/Comuni_del_Trentino-Alto_Adige"
DOMAIN = "https://it.wikipedia.org"
SCRAPE_PATH = "./data/wikipedia.csv"
CLEAN_PATH = "./data/wikipedia_clean.csv"


def scrape():
    http_headers = {"User-agent": "Mozilla/5.0"}
    response = requests.get(MAIN_LINK, headers=http_headers)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", attrs={"class": "wikitable"})
    headers = []
    for col in table.find_all("th"):
        text = col.get_text()
        text = re.sub(r"\[\d\]", "", text).replace("\n", "").lower()
        headers.append(text)
    # 'comune', 'provincia autonoma', 'popolazione', 'superficie', 'densità', 'altitudine', 'link', 'codice postale', 'sito',
    # 'comuni confinanti', 'lat', 'lon'
    headers.extend(
        ["link", "codice postale", "istat", "sito", "comuni confinanti", "lat", "lon"]
    )
    values = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if not len(cells):
            continue
        anchor = cells[0].find("a")
        link = DOMAIN + anchor.attrs.get("href")
        content = [re.sub(r"[\n\xa0,]", "", cell.get_text()).lower() for cell in cells]
        content.append(link)
        if content[1] == "trento":
            response = requests.get(link, headers=http_headers)
            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table", attrs={"class": "infobox"})
            lat = table.find(class_="latitude").get_text()
            lon = table.find(class_="longitude").get_text()
            postal_code = (
                table.find("a", string=re.compile("postale", re.I))
                .find_parent("tr")
                .find("td")
                .get_text()
                .replace("\n", "")
            )
            istat = (
                table.find("a", string=re.compile("istat", re.I))
                .find_parent("tr")
                .find("td")
                .get_text()
                .replace("\n", "")
            )
            istat = re.sub(r"\[\d\]", "", istat)
            website = table.find(
                "a", string=re.compile("sito istituzionale", re.I)
            ).attrs.get("href")
            anchors = (
                table.find("th", string=re.compile("comuni confinanti", re.I))
                .find_parent("tr")
                .find_all("a")
            )
            border_municipalities = "|".join(
                [DOMAIN + a.attrs.get("href") for a in anchors]
            )
            content.extend(
                [postal_code, istat, website, border_municipalities, lat, lon]
            )

            values.append(content)
            # sleep in order to avoid rate limiting
            time.sleep(0.25)

    df = pl.DataFrame(values, schema=headers, orient="row")
    df.write_csv(SCRAPE_PATH, separator=";")


def parse_coords(s: str):
    matches = enumerate(re.findall(r"(\d+(?:\.\d+)?)[°′″]", s))
    val = reduce(lambda acc, val: acc + (float(val[1]) / (60 ** val[0])), matches, 0)
    return val


def clean():
    df = pl.read_csv(SCRAPE_PATH, separator=";")
    unique_links = set(df.select(pl.col("link")).unique().to_numpy().flatten().tolist())
    df = df.with_columns(
        pl.col("comuni confinanti")
        .str.split("|")
        .list.filter(pl.element().is_in(unique_links))
        .list.join("|"),
        lat_n=pl.col("lat").map_elements(parse_coords, return_dtype=pl.Float64),
        lon_n=pl.col("lon").map_elements(parse_coords, return_dtype=pl.Float64),
    )
    df.write_csv(CLEAN_PATH, separator=";")
