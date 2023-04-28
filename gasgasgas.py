import os, csv

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter

from datetime import datetime
from requests import get, post


class gas_prices:
    def __init__(self):
        self.headers = {
            'content-type': 'application/json; charset=utf-8',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }
        
        self.opet = 'https://api.opet.com.tr/api/fuelprices/prices?ProvinceCode=934&IncludeAllProducts=true'        
        self.bp = 'https://www.bp.com/bp-tr-pump-prices/api/PumpPrices?strCity=%C4%B0STANBUL%20(AVRUPA)'
        self.log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gas_prices.csv')
        
        # pain :D
        self.aygaz = {
            'dates': 'https://www.aygaz.com.tr/otogaz/otogazapi.aspx/gecerlilikTarihleriGetir',
            'prices': 'https://www.aygaz.com.tr/otogaz/otogazapi.aspx/fiyatGetir',
            'json': {'il': '341'}
        }

        # Define the latest prices as a dictionary
        self.latest_prices = {}

        # Check if the gas_prices.csv file exists
        self.file_exists = os.path.isfile(self.log_file_path)

        # If the file exists, read the latest prices from it
        if self.file_exists:
            with open(self.log_file_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        self.latest_prices = {
                            'gasoline': row[1],
                            'diesel': row[2],
                            'lpg': row[3]
                        }

        # If the file does not exist, try to get the prices from the parse_prices function
        if not self.file_exists:
            self.latest_prices = self.parse_prices()


    def fetch_prices(self):
        prices = True
        
        # Get the bloody Opet LPG prices
        lpg_date = post(self.aygaz['dates'], json=self.aygaz['json'], headers=self.headers)

        # After getting the latest available date from the API, call the other endpoint with it
        if lpg_date.status_code == 200:
            post_json = {**self.aygaz['json'] ,'tarih': eval(lpg_date.json()['d'])[0]}
            lpg_price = post(self.aygaz['prices'], json=post_json, headers=self.headers).json()['d'].replace('"', '')
        else:
            # Use BP as a backup if Aygaz API fails
            bp_lpg = get(self.bp, headers=self.headers)

            if bp_lpg.status_code == 200:
                lpg_price = bp_lpg.json()[0]['LpgPrice']
            else:
                lpg_price = False
                print('None of the LPG price APIs work.')

        # Try to get the prices from Opet
        opet_resp = get(self.opet, headers=self.headers)
        if opet_resp.status_code == 200:
            opet_prices = opet_resp.json()
            data_type = 'Opet'
        else:
            # Use BP as a backup if Opet API fails
            bp_resp = get(self.bp, headers=self.headers)
            if bp_resp.status_code == 200:
                bp_prices = bp_resp.json()
                data_type = 'BP'
            else:
                prices = None

        # If both requests fail, raise an exception
        if prices is None:
            raise Exception('Failed to retrieve prices from both Opet and BP')
        
        return [('LPG', lpg_price), (data_type, opet_prices or bp_prices)]


    def parse_prices(self):
        data = self.fetch_prices()
        source = data[1][0]

        results = {}

        # If both of the LPG price APIs fail, write the last known price
        if data[0][1] == False:
            results['lpg'] = self.latest_prices['lpg']
        else:
            results['lpg'] = str(data[0][1])

        if source == 'Opet':
            results['gasoline'] = str(data[1][1][0]['prices'][0]['amount'])
            results['diesel'] = str(data[1][1][0]['prices'][2]['amount'])
        elif source == 'BP':
            results['gasoline'] = str(data[1][1][0]['Benzin'])
            results['diesel'] = str(data[1][1][0]['Motorin'])

        return results
    

    def logging(self, prices):
        # Check if the current data is different from the previous entry
        current_data = [datetime.now().strftime('%d/%m/%Y'), prices['gasoline'], prices['diesel'], prices['lpg']]
        previous_data = [self.latest_prices['gasoline'], self.latest_prices['diesel'], self.latest_prices['lpg']]

        if previous_data == current_data[1:]: # minus the date
            print('Data is not changed. Skipping the write to CSV file.')
            return

        # Write to the log file
        with open(self.log_file_path, 'a', newline='') as file:
            headers = ['Timestamp', 'Gasoline Price', 'Diesel Price', 'LPG Price']
            writer = csv.DictWriter(file, fieldnames=headers)

            # Write headers to the file if it doesn't exist
            if not self.file_exists:
                writer.writeheader()

            # Write the data to the file
            writer.writerow({
                'Timestamp': current_data[0],
                'Gasoline Price': current_data[1],
                'Diesel Price': current_data[2],
                'LPG Price': current_data[3]
            })

        print('Data is changed. Writing to CSV file.')


    def generate_charts(self):
        # Load data from CSV file into a pandas DataFrame
        df = pd.read_csv(self.log_file_path, dayfirst=True, parse_dates=['Timestamp'], index_col='Timestamp')

        # Create a line chart with all data on a single chart
        ax = df.plot(figsize=(15, 12), linewidth=4, marker='o', markersize=12)

        # Set chart title and axis labels
        ax.set_title('Fuel Prices Over Time', fontsize=36, fontweight='bold')
        ax.set_xlabel('Date', fontsize=36, fontweight='bold')
        ax.set_ylabel('Price Per Liter (₺)', fontsize=36, fontweight='bold')

        # Customize tick labels and grid lines
        ax.tick_params(axis='both', which='major', labelsize=24)
        ax.tick_params(axis='y', which='major', labelsize=24)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Keep track of the last value for each fuel type
        last_values = {fuel_type: None for fuel_type in df.columns}

        for i, line in enumerate(ax.lines):
            fuel_type = df.columns[i]
            for x, y in zip(line.get_xdata(), line.get_ydata()):
                # Only annotate the chart if the current value is different from the last value
                if last_values[fuel_type] is None or y != last_values[fuel_type]:
                    label = f"{y:.2f}"
                    ax.annotate(label, xy=(x, y), xytext=(5, 5), textcoords="offset points", color=line.get_color(), fontsize=18)
                    last_values[fuel_type] = y

        # Customize colors and styles for each line
        ax.lines[0].set_color('#FF9AA2')  # light pink for gasoline prices
        ax.lines[0].set_linestyle('-')   # solid line style
        ax.lines[1].set_color('#6A5ACD')  # blue-violet for diesel prices
        ax.lines[1].set_linestyle('--')  # dashed line style
        ax.lines[2].set_color('#87CEEB')  # sky blue for LPG prices
        ax.lines[2].set_linestyle(':')   # dotted line style

        # Customize markers for each line
        ax.lines[0].set_markerfacecolor('#FF9AA2')  # light pink for gasoline markers
        ax.lines[0].set_markeredgecolor('#E75480')  # darker pink for gasoline marker edges
        ax.lines[1].set_markerfacecolor('#6A5ACD')  # blue-violet for diesel markers
        ax.lines[1].set_markeredgecolor('#4B0082')  # indigo for diesel marker edges
        ax.lines[2].set_markerfacecolor('#87CEEB')  # sky blue for LPG markers
        ax.lines[2].set_markeredgecolor('#1E90FF')  # dodger blue for LPG marker edges

        # Add legend and adjust its position and font size
        ax.legend(['Gasoline', 'Diesel', 'LPG'], loc='center left', fontsize=32)

        # Add a background color to the chart
        ax.set_facecolor('#FDEFF2')

        # Set x-axis tick labels to display precise dates of the data entries
        xticks = df.index
        xticklabels = [dt.strftime('%d %b %Y') for dt in xticks]
        ax.set_xticks(xticks)                  # 90?
        ax.set_xticklabels(xticklabels, rotation=45, ha='right')

        # Add grid lines to the price axis and customize their style
        ax.yaxis.grid(linestyle='--', alpha=0.7)

        # Customize y-axis tick labels to display prices with two decimal places
        y_format = FormatStrFormatter('%.2f')
        ax.yaxis.set_major_formatter(y_format)

        # Show the DataFrame with two decimal places for the price values
        print(df.to_string(float_format='{:,.2f}'.format))

        # Set custom figure size and dpi
        fig = plt.gcf()
        fig.set_size_inches(38.4, 21.6)  # 3840x2160 pixels

        # Save the chart
        chart_filename = f'{datetime.now().strftime("%d-%m-%Y")}.png'
        plt.savefig(chart_filename, dpi=150)

        # Display the chart
        # plt.show()

        return chart_filename