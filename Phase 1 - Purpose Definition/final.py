import polars as pl
import json
import re

STAGING_FOLDER = "./data/staging/"
FINAL_FOLDER = "./data/final/"

WIKIPEDIA = STAGING_FOLDER + "wikipedia_clean.csv"
VIVOSCUOLA = STAGING_FOLDER + "vivoscuola_clean2.csv"
MISALIGNED_MUNICIPALITIES = STAGING_FOLDER + "misaligned_municipalities.csv"
PATH_SCHOOL_LINKS = STAGING_FOLDER + "vivoscuola_school_links.csv"
VIVOSCUOLA_FINAL = FINAL_FOLDER + "vivoscuola_final.csv"
WIKIPEDIA_FINAL = FINAL_FOLDER + "wikipedia.csv"
INSTITUTES_FINAL = FINAL_FOLDER + "institutes.csv"
SCHOOLS_FINAL = FINAL_FOLDER + "schools.csv"
STATS = STAGING_FOLDER + "vivoscuola_stats.json"
AVERAGE_ADMISSION_RATES = FINAL_FOLDER + "average_admission_rates.csv"
ADMISSION_RATES = FINAL_FOLDER + "admission_rates.csv"
STUDENTS = FINAL_FOLDER + "students.csv"
MIUR_CODE_CHECK = FINAL_FOLDER + "miur code check.csv"
STATISTICS = FINAL_FOLDER + "statistics.csv"


def municipality_join_attempt():
    df = pl.read_csv(VIVOSCUOLA, separator=";")
    municipalities = pl.read_csv(WIKIPEDIA, separator=";").select(
        "municipality", "wikipedia link"
    )
    df = df.join(municipalities, on="municipality", how="left")
    errors = (
        df.filter(pl.col("wikipedia link").is_null())
        .select("municipality")
        .unique()
        .write_csv(MISALIGNED_MUNICIPALITIES, separator=";")
    )


def schools_join_data():
    df = pl.read_csv(VIVOSCUOLA, separator=";")
    municipalities = pl.read_csv(WIKIPEDIA, separator=";").select(
        "municipality", "wikipedia link"
    )
    df = df.with_columns(
        pl.col("municipality")
        .str.replace("e'", "é")
        .str.replace("contá", "contà")
        .str.replace("ruffré - mendola", "ruffré-mendola")
        .str.replace("soraga", "soraga di fassa")
    )
    df = df.with_columns(
        municipality=pl.when(pl.col("municipality").str.contains(" - "))
        .then(pl.col("municipality").str.split(" - ").list.first())
        .otherwise(pl.col("municipality"))
    )
    df = df.join(municipalities, on="municipality", how="left").rename(
        {"wikipedia link": "wikipedia municipality link"}
    )
    errors = (
        df.filter(pl.col("wikipedia municipality link").is_null())
        .select("municipality")
        .unique()
    )
    print(errors)
    school_links = pl.read_csv(PATH_SCHOOL_LINKS, separator=";").rename(
        {"name": "school", "school link": "vivoscuola school link"}
    )
    df = df.with_columns(pl.col("school").str.strip_chars())
    df = df.join(school_links, on=["vivoscuola institute link", "school"], how="left")
    errors = df.filter(
        pl.col("vivoscuola school link").is_null() & pl.col("school").is_not_null()
    )
    print(errors)
    df.write_csv(VIVOSCUOLA_FINAL, separator=";")


def save_final_files():
    df = pl.read_csv(VIVOSCUOLA_FINAL, separator=";")
    df.filter(pl.col("entity") == "institute").select(
        [
            "main institute",
            "institute type",
            "administration type",
            "manager",
            "director",
            "educational coordinator",
            "address",
            "municipality",
            "telephone",
            "fax",
            "institute email",
            "management email",
            "secretary's office email",
            "website",
            "miur code",
            "vivoscuola institute link",
            "wikipedia municipality link",
        ]
    ).write_csv(INSTITUTES_FINAL, separator=";")
    df.filter(pl.col("entity") == "school").select(
        [
            "school",
            "administration type",
            "manager",
            "director",
            "educational coordinator",
            "address",
            "municipality",
            "telephone",
            "fax",
            "institute email",
            "management email",
            "secretary's office email",
            "website",
            "miur code",
            "vivoscuola institute link",
            "wikipedia municipality link",
            "vivoscuola school link",
        ]
    ).write_csv(SCHOOLS_FINAL, separator=";")
    pl.read_csv(WIKIPEDIA, separator=";").write_csv(WIKIPEDIA_FINAL, separator=";")


def clean_stats():
    with open(STATS, "r") as f:
        data = json.load(f)
        admission_rates = []
        n_students = []
        admission_rates_list = []
        for row in data:
            school_link = row["school link"]
            grades = row["grades"]
            students = row["students"]
            if grades:
                admission_rates.append(
                    [school_link, grades["percentage admissions total"]]
                )
                for entry in grades["results"]:
                    percentages = entry["percentages"]
                    name = re.findall(r"^Amessi (\d+)\/\d+$", entry["name"])
                    if len(name):
                        academic_year = int(name[0])
                        academic_year = f"{academic_year}/{academic_year+1}"
                        for school_year, percentage in enumerate(percentages, start=1):
                            admission_rates_list.append(
                                [school_link, academic_year, school_year, percentage]
                            )

            if students:
                entries = students["current_students"]
                if "past_year_students" in students:
                    entries += students["past_year_students"]
                if "past_2years_students" in students:
                    entries += students["past_2years_students"]

                for entry in entries:
                    academic_year = re.findall(r"^(\d+)\/\d+$", entry["academic year"])[
                        0
                    ]
                    academic_year = int(academic_year)
                    academic_year = f"{academic_year}/{academic_year+1}"
                    n_students.append(
                        [
                            school_link,
                            academic_year,
                            entry["school year"],
                            entry["number of students"],
                            entry["number of classes"],
                        ]
                    )
            pl.DataFrame(
                admission_rates,
                schema=["vivoscuola school link", "admission rate"],
                orient="row",
            ).write_csv(AVERAGE_ADMISSION_RATES, separator=";")
            pl.DataFrame(
                admission_rates_list,
                schema=[
                    "vivoscuola school link",
                    "academic year",
                    "school year",
                    "admission rate",
                ],
                orient="row",
            ).write_csv(ADMISSION_RATES, separator=";")
            pl.DataFrame(
                n_students,
                schema=[
                    "vivoscuola school link",
                    "academic year",
                    "school year",
                    "number of students",
                    "number of classes",
                ],
                orient="row",
            ).write_csv(STUDENTS, separator=";")


def add_admission_rates():
    df = pl.read_csv(
        SCHOOLS_FINAL, separator=";", schema_overrides={"telephone": pl.String}
    )
    admission_rates = pl.read_csv(AVERAGE_ADMISSION_RATES, separator=";").filter(
        pl.col("admission rate") != 0
    )
    df.join(admission_rates, on="vivoscuola school link", how="left").write_csv(
        SCHOOLS_FINAL, separator=";"
    )


def general_explore():
    df = pl.read_csv(VIVOSCUOLA_FINAL, separator=";")
    df_s = df.filter(pl.col("entity") == "school")
    df_i = df.filter(pl.col("entity") == "institute")

    print("schools", df_s.shape)
    print(df_s.null_count().to_dicts())
    print("institute", df_i.shape)
    print(df_i.null_count().to_dicts())
    print("\n\n")
    cols_to_check = [
        "administration type",
        "manager",
        "director",
        "educational coordinator",
        "address",
        "municipality",
        "telephone",
        "fax",
        "institute email",
        "management email",
        "secretary's office email",
        "website",
        "miur code",
    ]

    df_dup = df.group_by("main institute").agg(pl.col(cols_to_check).n_unique())
    long = df_dup.unpivot(
        index="main institute", variable_name="column", value_name="n_unique"
    )
    summary = long.group_by("column").agg(
        (pl.col("n_unique") > 1).any().alias("has_inconsistency")
    )
    print(summary.filter(pl.col("has_inconsistency") == False))
    print(summary.filter(pl.col("has_inconsistency") == True))


def focused_explore(col_name: str):
    df = pl.read_csv(VIVOSCUOLA_FINAL, separator=";")
    df = (
        df.select("main institute", col_name)
        .with_columns(count=pl.col(col_name).n_unique().over("main institute"))
        .filter(pl.col("count") > 1)
    )
    print(df)


def miur_code_explore():
    df = pl.read_csv(VIVOSCUOLA_FINAL, separator=";").select(
        "main institute", "school", "miur code", "entity", "address"
    )
    df_g = (
        df.select("main institute", "miur code")
        .group_by("main institute")
        .agg("miur code")
        .with_columns(
            pl.col("miur code")
            .list.filter(pl.element().is_not_null())
            .list.unique()
            .alias("miur code list")
        )
        .select(pl.exclude("miur code"))
    )
    df_s = (
        df.select("main institute", "entity")
        .filter(pl.col("entity") == "school")
        .group_by("main institute")
        .agg(pl.col("entity").len().alias("school count"))
    )
    df = (
        df.join(df_g, on="main institute", how="left")
        .join(df_s, on="main institute", how="left")
        .with_columns(
            (
                (pl.col("school count") - pl.col("miur code list").list.len()).alias(
                    "check"
                )
            ),
            (pl.col("miur code list").list.join("|")),
        )
    )
    df.write_csv(MIUR_CODE_CHECK, separator=";")


def clean_telephone():
    df = pl.read_csv(VIVOSCUOLA_FINAL, separator=";").with_columns(
        pl.col("telephone").str.replace_all(r"[\/\- ]", "")
    )
    df.write_csv(VIVOSCUOLA_FINAL, separator=";")


def fix_directors():
    pl.read_csv(VIVOSCUOLA_FINAL, separator=";").with_columns(
        pl.col("director").fill_null(strategy="backward").over("main institute")
    ).write_csv(VIVOSCUOLA_FINAL, separator=";")


def final_cleanup():
    df = pl.read_csv(
        VIVOSCUOLA_FINAL, separator=";", schema_overrides={"telephone": pl.String}
    )
    df.filter(pl.col("entity") == "institute").select(
        [
            "main institute",
            "institute type",
            "administration type",
            "manager",
            "director",
            "educational coordinator",
            "address",
            "municipality",
            "telephone",
            "fax",
            "institute email",
            "management email",
            "secretary's office email",
            "website",
            "miur code",
            "vivoscuola institute link",
            "wikipedia municipality link",
        ]
    ).write_csv(INSTITUTES_FINAL, separator=";")
    df.filter(pl.col("entity") == "school").select(
        [
            "school",
            "address",
            "municipality",
            "telephone",
            "institute email",
            "miur code",
            "vivoscuola institute link",
            "wikipedia municipality link",
            "vivoscuola school link",
        ]
    ).write_csv(SCHOOLS_FINAL, separator=";")


df_s = pl.read_csv(STUDENTS, separator=";")
df_a = pl.read_csv(ADMISSION_RATES, separator=";")
df = (
    df_s.join(
        df_a, on=["vivoscuola school link", "academic year", "school year"], how="full"
    )
    .with_columns(
        pl.when(pl.col("vivoscuola school link").is_not_null())
        .then("vivoscuola school link")
        .otherwise("vivoscuola school link_right")
        .alias("vivoscuola school link"),
        pl.when(pl.col("academic year").is_not_null())
        .then("academic year")
        .otherwise("academic year_right")
        .alias("academic year"),
        pl.when(pl.col("school year").is_not_null())
        .then("school year")
        .otherwise("school year_right")
        .alias("school year"),
    )
    .select(
        pl.exclude(
            "vivoscuola school link_right", "academic year_right", "school year_right"
        )
    )
)
df.write_csv(FINAL_FOLDER + "test.csv", separator=";")
