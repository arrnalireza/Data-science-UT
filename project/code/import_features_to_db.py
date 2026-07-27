import pandas as pd
from database_connection import get_engine
from perfect_config import db_config


def import_raw_csvs():
    engine= get_engine()
    for table_name, csv_path in db_config.raw_csv_paths.items():
        df= pd.read_csv(csv_path)
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False
        )

if __name__ == "__main__":
    import_raw_csvs()