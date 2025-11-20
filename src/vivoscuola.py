import polars as pl

# 'istituto principale', 'scuola', 'tipo istituto', 'tipo gestione', 'dirigente', 'direttore',
# 'coordinatore pedagogico', 'indirizzo', 'comune', 'telefono', 'fax', 'email istituto', 'email dirigenza',
# 'email segreteria', 'sito web', 'codice miur'

# Source: https://www.vivoscuola.it/

PATH_OG = "./data/vivoscuola.csv"
PATH_CLEAN = "./data/vivoscuola_clean.csv"


def clean():
    df = pl.read_csv(PATH_OG, separator=";")
    df = df.rename(lambda col: col.lower())
    df = df.with_columns(
        [
            pl.col(col).str.to_lowercase()
            for col in df.columns
            if df[col].dtype == pl.String
        ]
    )
    df.write_csv(PATH_CLEAN, separator=";")


df = pl.read_csv(PATH_CLEAN, separator=";").select("dirigente", "direttore")
print(df)
