import polars as pl

INPUT_FOLDER = "./input_data/"
OUTPUT_FOLDER = "./input_data/obj_properties/"


def bordering():
    df = pl.read_csv(INPUT_FOLDER + "wikipedia.csv", separator=";")
    df = df.select("municipality", "bordering municipalities", "wikipedia link").rename(
        {
            "municipality": "name",
            "bordering municipalities": "bordering",
            "wikipedia link": "link",
        }
    )
    mapping = df.select("name", "link").unique().to_dicts()
    mapping = {item["link"]: item["name"] for item in mapping}
    df = (
        df.select("name", "bordering")
        .with_columns(pl.col("bordering").str.split("|"))
        .explode("bordering")
        .with_columns(pl.col("bordering").replace(mapping))
    )
    df.write_csv(OUTPUT_FOLDER + "bordering.csv", separator=";")


def add_row_index(path: str):
    pl.read_csv(path, separator=";").with_row_index(offset=1).write_csv(
        path, separator=";"
    )


def add_addmission_rates():
    df1 = pl.read_csv(INPUT_FOLDER + "schools.csv", separator=";")
    df2 = pl.read_csv(INPUT_FOLDER + "average_admission_rates.csv", separator=";")
    df = df1.join(df2, on="vivoscuola school link", how="left")
    df.write_csv(INPUT_FOLDER + "schools.csv", separator=";")


def has_school():
    df_i = pl.read_csv(INPUT_FOLDER + "institutes.csv", separator=";")
    df_s = pl.read_csv(INPUT_FOLDER + "schools.csv", separator=";")
    mapping = df_i.select("index", "vivoscuola institute link").to_dicts()
    mapping = {item["vivoscuola institute link"]: item["index"] for item in mapping}
    df = (
        df_s.select("index", "vivoscuola institute link")
        .rename({"index": "school", "vivoscuola institute link": "institute"})
        .with_columns(pl.col("institute").replace(mapping))
    )
    df.write_csv(OUTPUT_FOLDER + "has_school.csv", separator=";")


def is_located():
    df_i = pl.read_csv(INPUT_FOLDER + "institutes.csv", separator=";")
    df_s = pl.read_csv(INPUT_FOLDER + "schools.csv", separator=";")
    df_m = pl.read_csv(INPUT_FOLDER + "wikipedia.csv", separator=";")
    df_m = df_m.select("municipality", "wikipedia link").rename(
        {
            "municipality": "name",
            "wikipedia link": "link",
        }
    )
    mapping = df_m.select("name", "link").unique().to_dicts()
    mapping = {item["link"]: item["name"] for item in mapping}
    df_i = (
        df_i.select("index", "wikipedia municipality link")
        .rename({"index": "institute", "wikipedia municipality link": "municipality"})
        .with_columns(pl.col("municipality").replace(mapping))
    )
    df_i.write_csv(OUTPUT_FOLDER + "institutes_located.csv", separator=";")
    df_s = (
        df_s.select("index", "wikipedia municipality link")
        .rename({"index": "school", "wikipedia municipality link": "municipality"})
        .with_columns(pl.col("municipality").replace(mapping))
    )
    df_s.write_csv(OUTPUT_FOLDER + "schools_located.csv", separator=";")


def school_stats():
    df_a = pl.read_csv(INPUT_FOLDER + "admission_rates.csv", separator=";")
    df_s = pl.read_csv(INPUT_FOLDER + "students.csv", separator=";")
    mapping = (
        pl.read_csv(INPUT_FOLDER + "schools.csv", separator=";")
        .select("index", "vivoscuola school link")
        .rename({"index": "school", "vivoscuola school link": "link"})
        .to_dicts()
    )
    mapping = {item["link"]: item["school"] for item in mapping}
    df_a = df_a.with_columns(
        pl.col("vivoscuola school link").replace(mapping).alias("school")
    ).select(pl.exclude("vivoscuola school link"))
    df_a.write_csv(INPUT_FOLDER + "admission_rates.csv", separator=";")
    df_s = df_s.with_columns(
        pl.col("vivoscuola school link").replace(mapping).alias("school")
    ).select(pl.exclude("vivoscuola school link"))
    df_s.write_csv(INPUT_FOLDER + "students.csv", separator=";")


def stats_relations():
    df_a = pl.read_csv(INPUT_FOLDER + "admission_rates.csv", separator=";")
    df_s = pl.read_csv(INPUT_FOLDER + "students.csv", separator=";")
    df_a.select("index", "school").write_csv(
        OUTPUT_FOLDER + "has_statistics.csv", separator=";"
    )
    df_s.select("index", "school").write_csv(
        OUTPUT_FOLDER + "has_students_info.csv", separator=";"
    )


def join_school_types():
    df_s = pl.read_csv(INPUT_FOLDER + "schools.csv", separator=";").select(
        "index", "school", "vivoscuola institute link"
    )
    df_i = (
        pl.read_csv(INPUT_FOLDER + "institutes.csv", separator=";")
        .select("main institute", "vivoscuola institute link")
        .rename({"main institute": "institute"})
    )
    df = (
        df_s.join(df_i, on="vivoscuola institute link", how="left")
        .select(pl.exclude("vivoscuola institute link"))
        .with_columns(
            pl.col("school").str.strip_chars(), pl.col("institute").str.strip_chars()
        )
    )
    df_t = pl.read_csv(INPUT_FOLDER + "school_types.csv", separator=";").with_columns(
        pl.col("school").str.strip_chars(), pl.col("institute").str.strip_chars()
    )
    df = df.join(df_t, on=["institute", "school"], how="left").select(
        "index", "school type"
    )
    df.write_csv(INPUT_FOLDER + "school_types_final.csv", separator=";")


join_school_types()
