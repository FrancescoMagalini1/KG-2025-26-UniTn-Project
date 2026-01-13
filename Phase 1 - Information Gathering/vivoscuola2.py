import requests
import json
import re
import polars as pl
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

FOLDER = "./data/staging/"
PATH_SCRAPE = FOLDER + "vivoscuola.json"
PATH_CLEAN = FOLDER + "vivoscuola_clean.csv"
PATH_CLEAN_2 = FOLDER + "vivoscuola_clean2.csv"
PATH_SCHOOL_LINKS = FOLDER + "vivoscuola_school_links.csv"
PATH_STATS_TEMP = FOLDER + "vivoscuola_stats_temp.csv"
PATH_STATS = FOLDER + "vivoscuola_stats.json"


def get_data():
    DOMAIN = "https://www.vivoscuola.it"
    PATH = "/facetsearch/datatable_search/istituto_plesso/$PARENT_INSTITUTE$|viv_indirizzo|viv_plesso|municipality|phone|$MODAL_GEO$/extra_tipoistruzione_name____s|miurcode|legalstate|extra_adulti_name____s|extra_comune_name____s|typelocation/265"

    QUERY = {
        "draw": "6",
        "columns[0][data]": "0",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "1",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "2",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "3",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "4",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "false",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "5",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "false",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "order[0][column]": "1",
        "order[0][dir]": "desc",
        "order[1][column]": "2",
        "order[1][dir]": "desc",
        "start": "0",
        "length": "2000",
        "search[value]": "",
        "search[regex]": "false",
        "extra_tipoistruzione_name____s": "",
        "show": "10",
        "extra_comune_name____s": "",
        "typelocation": "",
        "simpleQuery": "",
        "undefined": "",
        "query": "",
        "miurcode": "",
        "legalstate_radio_btn": "",
        "legalstate": "",
        "extra_adulti_name____s": "",
        "_": "1763372720643",
    }

    cookies = {
        "cc_index_www.vivoscuola.it": '{"level":["necessary","analytics","targeting"],"revision":1,"data":null,"rfc_cookie":true}',
        "eZSESSID": "lqq5tufaokmncurrg4m47qk656",
        "X-IT-LB-ID": "itnlb.pr65w",
    }

    response = requests.get(DOMAIN + PATH, params=QUERY, cookies=cookies)
    data = response.json()
    with open(PATH_SCRAPE, "w") as f:
        json.dump(data, f, indent=4)


# 'istituto principale', 'scuola', 'tipo istituto', 'tipo gestione', 'dirigente', 'direttore',
# 'coordinatore pedagogico', 'indirizzo', 'comune', 'telefono', 'fax', 'email istituto', 'email dirigenza',
# 'email segreteria', 'sito web', 'codice miur', 'link istituto vivoscuola', 'entity'


def join_and_clean():
    with open(PATH_SCRAPE, "r") as f:
        data = json.load(f)
        headers = ["link istituto vivoscuola", "istituto principale"]
        values = []
        for item in data["data"]:
            link = re.findall(r"href=\"(.+?)\"", item[0])[0]
            name = re.findall(r">(.+?)</", item[0])[0]
            values.append([link, name])

        df_links = (
            pl.DataFrame(values, schema=headers, orient="row")
            .with_columns(pl.col("istituto principale").str.to_lowercase())
            .unique()
        )
        df = pl.read_csv(PATH_CLEAN, separator=";")
        df = (
            df.join(df_links, on="istituto principale", how="left")
            .with_columns(
                entity=pl.when(pl.col("scuola").is_null())
                .then(pl.lit("institute"))
                .otherwise(pl.lit("school"))
            )
            .sort("istituto principale", "scuola")
            .rename(
                {
                    "istituto principale": "main institute",
                    "scuola": "school",
                    "tipo istituto": "school type",
                    "tipo gestione": "administration type",
                    "dirigente": "manager",
                    "direttore": "director",
                    "coordinatore pedagogico": "educational coordinator",
                    "indirizzo": "address",
                    "comune": "municipality",
                    "telefono": "telephone",
                    "email istituto": "institute email",
                    "email dirigenza": "management email",
                    "email segreteria": "secretary's office email",
                    "sito web": "website",
                    "codice miur": "miur code",
                    "link istituto vivoscuola": "vivoscuola institute link",
                }
            )
        )
        df.write_csv(PATH_CLEAN_2, separator=";")


# 'main institute', 'school', 'school type', 'administration type', 'manager', 'director',
# 'educational coordinator', 'address', 'municipality', 'telephone', 'fax', 'institute email', 'management email',
# 'secretary's office email', 'website', 'miur code', 'vivoscuola institute link', 'entity'
def scrape_school_links():

    def parse_page(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", attrs={"id": "table-unita-scolastiche"}).find(
            "tbody"
        )
        values = []
        for tr in table.find_all("tr"):
            anchor = tr.find("td", attrs={"data-label": "Scuole"}).find("a")
            link = anchor.attrs.get("href")
            name = anchor.get_text(strip=True)
            values.append([url, name, "https://www.vivoscuola.it" + link])
        return values

    df = pl.read_csv(PATH_CLEAN_2, separator=";")
    df_links = (
        df.select("main institute", "vivoscuola institute link").unique().to_dicts()
    )
    values = []
    MAX_THREADS = 4
    print(f"Scraping {len(df_links)} page links...")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(parse_page, row["vivoscuola institute link"])
            for row in df_links
        ]
        for future in tqdm(as_completed(futures), total=len(df_links)):
            result = future.result()
            values += result
    df_school_links = pl.DataFrame(
        values,
        schema=["vivoscuola institute link", "name", "school link"],
        orient="row",
    ).with_columns(pl.col("name").str.to_lowercase())
    df_school_links.write_csv(PATH_SCHOOL_LINKS, separator=";")
    print("Done")


def scrape_api_ids():

    def parse_page_1(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        link = (
            soup.find("div", attrs={"class": "dropdown-menu"})
            .find("a", href=lambda x: x and "alunniclassi" in x)
            .attrs.get("href")
        )
        return [url, link]

    def parse_page_2(arg):
        url, link = arg
        response = requests.get("https://www.vivoscuola.it" + link)
        content = response.text
        match = re.findall(r"var provincecode = \"(\d+)\";", content)[0]
        return [url, match]

    school_links = pl.read_csv(PATH_SCHOOL_LINKS, separator=";").to_dicts()
    urls = [row["school link"] for row in school_links]
    MAX_THREADS = 3
    links = []
    print(f"Scraping {len(school_links)} page links...")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(parse_page_1, url) for url in urls]
        for future in tqdm(as_completed(futures), total=len(urls)):
            result = future.result()
            links.append(result)
    values = []
    print(f"Scraping {len(links)} stats IDs...")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(parse_page_2, arg) for arg in links]
        for future in tqdm(as_completed(futures), total=len(links)):
            result = future.result()
            values.append(result)

    df = pl.DataFrame(values, schema=["school link", "api id"], orient="row")
    df.write_csv(PATH_STATS_TEMP, separator=";")
    print("Done")


def scrape_school_stats():

    url_grades = (
        lambda id: f"https://istruzione.cloud.provincia.tn.it/services/sei/api/v1/institutes/gradingResults/{id}"
    )
    url_students = (
        lambda id: f"https://istruzione.cloud.provincia.tn.it/services/sei/api/v1/institutes/students/{id}"
    )

    def get_grades(d):
        api_id = d["api id"]
        url = url_grades(api_id)
        response = requests.get(url)
        content = response.json()
        if not content:
            d["grades"] = None
        else:
            d["grades"] = {
                "percentage admissions total": content[0]["percentualeAmmessiTotale"],
                "results": [
                    {"percentages": result["percentuali"], "name": result["etichetta"]}
                    for result in content[0]["esitiScrutini"]
                ],
            }
        return d

    def get_students(d):
        api_id = d["api id"]
        url = url_students(api_id)
        response = requests.get(url)
        content = response.json()

        if not content:
            d["students"] = None
        else:
            # print(content["alunniXClassiAnnoScolasticoCorrente"])
            d["students"] = {
                "current_students": [
                    {
                        "academic year": year["annoScolastico"],
                        "school year": year.get("annoDiCorso", 0),
                        "number of students": year["numeroAlunni"],
                        "number of classes": year["numeroClassi"],
                    }
                    for year in content["alunniXClassiAnnoScolasticoCorrente"]
                ],
            }
            if "alunniXClassiAnnoScolasticoPrecedente" in content:
                d["students"]["past_year_students"] = [
                    {
                        "academic year": year["annoScolastico"],
                        "school year": year.get("annoDiCorso", 0),
                        "number of students": year["numeroAlunni"],
                        "number of classes": year["numeroClassi"],
                    }
                    for year in content["alunniXClassiAnnoScolasticoPrecedente"]
                ]
            if "alunniXClassi2AnniScolasticiPrecedenti" in content:
                d["students"]["past_2years_students"] = [
                    {
                        "academic year": year["annoScolastico"],
                        "school year": year.get("annoDiCorso", 0),
                        "number of students": year["numeroAlunni"],
                        "number of classes": year["numeroClassi"],
                    }
                    for year in content["alunniXClassi2AnniScolasticiPrecedenti"]
                ]
        return d

    # "school link", "api id"
    entries = pl.read_csv(
        PATH_STATS_TEMP, separator=";", schema_overrides={"api id": pl.String}
    ).to_dicts()
    values = []
    MAX_THREADS = 4
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(get_grades, entry) for entry in entries]
        for future in tqdm(as_completed(futures), total=len(entries)):
            result = future.result()
            values.append(result)
    values2 = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(get_students, value) for value in values]
        for future in tqdm(as_completed(futures), total=len(values)):
            result = future.result()
            values2.append(result)
    with open(PATH_STATS, "w") as f:
        json.dump(values2, f, indent=4)
