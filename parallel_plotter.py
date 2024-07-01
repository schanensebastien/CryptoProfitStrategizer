import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os
from matplotlib import cm
import mplcursors

# Function to get all available currency pairs from the data directory
def get_all_currency_pairs(abs_file_path, interval):
    base_path = f'{abs_file_path}/data/{interval}/'
    if not os.path.exists(base_path):
        print(f"The base path {base_path} does not exist.")
        return []
    files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
    currency_pairs = list(set(f.split('_')[0] for f in files))
    return currency_pairs


# Function to get the latest currency pair files
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

# Function to normalize the data
def normalize_data(df, start_from_zero=False, normalize_by_percentage_growth=False):
    if normalize_by_percentage_growth:
        # Normalize by percentage growth
        df['normalized_close'] = (df['close'] / df['close'].iloc[0] - 1) * 100
    else:
        # Normalize by range
        min_val = df['close'].min()
        max_val = df['close'].max()
        df['normalized_close'] = (df['close'] - min_val) / (max_val - min_val) * 100
        if start_from_zero:
            df['normalized_close'] -= df['normalized_close'].iloc[0]
    return df











def parallel_plotter(
        currency_pairs,
        start_date = '2024-01-01-00-00',
        end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00',
        interval = 86400,  # 1 day in seconds
        start_from_zero = True,
        normalize_by_percentage_growth = True,
    ):
    # currency_pairs = [
    #     'DOGE-USD', 'SHIB-USD', 'BTC-USD', 'AIOZ-USD', 'AVAX-USD', 'AUCTION-USD', 
    #     'QI-USD', 'UNI-USD', 'VELO-USD', 'ABT-USD', 'ARB-USD', 'JTO-USD', 'VTHO-USD', 
    #     'ORN-USD', 'LPT-USD', 'JASMY-USD', 'AVT-USD', 'SUKU-USD', 'FET-USD', 'FOX-USD', 
    #     'BONK-USD', 'RARI-USD', 'AMP-USD'
    # ]
    # interval = 86400  # 1 day in seconds
    # start_date = '2024-01-01-00-00'
    # end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
    
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    if currency_pairs == True:
        currency_pairs = get_all_currency_pairs(script_directory, interval)


    latest_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)
    normalized_data = {}
    growth_rates = {}

    for currency_pair, file in zip(currency_pairs, latest_files):
        print(f"Loading data for {currency_pair} from {file}")
        data = pd.read_csv(file, parse_dates=['time'])
        start_dt = pd.to_datetime(start_date, format='%Y-%m-%d-%H-%M')
        end_dt = pd.to_datetime(end_date, format='%Y-%m-%d-%H-%M')
        data = data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]
        data['growth_rate'] = data['close'].pct_change().fillna(0)
        normalized_data[currency_pair] = normalize_data(data, start_from_zero, normalize_by_percentage_growth)
        growth_rates[currency_pair] = data.set_index('time')['growth_rate']

    colors = cm.get_cmap('tab20', len(currency_pairs))
    plt.figure(figsize=(14, 7))
    lines = []
    for i, currency_pair in enumerate(currency_pairs):
        line, = plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i), linewidth=2.0 if currency_pair == 'BTC-USD' else 1.0)
        lines.append(line)

    growth_rates_df = pd.DataFrame(growth_rates)
    strongest_growth_intervals = growth_rates_df.idxmax(axis=1)
    for time in strongest_growth_intervals.index:
        strongest_currency = strongest_growth_intervals.loc[time]
        color_index = currency_pairs.index(strongest_currency)
        plt.hlines(y=-100, xmin=time, xmax=time + pd.Timedelta(seconds=interval), colors=colors(color_index), linewidth=2.0 if strongest_currency == 'BTC-USD' else 6.0)

    plt.title('Normalized Cryptocurrency Prices')
    plt.xlabel('Date')
    plt.ylabel('Normalized Price (0 to 100)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    cursor = mplcursors.cursor(lines, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
    plt.show()



# # Define the currency pairs
# currency_pairs = [
#     'DOGE-USD',
#     'SHIB-USD',
#     'BTC-USD',
#     'AIOZ-USD',
#     'AVAX-USD',
#     'AUCTION-USD',
#     'QI-USD',
#     'UNI-USD',
#     'VELO-USD',
#     'ABT-USD',
#     'ARB-USD',
#     'JTO-USD',
#     'VTHO-USD',
#     'ORN-USD',
#     'LPT-USD',
#     'JASMY-USD',
#     'AVT-USD',
#     'SUKU-USD',
#     'FET-USD',
#     'FOX-USD',
#     'BONK-USD',
#     'RARI-USD',
#     'AMP-USD',
# ]

# interval = 86400  # 1 day in seconds
# start_date = '2024-01-01-00-00'
# end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
# script_directory = os.path.dirname(os.path.abspath(__file__))

# # Toggle variables
# start_from_zero = True
# normalize_by_percentage_growth = True

# # Parse command-line arguments
# parser = argparse.ArgumentParser(description='Plot normalized cryptocurrency prices.')
# parser.add_argument('-a', '--all', action='store_true', help='Select all cryptocurrencies in the data folder')
# args = parser.parse_args()

# if args.all:
#     currency_pairs = get_all_currency_pairs(script_directory, interval)

# # Fetch the latest data files for the currency pairs
# latest_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)

# # Dictionary to hold the normalized data
# normalized_data = {}
# growth_rates = {}

# # Load, filter, normalize, and store data for each currency pair
# for currency_pair, file in zip(currency_pairs, latest_files):
#     print(f"Loading data for {currency_pair} from {file}")
#     data = pd.read_csv(file, parse_dates=['time'])

#     # Convert start_date and end_date to datetime
#     start_dt = pd.to_datetime(start_date, format='%Y-%m-%d-%H-%M')
#     end_dt = pd.to_datetime(end_date, format='%Y-%m-%d-%H-%M')

#     # Filter the data within the date range
#     data = data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]

#     # Calculate growth rates
#     data['growth_rate'] = data['close'].pct_change().fillna(0)

#     # Normalize the data
#     normalized_data[currency_pair] = normalize_data(data, start_from_zero, normalize_by_percentage_growth)

#     # Store growth rates
#     growth_rates[currency_pair] = data.set_index('time')['growth_rate']

# # Define a colormap
# colors = cm.get_cmap('tab20', len(currency_pairs))

# # Plotting
# plt.figure(figsize=(14, 7))
# lines = []
# for i, currency_pair in enumerate(currency_pairs):
#     line, = plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i), linewidth=2.0 if currency_pair == 'BTC-USD' else 1.0)
#     lines.append(line)

# # Find the cryptocurrency with the highest growth rate for each time interval
# growth_rates_df = pd.DataFrame(growth_rates)
# strongest_growth_intervals = growth_rates_df.idxmax(axis=1)

# # Draw horizontal lines at y=-100 for the strongest growing cryptocurrency
# for time in strongest_growth_intervals.index:
#     strongest_currency = strongest_growth_intervals.loc[time]
#     color_index = currency_pairs.index(strongest_currency)
#     plt.hlines(y=-100, xmin=time, xmax=time + pd.Timedelta(seconds=interval), colors=colors(color_index), linewidth=2.0 if strongest_currency == 'BTC-USD' else 6.0)

# # Customize the plot
# plt.title('Normalized Cryptocurrency Prices')
# plt.xlabel('Date')
# plt.ylabel('Normalized Price (0 to 100)')
# plt.legend()
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()

# # Add hover functionality
# cursor = mplcursors.cursor(lines, hover=True)
# cursor.connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

# # Show the plot
# plt.show()


















# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# import datetime
# import os
# from matplotlib import cm
# import mplcursors  # Add this import
#
# # Define the currency pairs
# currency_pairs = [
#     'DOGE-USD',
#     'SHIB-USD',
#     'BTC-USD',
#     'AIOZ-USD',
#     'AVAX-USD',
#     'AUCTION-USD',
#     'QI-USD',
#     'UNI-USD',
#     'VELO-USD',
#     'ABT-USD',
#     'ARB-USD',
#     'JTO-USD',
#     'VTHO-USD',
#     'ORN-USD',
#     'LPT-USD',
#     'JASMY-USD',
#     'AVT-USD',
#     'SUKU-USD',
#     'FET-USD',
#     'FOX-USD',
#     'BONK-USD',
#     'RARI-USD',
#     'AMP-USD',
# ]
# interval = 86400  # 1 day in seconds
# start_date = '2024-01-01-00-00'
# end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
# script_directory = os.path.dirname(os.path.abspath(__file__))
#
# # Toggle variables
# start_from_zero = True
# normalize_by_percentage_growth = True
#
# # Function to get the latest currency pair files
# def get_latest_currency_pairs(currency_pairs, interval, abs_file_path):
#     # Prepare the list to hold the full path filenames of the latest files
#     path_file_names = []
#
#     # Base path for data, incorporating the interval directly
#     base_path = f'{abs_file_path}/data/{interval}/'
#     print('base_path: ', base_path)
#
#     # Ensure the base path exists
#     if not os.path.exists(base_path):
#         print(f"The base path {base_path} does not exist.")
#         return path_file_names
#
#     # Iterate through each currency pair to find the latest file
#     for pair in currency_pairs:
#         # Initialize a flag to check if a matching file is found
#         found = False
#         # List all files in the base directory that matches the interval
#         files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
#
#         # Filter and sort files by date for the current currency pair
#         sorted_files = sorted(
#             [file for file in files if file.startswith(pair + "_")],
#             key=lambda x: datetime.datetime.strptime(x.split('_')[-1], "%Y-%m-%d-%H-%M.csv"),
#             reverse=True
#         )
#
#         # If we find at least one file for the currency pair, add the full path of the latest file to the list
#         if sorted_files:
#             latest_file = sorted_files[0]
#             full_path = os.path.join(base_path, latest_file)
#             path_file_names.append(full_path)
#             found = True
#
#         if not found:
#             print(f"No files found for {pair} in {base_path}")
#
#     return path_file_names
#
# # Function to normalize the data
# def normalize_data(df, start_from_zero=False, normalize_by_percentage_growth=False):
#     if normalize_by_percentage_growth:
#         # Normalize by percentage growth
#         df['normalized_close'] = (df['close'] / df['close'].iloc[0] - 1) * 100
#     else:
#         # Normalize by range
#         min_val = df['close'].min()
#         max_val = df['close'].max()
#         df['normalized_close'] = (df['close'] - min_val) / (max_val - min_val) * 100
#         if start_from_zero:
#             df['normalized_close'] -= df['normalized_close'].iloc[0]
#     return df
#
# # Fetch the latest data files for the currency pairs
# latest_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)
#
# # Dictionary to hold the normalized data
# normalized_data = {}
# growth_rates = {}
#
# # Load, filter, normalize, and store data for each currency pair
# for currency_pair, file in zip(currency_pairs, latest_files):
#     print(f"Loading data for {currency_pair} from {file}")
#     data = pd.read_csv(file, parse_dates=['time'])
#
#     # Convert start_date and end_date to datetime
#     start_dt = pd.to_datetime(start_date, format='%Y-%m-%d-%H-%M')
#     end_dt = pd.to_datetime(end_date, format='%Y-%m-%d-%H-%M')
#
#     # Filter the data within the date range
#     data = data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]
#
#     # Calculate growth rates
#     data['growth_rate'] = data['close'].pct_change().fillna(0)
#
#     # Normalize the data
#     normalized_data[currency_pair] = normalize_data(data, start_from_zero, normalize_by_percentage_growth)
#
#     # Store growth rates
#     growth_rates[currency_pair] = data.set_index('time')['growth_rate']
#
# # Define a colormap
# colors = cm.get_cmap('tab20', len(currency_pairs))
#
# # Plotting
# plt.figure(figsize=(14, 7))
# lines = []
# for i, currency_pair in enumerate(currency_pairs):
#     line, = plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i), linewidth=2.0 if currency_pair == 'BTC-USD' else 1.0)
#     lines.append(line)
#
# # Find the cryptocurrency with the highest growth rate for each time interval
# growth_rates_df = pd.DataFrame(growth_rates)
# strongest_growth_intervals = growth_rates_df.idxmax(axis=1)
#
# # Draw horizontal lines at y=-100 for the strongest growing cryptocurrency
# for time in strongest_growth_intervals.index:
#     strongest_currency = strongest_growth_intervals.loc[time]
#     color_index = currency_pairs.index(strongest_currency)
#     plt.hlines(y=-100, xmin=time, xmax=time + pd.Timedelta(seconds=interval), colors=colors(color_index), linewidth=2.0 if strongest_currency == 'BTC-USD' else 6.0)
#
# # Customize the plot
# plt.title('Normalized Cryptocurrency Prices')
# plt.xlabel('Date')
# plt.ylabel('Normalized Price (0 to 100)')
# plt.legend()
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()
#
# # Add hover functionality
# cursor = mplcursors.cursor(lines, hover=True)
# cursor.connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
#
# # Show the plot
# plt.show()
























# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# import datetime
# import os
# from matplotlib import cm
#
# # Define the currency pairs
# currency_pairs = [
#   'DOGE-USD',
#   'SHIB-USD',
#   'BTC-USD',
#   'AIOZ-USD',
#   'AVAX-USD',
#   'AUCTION-USD',
#   'QI-USD',
#   'UNI-USD',
#   'VELO-USD',
#   'ABT-USD',
#   'ARB-USD',
#   'JTO-USD',
#   'VTHO-USD',
#   'ORN-USD',
#   'LPT-USD',
#   'JASMY-USD',
#   'AVT-USD',
#   'SUKU-USD',
#   'FET-USD',
#   'FOX-USD',
#   'BONK-USD',
#   'RARI-USD',
#   'AMP-USD',
# ]
# interval = 86400  # 1 day in seconds
# start_date = '2024-01-01-00-00'
# end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
# script_directory = os.path.dirname(os.path.abspath(__file__))
#
# # Toggle variables
# start_from_zero = True
# normalize_by_percentage_growth = True
#
# # Function to get the latest currency pair files
# def get_latest_currency_pairs(currency_pairs, interval, abs_file_path):
#     # Prepare the list to hold the full path filenames of the latest files
#     path_file_names = []
#
#     # Base path for data, incorporating the interval directly
#     base_path = f'{abs_file_path}/data/{interval}/'
#     print('base_path: ', base_path)
#
#     # Ensure the base path exists
#     if not os.path.exists(base_path):
#         print(f"The base path {base_path} does not exist.")
#         return path_file_names
#
#     # Iterate through each currency pair to find the latest file
#     for pair in currency_pairs:
#         # Initialize a flag to check if a matching file is found
#         found = False
#         # List all files in the base directory that matches the interval
#         files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
#
#         # Filter and sort files by date for the current currency pair
#         sorted_files = sorted(
#             [file for file in files if file.startswith(pair + "_")],
#             key=lambda x: datetime.datetime.strptime(x.split('_')[-1], "%Y-%m-%d-%H-%M.csv"),
#             reverse=True
#         )
#
#         # If we find at least one file for the currency pair, add the full path of the latest file to the list
#         if sorted_files:
#             latest_file = sorted_files[0]
#             full_path = os.path.join(base_path, latest_file)
#             path_file_names.append(full_path)
#             found = True
#
#         if not found:
#             print(f"No files found for {pair} in {base_path}")
#
#     return path_file_names
#
# # Function to normalize the data
# def normalize_data(df, start_from_zero=False, normalize_by_percentage_growth=False):
#     if normalize_by_percentage_growth:
#         # Normalize by percentage growth
#         df['normalized_close'] = (df['close'] / df['close'].iloc[0] - 1) * 100
#     else:
#         # Normalize by range
#         min_val = df['close'].min()
#         max_val = df['close'].max()
#         df['normalized_close'] = (df['close'] - min_val) / (max_val - min_val) * 100
#         if start_from_zero:
#             df['normalized_close'] -= df['normalized_close'].iloc[0]
#     return df
#
# # Fetch the latest data files for the currency pairs
# latest_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)
#
# # Dictionary to hold the normalized data
# normalized_data = {}
# growth_rates = {}
#
# # Load, filter, normalize, and store data for each currency pair
# for currency_pair, file in zip(currency_pairs, latest_files):
#     print(f"Loading data for {currency_pair} from {file}")
#     data = pd.read_csv(file, parse_dates=['time'])
#
#     # Convert start_date and end_date to datetime
#     start_dt = pd.to_datetime(start_date, format='%Y-%m-%d-%H-%M')
#     end_dt = pd.to_datetime(end_date, format='%Y-%m-%d-%H-%M')
#
#     # Filter the data within the date range
#     data = data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]
#
#     # Calculate growth rates
#     data['growth_rate'] = data['close'].pct_change().fillna(0)
#
#     # Normalize the data
#     normalized_data[currency_pair] = normalize_data(data, start_from_zero, normalize_by_percentage_growth)
#
#     # Store growth rates
#     growth_rates[currency_pair] = data.set_index('time')['growth_rate']
#
# # Define a colormap
# colors = cm.get_cmap('tab20', len(currency_pairs))
#
# # Plotting
# plt.figure(figsize=(14, 7))
# for i, currency_pair in enumerate(currency_pairs):
#     plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i), linewidth=2.0 if currency_pair == 'BTC-USD' else 1.0)
#
# # Find the cryptocurrency with the highest growth rate for each time interval
# growth_rates_df = pd.DataFrame(growth_rates)
# strongest_growth_intervals = growth_rates_df.idxmax(axis=1)
#
# # Draw horizontal lines at y=-100 for the strongest growing cryptocurrency
# for time in strongest_growth_intervals.index:
#     strongest_currency = strongest_growth_intervals.loc[time]
#     color_index = currency_pairs.index(strongest_currency)
#     plt.hlines(y=-100, xmin=time, xmax=time + pd.Timedelta(seconds=interval), colors=colors(color_index), linewidth=2.0 if strongest_currency == 'BTC-USD' else 6.0)
#
# # Customize the plot
# plt.title('Normalized Cryptocurrency Prices')
# plt.xlabel('Date')
# plt.ylabel('Normalized Price (0 to 100)')
# plt.legend()
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()
#
# # Show the plot
# plt.show()
#
#
#
#
#
#
#
#
#
#
#
#
#
# # import matplotlib.pyplot as plt
# # import pandas as pd
# # import numpy as np
# # import datetime
# # import os
# # from matplotlib import cm
#
# # # Define the currency pairs
# # currency_pairs = [
# #   'DOGE-USD',
# #   'SHIB-USD',
# #   'BTC-USD',
# #   'AIOZ-USD',
# #   'ARB-USD',
# #   'JTO-USD',
# #   'VTHO-USD',
# #   'ORN-USD',
# #   'LPT-USD',
# #   'JASMY-USD',
# #   'AVT-USD',
# #   'SUKU-USD',
# #   'FET-USD',
# # ]
# # interval = 86400  # 1 day in seconds
# # start_date = '2024-02-01-00-00'
# # end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
# # script_directory = os.path.dirname(os.path.abspath(__file__))
#
# # # Toggle variables
# # start_from_zero = True
# # normalize_by_percentage_growth = True
#
# # # Function to get the latest currency pair files
# # def get_latest_currency_pairs(currency_pairs, interval, abs_file_path):
# #     # Prepare the list to hold the full path filenames of the latest files
# #     path_file_names = []
#
# #     # Base path for data, incorporating the interval directly
# #     base_path = f'{abs_file_path}/data/{interval}/'
# #     print('base_path: ', base_path)
#
# #     # Ensure the base path exists
# #     if not os.path.exists(base_path):
# #         print(f"The base path {base_path} does not exist.")
# #         return path_file_names
#
# #     # Iterate through each currency pair to find the latest file
# #     for pair in currency_pairs:
# #         # Initialize a flag to check if a matching file is found
# #         found = False
# #         # List all files in the base directory that matches the interval
# #         files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
#
# #         # Filter and sort files by date for the current currency pair
# #         sorted_files = sorted(
# #             [file for file in files if file.startswith(pair + "_")],
# #             key=lambda x: datetime.datetime.strptime(x.split('_')[-1], "%Y-%m-%d-%H-%M.csv"),
# #             reverse=True
# #         )
#
# #         # If we find at least one file for the currency pair, add the full path of the latest file to the list
# #         if sorted_files:
# #             latest_file = sorted_files[0]
# #             full_path = os.path.join(base_path, latest_file)
# #             path_file_names.append(full_path)
# #             found = True
#
# #         if not found:
# #             print(f"No files found for {pair} in {base_path}")
#
# #     return path_file_names
#
# # # Function to normalize the data
# # def normalize_data(df, start_from_zero=False, normalize_by_percentage_growth=False):
# #     if normalize_by_percentage_growth:
# #         # Normalize by percentage growth
# #         df['normalized_close'] = (df['close'] / df['close'].iloc[0] - 1) * 100
# #     else:
# #         # Normalize by range
# #         min_val = df['close'].min()
# #         max_val = df['close'].max()
# #         df['normalized_close'] = (df['close'] - min_val) / (max_val - min_val) * 100
# #         if start_from_zero:
# #             df['normalized_close'] -= df['normalized_close'].iloc[0]
# #     return df
#
# # # Fetch the latest data files for the currency pairs
# # latest_files = get_latest_currency_pairs(currency_pairs, interval, script_directory)
#
# # # Dictionary to hold the normalized data
# # normalized_data = {}
#
# # # Load, filter, normalize, and store data for each currency pair
# # for currency_pair, file in zip(currency_pairs, latest_files):
# #     print(f"Loading data for {currency_pair} from {file}")
# #     data = pd.read_csv(file, parse_dates=['time'])
#
# #     # Convert start_date and end_date to datetime
# #     start_dt = pd.to_datetime(start_date, format='%Y-%m-%d-%H-%M')
# #     end_dt = pd.to_datetime(end_date, format='%Y-%m-%d-%H-%M')
#
# #     # Filter the data within the date range
# #     data = data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]
#
# #     # Normalize the data
# #     normalized_data[currency_pair] = normalize_data(data, start_from_zero, normalize_by_percentage_growth)
#
# # # Define a colormap
# # colors = cm.get_cmap('tab20', len(currency_pairs))
#
# # # Plotting
# # plt.figure(figsize=(14, 7))
# # for i, currency_pair in enumerate(currency_pairs):
# #     if currency_pair == 'BTC-USD':
# #         plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i), linewidth=5.0)
# #     else:
# #         plt.plot(normalized_data[currency_pair]['time'], normalized_data[currency_pair]['normalized_close'], label=currency_pair, color=colors(i))
#
# # # Customize the plot
# # plt.title('Normalized Cryptocurrency Prices')
# # plt.xlabel('Date')
# # plt.ylabel('Normalized Price (0 to 100)')
# # plt.legend()
# # plt.grid(True)
# # plt.xticks(rotation=45)
# # plt.tight_layout()
#
# # # Show the plot
# # plt.show()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # import matplotlib.pyplot as plt
# # import pandas as pd
# # import numpy as np
# # import datetime
# # from Historic_Crypto import HistoricalData
#
#
#
#
# # # Define the currency pairs
# # currency_pairs = [
# #   'DOGE-USD',
# #   'SHIB-USD',
# #   'BTC-USD',
# #   'AIOZ-USD',
# #   'ARB-USD',
# #   'JTO-USD',
# #   'VTHO-USD',
# #   'ORN-USD',
# #   'LPT-USD',
# #   'JASMY-USD',
# #   'AVT-USD',
# #   'SUKU-USD',
# #   'FET-USD',
# # ]
#
# # # Define the interval and date range for the historical data
# # interval = 86400  # 1 day in seconds
# # start_date = '2024-01-01-00-00'
# # end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'
#
#
#
#
# # # Function to normalize the data
# # def normalize_data(df):
# #   min_val = df['close'].min()
# #   max_val = df['close'].max()
# #   df['normalized_close'] = (df['close'] - min_val) / (max_val - min_val) * 100
# #   return df
#
#
#
# # # Dictionary to hold the normalized data
# # normalized_data = {}
#
# # # Fetch, normalize, and store data for each currency pair
# # for currency_pair in currency_pairs:
# #   print(f"Fetching data for {currency_pair}")
# #   historical_data = HistoricalData(currency_pair, interval, start_date, end_date).retrieve_data()
# #   normalized_data[currency_pair] = normalize_data(historical_data)
#
# # # Plotting
# # plt.figure(figsize=(14, 7))
# # for currency_pair in currency_pairs:
# #   plt.plot(normalized_data[currency_pair].index, normalized_data[currency_pair]['normalized_close'], label=currency_pair)
#
# # # Customize the plot
# # plt.title('Normalized Cryptocurrency Prices')
# # plt.xlabel('Date')
# # plt.ylabel('Normalized Price (0 to 100)')
# # plt.legend()
# # plt.grid(True)
# # plt.xticks(rotation=45)
# # plt.tight_layout()
#
# # # Show the plot
# # plt.show()
