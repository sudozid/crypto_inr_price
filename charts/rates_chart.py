import re
import pandas as pd
from flask import Flask, send_file
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import render_template

app = Flask(__name__)

# Update the path if your CSV file is in a different directory
csv_file_path = 'rates.csv'

# Function to read CSV data from a file and return a DataFrame
def read_csv_data(file_path):
    # Use a regular expression to correctly separate the columns
    pattern = re.compile(r'\"(\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2})\",(\d+.\d+),(\d+.\d+),(\d+.\d+),(\d+.\d+)')

    # Read the entire file into a string
    with open(file_path, 'r') as file:
        file_contents = file.read()

    data = []
    for match in pattern.finditer(file_contents.strip()):
        row = match.groups()
        # Combine date and time into one datetime column
        data.append([f"{row[0]} {row[1]}", *map(float, row[2:])])

    df = pd.DataFrame(data, columns=['DateTime', 'Binance Price', 'WAZX Price', 'Paxful Price', 'White Price'])
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    return df

# Function to plot the DataFrame and save as an image
def plot_data(df):
    plt.figure(figsize=(10, 5))
    # Calculate running averages for selected prices
    df['Binance Avg'] = df['Binance Price'].rolling(window=5).mean()
    df['WAZX Avg'] = df['WAZX Price'].rolling(window=5).mean()
    df['Paxful Avg'] = df['Paxful Price'].rolling(window=5).mean()

    # Plot running averages
    plt.plot(df['DateTime'], df['Binance Avg'], label='Binance Avg')
    plt.plot(df['DateTime'], df['WAZX Avg'], label='WAZX Avg')
    plt.plot(df['DateTime'], df['Paxful Avg'], label='Paxful Avg')

    # Plot only the White Price without running average
    plt.plot(df['DateTime'], df['White Price'], label='White Price')

    plt.xlabel('DateTime')
    plt.ylabel('Price')
    plt.title('Cryptocurrency Prices (Running Averages & White Price)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Flask route to serve the chart and data table
@app.route('/chart')
def chart():
    df = read_csv_data(csv_file_path)
    buf = plot_data(df)
    # Encode image to base64 string
    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    # Convert DataFrame to HTML
    data_table = df.to_html(index=False, classes='table table-striped', border=0)
    # Render template with image and data table
    return render_template('chart_with_data.html', image_data=image_data, data_table=data_table)

if __name__ == '__main__':
    app.run(debug=True)
