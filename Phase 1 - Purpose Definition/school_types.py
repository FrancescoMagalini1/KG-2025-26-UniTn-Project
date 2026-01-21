import polars as pl

FOLDER = "./data/school types/"
FILES = {
    "infanzia.csv": "infanzia",
    "formazione_professionale.csv": "formazione professionale",
    "primaria.csv": "primaria",
    "secondaria_1.csv": "secondaria di primo grado",
    "secondaria_2.csv": "secondaria di secondo grado",
}

dfs: list[pl.DataFrame] = []
for file, value in FILES.items():
    df = (
        pl.read_csv(FOLDER + file, separator=";")
        .select("Istituto Principale", "Scuola")
        .rename({"Istituto Principale": "institute", "Scuola": "school"})
        .with_columns(pl.lit(value).alias("school type"))
    )
    dfs.append(df)

final = pl.concat(dfs)
final = final.filter(pl.col("school").is_not_null())
final = final.with_columns(
    [
        pl.col(col).str.to_lowercase()
        for col in final.columns
        if final[col].dtype == pl.String
    ]
)
final.write_csv(FOLDER + "school_types.csv", separator=";")
