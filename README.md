# GreenFeed Data Retrieval API

This project is designed to interact with the GreenFeed methane measurement units via an API. It enables users to authenticate, retrieve, and process data from GreenFeed systems, specifically focusing on methane, carbon dioxide, and other relevant emissions data. The data is saved locally in CSV format for further analysis.


## Features

- **Authentication**: Securely log in using user credentials to retrieve an access token.
- **Data Retrieval**: Fetch data from GreenFeed units, including methane and other gas emissions.
- **Data Processing**: Process raw data, add relevant metadata, and save results in CSV format.
- **Customizable Data Range**: Specify the number of days for which you want to retrieve data.
- **Support for Multiple Data Types**: Retrieve data in various formats, such as visits and raw feeds.

## Requirements

- Python 3.8 or higher
- The following Python packages:
  - `pandas`
  - `numpy`
  - `datetime`
  - `sqlalchemy`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/greenfeed-api.git
    cd greenfeed-api
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Make sure you have `curl` installed on your system, as it is used for making API requests.

## Usage

To use this API, you need to run the script with valid user credentials and specify the desired time interval for data retrieval.

### Example

Here's an example of how to use the `process` function to retrieve data:

```python
from greenfeed_api import process, feed

# Replace 'USER' and 'PASS' with your GreenFeed credentials
USER = 'your_username'
PASS = 'your_password'

# Specify the number of days of data you want to retrieve
INTERVAL = 7

# Retrieve and process emissions data
process(USER, PASS, INTERVAL)

# Retrieve and process feed data
feed(USER, PASS, INTERVAL, 'rfid')
