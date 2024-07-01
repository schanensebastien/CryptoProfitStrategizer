 
# Cryptocurrency Data Analysis Tool

This repository contains a suite of Python scripts for fetching, downloading, analyzing, and visualizing cryptocurrency data. The main functionalities include fetching historical cryptocurrency data, analyzing consecutive days with specific price and volume criteria, and plotting normalized cryptocurrency prices.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Fetch Cryptocurrency Data](#fetch-cryptocurrency-data)
  - [Analyze Consecutive Days](#analyze-consecutive-days)
  - [Plot Cryptocurrency Data](#plot-cryptocurrency-data)
- [Files](#files)
- [License](#license)

## Requirements

- Python 3.7+
- pandas
- matplotlib
- numpy
- argparse
- Historic_Crypto
- mplcursors

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/cryptocurrency-data-analysis.git
    cd cryptocurrency-data-analysis
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Fetch Cryptocurrency Data
Fetch and download historical cryptocurrency data for all available currency pairs.
```sh
python main.py fetch
```
Optional arguments:
- `-i`, `--interval`: Interval in seconds for data fetch; default is 86400 (1 day).


### Analyze Consecutive Days
Analyze consecutive days with specified price and volume criteria for a list of cryptocurrency pairs.

```sh
python main.py analyze -c 'BTC-USD' -p 0.01 -v 0.01
```
Required arguments:
- `-c`, `--currency_pairs`: List of cryptocurrency pairs to analyze.
- `-p`, `--price_tolerance`: Price tolerance for analysis.
- `-v`, `--volume_tolerance`: Volume tolerance for analysis.

Optional arguments:
- `-n`, `--num_consecutive_days`: Number of consecutive days for analysis; default is 3.
- `-s`, `--start_from`: Starting index for data analysis; default is 0.
- `-r`, `--remove_lastdatapoints`: Data points to remove from the end of the dataset; default is 0.
- `-i`, `--interval`: Interval in seconds for data analysis; default is 86400 (1 day).


### Plot Cryptocurrency Data
Plot normalized cryptocurrency prices for a list of cryptocurrency pairs.
```sh
python main.py plot -c 'BTC-USD' 'ETH-USD'
```
Optional arguments:
- `-c`, `--currency_pairs`: List of cryptocurrency pairs to analyze. If not specified, all available pairs will be used.
- `-s`, `--start_date`: Start date for the data plot; default is '2024-01-01-00-00'.
- `-e`, `--end_date`: End date for the data plot; default is the current date minus one day.
- `-i`, `--interval`: Interval in seconds for plotting; default is 86400 (1 day).
- `-z`, `--start_from_zero`: Whether to start normalization from zero; default is True.
- `-n`, `--normalize_by_percentage_growth`: Whether to normalize by percentage growth; default is True.


## Files
- `main.py`: Main entry point for the program. Includes argument parsing and command execution.
- `fetch_download_currencies.py`: Contains functions to fetch and download historical cryptocurrency data.
- `consecutivedays_analyzer.py`: Contains functions to analyze consecutive days based on price and volume criteria.
- `parallel_plotter.py`: Contains functions to plot normalized cryptocurrency prices.


## License
This project is licensed under the AGPL-3.0 License.


