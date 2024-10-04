import os
from io import StringIO
import datetime
import pandas as pd
import requests

def get_token(user, password):

    response = requests.post("https://portal.c-lockinc.com/api/login", data={"user": user, "pass": password})
    if response.status_code == 200:
        token = response.text.strip()
        print(token)
        return token
    else:
        response.raise_for_status()

def get(url, token):
    response = requests.post(url, data={"token": token})
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()


def get_owned_systems(name, token):
    """
    Retrieves the list of systems owned by the user.

    Args:
        name (str): The name identifier for the systems.
        token (str): The authentication token.

    Returns:
        list: A list of systems owned by the user.
    """
    response = get(f"https://portal.c-lockinc.com/api/getownedsystems?d={name}", token)
    
    response
    df = pd.read_csv(StringIO(response), skiprows=1, sep=",")
    
    return df["SystemID"].values


def process(user, password, interval):
    """
    Downloads data from the GreenFeed API and stores it in the database.

    Args:
        user (str): The username for authentication.
        password (str): The password for authentication.
        interval (int): The number of days of data to process.
    """
    token = get_token(user, password)
    systems = get_owned_systems("greenfeed", token)
    total_data = pd.DataFrame()
    today = datetime.datetime.now().date()

    # Process data for each day within the interval
    for i in range(interval):
        start = today - datetime.timedelta(days=i)
        end = today - datetime.timedelta(days=i - 1)


        # Skip the first two lines which are usually headers
        for feeder_id in systems:
            
            
            data = get(
                f"https://portal.c-lockinc.com/api/getemissions?d=visits&fids={feeder_id}&st={start}%2000:00:00&et={end}%2012:00:00&preliminary=0",
                token,
            )

            # Check for valid data length
            if len(data) < 100:
                print("Error in data")
                print(data)
                continue

            df = pd.read_csv(StringIO(data), skiprows=1, sep=",")

            # Process the dataframe if it contains sufficient columns and data
            if len(df.columns) > 5 and len(df["FeederID"].values) > 10:
                columns = list(df.columns)
                columns.remove("FeederID")
                columns = ["date", "cow", "greenfeed"] + columns + ["user"]
                df["cow"] = 0
                df["user"] = user
                df["greenfeed"] = int(feeder_id)
                df["date"] = pd.to_datetime(df["StartTime"]).dt.normalize()
                df = df[columns]
                total_data = pd.concat([df, total_data])

        # Save the data if it contains sufficient rows
        if len(total_data.columns) > 5 and len(total_data["greenfeed"].values) > 10:
            # Fill missing values
            total_data.fillna(0, inplace=True)
            total_data["AnimalName"] = total_data["AnimalName"].astype(int, errors="ignore")
            total_data["cow"] = total_data["cow"].astype(int, errors="ignore")
            total_data["RFID"] = total_data["RFID"].astype(np.int64, errors="ignore").astype(str)
            total_data["greenfeed"] = total_data["greenfeed"].astype(int, errors="ignore")
            total_data.fillna(0, inplace=True)

        # Save the summarized data to a CSV file
        total_data.to_csv(f'summarized_{start}.csv')
        print(total_data)
        total_data = pd.DataFrame()


def feed(user, password, interval, data_type="rfid"):
    """
    Downloads and processes raw feed data from the GreenFeed API.

    Args:
        user (str): The username for authentication.
        password (str): The password for authentication.
        interval (int): The number of days of data to process.
        data_type (str): The type of data to retrieve ('rfid' or other types).
    """
    token = get_token(user, password)
    systems = get_owned_systems("greenfeed", token)
    return systems
    rfid_count = 0
    feed_count = 0
    today = datetime.datetime.now().date()

    # Process data for each day within the interval
    for i in range(interval):
        start = today - datetime.timedelta(days=i)
        end = today - datetime.timedelta(days=i - 1)
        combined_data = False

        # Skip the first two lines which are usually headers
        for system in systems[2:]:
            feeder_id = system.split(",")[0]
            url = f"https://portal.c-lockinc.com/api/getraw?d={data_type}&fids={feeder_id}&st={start}%2000:00:00&et={end}%2012:00:00"           
            data = get(url, token)
            df = pd.read_csv(StringIO(data), skiprows=1, sep=",", on_bad_lines="skip")

            if len(df.columns) > 2:
                df["cow"] = 0
                df["user"] = user
                df["greenfeed"] = int(feeder_id)
                df["date"] = pd.to_datetime(df["DateTime"]).dt.date
                
            else:
                print("Skipping due to insufficient columns:", len(df.columns))

            if len(df.columns) > 5 and len(df["greenfeed"].values) > 10 and df.shape[0] > 0:
                if data_type == "rfid":
                    rfid_count += 1
                else:
                    feed_count += 1
            combined_data = pd.concat([df, combined_data]) if combined_data is not False else df

        combined_data.to_csv(f"{data_type}_{start}.csv")
        combined_data = False

process("USERNAME", "PASSWORD",2)
feed("USERNAME", "PASSWORD",5, 'feed')
feed("USERNAME", "PASSWORD",5, 'rfid')
