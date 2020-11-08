import urllib3
import json
import sqlite3
import collections
import os


def earthquakes_location():
    http = urllib3.PoolManager()
    req = http.request(
        "GET",
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
    )
    response = req.data
    obj = json.loads(response)

    details = obj["features"]
    return details


def populate_dict(details):
    quake_details = {}
    quake_locations = {}
    for item in details:
        innerlocation = {
            "id": item["id"],
            "latitude": item["geometry"]["coordinates"][0],
            "longitude": item["geometry"]["coordinates"][2],
        }
        innerdetails = {
            "id": item["id"],
            "mag": item["properties"]["mag"],
            "place": item["properties"]["place"],
            "time": item["properties"]["time"],
            "detail": item["properties"]["detail"],
            "felt": item["properties"]["felt"],
            "alert": item["properties"]["alert"],
            "status": item["properties"]["status"],
            "title": item["properties"]["title"],
            "tsunami": item["properties"]["tsunami"],
            "type": item["properties"]["type"],
        }
        quake_locations[item["id"]] = innerlocation
        quake_details[item["id"]] = innerdetails
    return quake_details, quake_locations


def dict_to_table(rows, table_name, database_name):
    db_conn = sqlite3.connect(database_name)
    c = db_conn.cursor()

    for row in rows:

        column_values = list(rows[row].values())
        column_lst = list(rows[row].keys())
        column_names = ", ".join(map(str, column_lst))
        place_holder = "?, " * len(column_lst)
        place_holder = place_holder[:-2]
        place_holder = str(place_holder)
        c.executemany(
            f"""INSERT OR IGNORE INTO {table_name}({column_names}) VALUES({place_holder}) ;""",
            [column_values],
        )
    db_conn.commit()
    db_conn.close()


def create_table(table_name, db_name):
    db_conn = sqlite3.connect(db_name)
    # cursor to interacte with sql db
    c = db_conn.cursor()

    if table_name == "details":
        c.execute(
            f"""CREATE TABLE  IF NOT EXISTS {table_name}(
            ID INTEGER,
            MAG NUM,
            PLACE TEXT,
            TIME DATE,
            DETAIL TEXT,
            FELT TEXT,
            ALERT TEXT DEAULT NULL,
            STATUS TEXT,
            TSUNAMI TEXT DEFUALT NULL,
            MAGTYPE TEXT DEFAULT NULL,
            TYPE TEXT DEFAULT NULL,
            TITLE TEXT DEFAULT NULL,
            UNIQUE(ID));
            """
        )
        # Creating table

    if table_name == "locations":

        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name}(
            ID INTEGER,
            LATITUDE TEXT ,
            LONGITUDE TEXT,
            UNIQUE(ID));
            """
        )
    db_conn.commit()
    db_conn.close()


def main():
    hourly_data = earthquakes_location()
    formatted_quakelocation, formatted_quakedetails = populate_dict(hourly_data)
    quake_locations_table_name = "details"
    quake_details_table_name = "locations"
    db_name = "earthquake.db"
    create_table(quake_details_table_name, db_name)
    create_table(quake_locations_table_name, db_name)
    dict_to_table(formatted_quakedetails, quake_details_table_name, db_name)
    dict_to_table(formatted_quakelocation, quake_locations_table_name, db_name)


if __name__ == "__main__":
    main()
