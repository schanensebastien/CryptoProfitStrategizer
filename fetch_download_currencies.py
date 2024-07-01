from Historic_Crypto import Cryptocurrencies, HistoricalData#, LiveCryptoData
import pandas as pd
import datetime
import glob
import os







def fetch_all_currency_pairs():
  """
  Fetches all available currency pairs from the Historical_Crypto library.
  """
  currency_pairs = Cryptocurrencies().find_crypto_pairs()
  return currency_pairs


def download_historical_data(currency_pair, interval, start_date, end_date, file_path):
  """
  Retrieves historical data for a given currency pair and interval and saves it to a CSV file.
  """
  historical_data = HistoricalData(currency_pair, interval, start_date, end_date)
  data = historical_data.retrieve_data()


  last_time = data.index[-1].strftime('%Y-%m-%d-%H-%M')
  filename = f"{file_path}/data/{interval}/{currency_pair}_{interval}_{last_time}.csv"
  print(f'filepath: {file_path}')
  data.reset_index().to_csv(filename, index=False)
  print(f"\n This file is saved: {filename}\n\n")

def get_previous_filedata(files):
    """
    Extracts the first and last time value from a CSV file.

    Args:
        filename (str): The path to the CSV file.
    """
    # Read the CSV file
    filename = files[0]
    data = pd.read_csv(filename)

    print('headers: ', data)

    # Extract the first and last time value
    start_date = data['time'][0] + '-00-00'
    file_enddate = list(data['time'])[-1] + '-00-00'


    return (start_date, file_enddate, filename)







def fetch_download_all_cryptocurrencies(interval=86400):
  script_directory = os.path.dirname(os.path.abspath(__file__))


  currency_pairs = fetch_all_currency_pairs()




  print('#####################################################')
  print('#####################################################')
  print('#############  DOWNLOADING CRYPTO  ##################')
  print('#####################################################')
  print('#####################################################')

  for currency_pair in currency_pairs[currency_pairs['status'] == 'online']['id'].tolist():
    print(currency_pair)
  
  
    files = glob.glob(f"data/{interval}/{currency_pair}_{interval}*.csv")
  
    start_date, file_enddate, filename = get_previous_filedata(files) if files else ('2008-11-16-00-00', 'None', None)
    end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
  
  
    print(f"\n\ncurrency_pair: {currency_pair}\ninterval: {interval}\nstart_date: {start_date}\nend_date: {end_date}")
    print('files: ', files)
  
    print(f"\n\n{end_date} | {file_enddate}\n{type(end_date)} | {type(file_enddate)}\n{end_date != file_enddate}\n\n")
    if end_date != file_enddate:
      if filename:
        os.remove(filename)
      print(currency_pair, start_date)
      download_historical_data(currency_pair, interval, start_date, end_date, script_directory)
    else:
      print(f"\n Current file already exist\n\n")






if __name__ == "__main__":
  fetch_download_all_cryptocurrencies()