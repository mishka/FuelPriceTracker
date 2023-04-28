It's a library that retrieves the latest gasoline, diesel, and LPG prices from fuel station APIs and logs them to a CSV file. It can also generate a graph of the historical prices.

![alt text](https://github.com/mishka/FuelPriceTracker/blob/main/29-04-2023.png?raw=true)
## Prerequisites
 - Python 3.x
 - pandas
 - matplotlib
 - requests
 
## How to Use
Clone the repository using the following command:

`git clone https://github.com/mishka/FuelPriceTracker.git`

Install the necessary packages via pip

`pip install pandas matplotlib requests`

## Usage Example

```python
# Import the gasgasgas module and create a gas object
from gasgasgas import gasgasgas
gas = gasgasgas()

# Retrieve the latest fuel prices using the "parse_prices" method
prices = gas.parse_prices()  # Output: {'lpg': '10.51', 'gasoline': '20.37', 'diesel': '19.76'}

# Alternatively, you can use the "latest_price" attribute to access the latest prices
# This will read the last entry of the CSV file (if it exists) and save it in this attribute
# If the file doesn't exist, it will generate the prices using the "parse_price" method
print(gas.latest_prices)  # Output: {'lpg': '10.51', 'gasoline': '20.37', 'diesel': '19.76'}

# Log the latest prices to the CSV file using the "log" method
# You will see print statements about whether the data is logged or not, depending on if the data has changed since the last run
gas.log(prices)

# Generate a chart based on all the data in the CSV file using the "generate_char" method
# This will return the filename of the created chart so you can refer to it later
filename_of_the_chart = gas.generate_chart()

# Example filename: 29-04-2023.png
```

## APIs used
 - BP  
 - Opet  
 - Aygaz  
 
Note: If and BP API fails, the Aygaz API is used as a backup for LPG prices.

## License
Distributed under the MIT License. See LICENSE for more information.
