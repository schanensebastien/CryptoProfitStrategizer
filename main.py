import argparse
import datetime

from fetch_download_currencies import fetch_download_all_cryptocurrencies
from consecutivedays_analyzer import consecutivedays_analyzer
from parallel_plotter import parallel_plotter



# TODO: https:⁄⁄tradologics.com⁄#overview
# TODO: Use QTPyLib and⁄or quantstats


def main():
    parser = argparse.ArgumentParser(description='Cryptocurrency Data Analysis Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Subparser for fetching and downloading cryptocurrency data
    # example: python3 main.py fetch
    fetch_parser = subparsers.add_parser('fetch', help='Fetch and download cryptocurrency data')
    fetch_parser.add_argument('-i', '--interval', type=int, default=86400, help='Interval in seconds for data fetch; default=86400')

    # Subparser for analyzing consecutive days
    # example: python3 main.py analyze -c 'DOGE-USD' -p 0.01 -v 0.01
    analyze_parser = subparsers.add_parser('analyze', help='Analyze consecutive days with price and volume data')
    analyze_parser.add_argument('-c', '--currency_pairs', nargs='+', help='List of cryptocurrency pairs to analyze')
    analyze_parser.add_argument('-p', '--price_tolerance', type=float, required=True, help='Price tolerance for analysis')
    analyze_parser.add_argument('-v', '--volume_tolerance', type=float, required=True, help='Volume tolerance for analysis')
    analyze_parser.add_argument('-n', '--num_consecutive_days', type=int, default=3, help='Number of consecutive days for analysis; default=3')
    analyze_parser.add_argument('-s', '--start_from', type=int, default=0, help='Starting index for data analysis; default=0')
    analyze_parser.add_argument('-r', '--remove_lastdatapoints', type=int, default=0, help='Data points to remove from the end of the dataset; default=0')
    analyze_parser.add_argument('-i', '--interval', type=int, default=86400, help='Interval in seconds for data analysis; default=86400')

    # Subparser for parallel plotting of data
    # example: python3 main.py plot -c 
    # example: python3 main.py plot -c 'DOGE-USD' 'BTC-USD'
    plot_parser = subparsers.add_parser('plot', help='Plot normalized cryptocurrency prices')
    plot_parser.add_argument('-c', '--currency_pairs', nargs='*', required=False, help='List of cryptocurrency pairs to analyze')
    plot_parser.add_argument('-s', '--start_date', type=str, default='2024-01-01-00-00', help="Start date for the data plot; default='2024-01-01-00-00'")
    plot_parser.add_argument('-e', '--end_date', type=str, default=(datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00', help="End date for the data plot; default=(datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '-00-00'")
    plot_parser.add_argument('-i', '--interval', type=int, default=86400, help='Interval in seconds for plotting; default=86400')
    plot_parser.add_argument('-z', '--start_from_zero', action='store_false', default=True, help='Whether to start normalization from zero; default=True')
    plot_parser.add_argument('-n', '--normalize_by_percentage_growth', action='store_false', default=True, help='Whether to normalize by percentage growth; default=True')
    
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    elif args.command == 'fetch':
        fetch_download_all_cryptocurrencies(
            args.interval,
        )
    elif args.command == 'analyze':
        consecutivedays_analyzer(
            args.currency_pairs,
            args.price_tolerance,
            args.volume_tolerance,
            num_consecutive_days = args.num_consecutive_days,
            interval = args.interval,
            start_from = args.start_from,
            remove_lastdatapoints = args.remove_lastdatapoints,
        )
    elif args.command == 'plot':
        if args.currency_pairs == []:
            args.currency_pairs = True

        print(f"args.currency_pairs: {args.currency_pairs}")            
        parallel_plotter(
            args.currency_pairs,
            start_date = args.start_date,
            end_date = args.end_date,
            interval = args.interval,
            start_from_zero = args.start_from_zero,
            normalize_by_percentage_growth = args.normalize_by_percentage_growth,
        )





if __name__ == "__main__":
    main()
