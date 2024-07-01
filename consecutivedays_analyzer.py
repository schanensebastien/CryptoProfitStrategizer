import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os






def get_latest_currency_pairs(currency_pairs, interval, abs_file_path):
  # Prepare the list to hold the full path filenames of the latest files
  path_file_names = []

  # Base path for data, incorporating the interval directly
  base_path = f'{abs_file_path}/data/{interval}/'
  print('base_path: ', base_path)

  # Ensure the base path exists
  if not os.path.exists(base_path):
      print(f"The base path {base_path} does not exist.")
      return path_file_names

  # Iterate through each currency pair to find the latest file
  for pair in currency_pairs:
      # Initialize a flag to check if a matching file is found
      found = False
      # List all files in the base directory that matches the interval
      files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]

      # Filter and sort files by date for the current currency pair
      sorted_files = sorted(
          [file for file in files if file.startswith(pair + "_")],
          key=lambda x: datetime.datetime.strptime(x.split('_')[-1], "%Y-%m-%d-%H-%M.csv"),
          reverse=True
      )


      # If we find at least one file for the currency pair, add the full path of the latest file to the list
      if sorted_files:
          latest_file = sorted_files[0]
          full_path = os.path.join(base_path, latest_file)
          path_file_names.append(full_path)
          found = True

      if not found:
          print(f"No files found for {pair} in {base_path}")

  return path_file_names










def is_higher_close_and_volume(price_data, i, price_tolerance, volume_tolerance):
  # Get current and previous price data and volume
  current_price = price_data.iloc[i]['price']
  previous_price = price_data.iloc[i - 1]['price']

  current_volume = price_data.iloc[i]['volume']
  previous_volume = price_data.iloc[i - 1]['volume']


  # Calculate the tolerances for price and volume
  price_tolerance = previous_price * price_tolerance
  volume_tolerance = previous_volume * volume_tolerance

  # Compare current and previous day's price and volume with tolerance
  is_price_higher_or_close = (current_price >= previous_price - price_tolerance)
  is_volume_higher_or_close = (current_volume >= previous_volume - volume_tolerance)

  if is_price_higher_or_close and is_volume_higher_or_close:
    return True
  else:
    return False




def find_consecutive_days(df, price_tolerance, volume_tolerance, num_consecutive_days=3):
  price_data = pd.DataFrame({
    'price': df[['open', 'close']].max(axis=1),
    'volume': df['volume']
  })

  consecutive_days = []
  consecutive_days_counter = 1
  position = []

  for i in range(1, len(df)):
    if is_higher_close_and_volume(price_data, i, price_tolerance, volume_tolerance):
      consecutive_days_counter += 1
    else:
      consecutive_days_counter = 0


    # print(f'{consecutive_days_counter} - {len(position)}; {consecutive_days_counter == 0 and len(position) >= 1}')

    if consecutive_days_counter == num_consecutive_days:
      position.append(i)
    elif consecutive_days_counter == 0 and len(position) >= 1:
      position.append(i)
      position.append(consecutive_days_counter)

      consecutive_days.append(position.copy())
      consecutive_days_counter = 0
      position = []

  return consecutive_days






def calculate_profits(df, consecutive_days, investment_amount = 100):
  balance = investment_amount
  profits = []

  # Calculate profit for each position
  for start, end, consecutive_days_value in consecutive_days:
    entry_price = df.iloc[start]['close']
    exit_price = df.iloc[end]['close']


    # Calculate profit in percent
    profit_percent = (exit_price - entry_price) / entry_price

    # Store profit for each position
    profits.append(profit_percent * 100)

    # Update total balance
    balance = (1 + profit_percent) * balance
    print('Balance: ', balance)

  # Display individual and total profits
  for i, profit in enumerate(profits, start=1):
    print(f"Profit for position {i}: {profit:.2f}%")

  print(f"Total cumulative percentage profit from all positions: {(balance - investment_amount):.2f}%")
  print(f"Average return per year: {(balance - investment_amount)/(len(df)/365):.2f}%")
  print(f"CAGR: {(((balance/investment_amount)**(1/(len(df)/365))-1)*100):.2f}%")
  print(f"Total years: {(len(df)/365):.2f}")







def consecutivedays_analyzer(
    currency_pairs,
    price_tolerance,
    volume_tolerance,
    num_consecutive_days = 3,
    interval = 86400,
    start_from = 0,
    remove_lastdatapoints = 0,
):
  script_directory = os.path.dirname(os.path.abspath(__file__))

  # interval = 86400  # 1 day in seconds


  # start_from = 150
  # remove_lastdatapoints = 200


  # currency_pairs = ['JASMY-USD']
  # price_tolerance = 0.01
  # volume_tolerance = 0.01
  # num_consecutive_days = 2

  # currency_pairs = ['DOGE-USD']
  # price_tolerance = 0.005
  # volume_tolerance = 0.1
  # num_consecutive_days = 3

  # currency_pairs = ['FET-USD']
  # price_tolerance = 0.175
  # volume_tolerance = 0.175
  # num_consecutive_days = 2

  #TODO: Treat the amount of sigmals as a buy signal?


  latest_selected_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)



  for selected_file in latest_selected_files:
    # Read data into DataFrame
    df = pd.read_csv(selected_file)
    df = df[start_from:len(df)-remove_lastdatapoints]
    print(len(df))
    print(df['time'])

    # Find consecutive days
    consecutive_days = find_consecutive_days(df, price_tolerance, volume_tolerance, num_consecutive_days)
    calculate_profits(df, consecutive_days)
    # exit()



    # for simpler visualisation
    # df['close'] = np.log(df['close'])

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(14, 7))



    df_dates = pd.read_csv(selected_file, parse_dates=['time'], index_col='time')[start_from:]

    # Plot the close chart on the primary y-axis
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    # ax1.set_xlabel('Date (index)')
    ax1.set_ylabel('Close Price', color=color)
    ax1.plot(df_dates.index, df_dates['close'], label='Close Price', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Rotate date labels for better readability
    plt.xticks(rotation=45)

    # Create a secondary y-axis for the volume bar chart
    ax2 = ax1.twinx()
    color = 'tab:gray'
    ax2.set_ylabel('Volume', color=color)
    ax2.bar(df_dates.index, df_dates['volume'], alpha=0.3, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # Mark consecutive days with vertical lines
    for start, end, consecutive_days_value in consecutive_days:
      # Convert index positions to dates
      start_date = df_dates.iloc[start].name
      end_date = df_dates.iloc[end].name

      # Use the dates for axvline
      ax1.axvline(x=start_date, color='green', linestyle='-')
      ax1.axvline(x=end_date, color='red', linestyle='-')



    plt.title(f'Close Price and Volume Chart - {selected_file}')
    fig.tight_layout()  # For better layout handling
    plt.legend(['Close Price'], loc='upper left')
    plt.show()






if __name__ == "__main__":
  consecutivedays_analyzer()