#!/usr/bin/python3
""" holds class User"""

from os import getenv
import sqlalchemy
from datetime import datetime
import pandas as pd
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from datetime import datetime
from hashlib import md5
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define your MySQL database connection parameters
db_config = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "Dilsebo_shop",  # Your database name
}

# Configure the database URL
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://piyasa_dev:piyasa_dev_pwd@localhost/Dilsebo_shop'

# Create the database object
db = SQLAlchemy(app)

class Sales(db.Model):
    __tablename__ = 'Sales'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    sale_date = db.Column(db.Date)
    quantity_sold = db.Column(db.Integer)
    price = db.Column(db.Float)
    total_sale_price = db.Column(db.Float)

# Define the CumulativeTotal class
class CumulativeTotal(db.Model):
    __tablename__ = 'CumulativeTotal'
    id = db.Column(db.Integer, primary_key=True)
    total_sale_price = db.Column(db.Float, default=0.0)

# Initialize a list to store today's sales data
today_sales_data = []

# Initialize a running total variable
running_total = 0.0


@app.route('/submit_Sale', methods=['POST'])
def submit_Sale():

    if request.method == 'POST':
        product_id = request.form['product_id']
        customer_id = request.form['customer_id']
        sale_date_str = request.form['sale_date']
        sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d')

        quantity_sold = request.form['quantity_sold']
        price = request.form['price']

        try:
            # Convert quantity_sold and price to appropriate data types
            quantity_sold = int(quantity_sold)
            price = float(price)

            # Calculate the total sale price
            total_sale_price = quantity_sold * price

            # Update the cumulative total in the CumulativeTotal table
            total_record = CumulativeTotal.query.first()
            total_record.total_sale_price += total_sale_price
            db.session.commit()

            # Add today's sales data to the list
            today_sales_data.append({
                'product_id': product_id,
                'customer_id': customer_id,
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'quantity_sold': quantity_sold,
                'price': price,
                'total_sale_price': total_sale_price
            })

            # Calculate the sum of total_sale_price for today's sales
            today_total_price = sum(sale['total_sale_price'] for sale in today_sales_data)


             # Retrieve today's sales records
            today_sales = Sales.query.filter_by(sale_date=datetime.now().date()).all()

            # Convert the sales records to a format you want to display (e.g., JSON)
            sales_data = [{'product_id': sale.product_id, 'customer_id': sale.customer_id, 'sale_date': sale.sale_date.strftime('%Y-%m-%d'), 'quantity_sold': sale.quantity_sold, 'price': sale.price, 'total_sale_price': sale.total_sale_price} for sale in today_sales]

            # Create a Pandas DataFrame from the sales data
            df = pd.DataFrame(sales_data)

            # Save the DataFrame as an Excel file
            excel_filename = 'sales_data.xlsx'
            df.to_excel(excel_filename, index=False)

             # Calculate the sum of total_sale_price for today's sales

            today_total_price = sum(sale['total_sale_price'] for sale in today_sales_data)

             # Render an HTML page to display the sales data as a table
            return render_template('sales_table.html', sales=df.to_html(classes='table table-striped'), title='Today\'s Sales', running_total=today_total_price)


            return f'Data saved as {excel_filename}', 200

        except ValueError:
            # Handle invalid input (e.g., non-numeric quantity or price)
            error_message = "Invalid input. Quantity and price must be numeric."
            response_data = {'error': error_message}
            return jsonify(response_data), 400


        except Exception as e:
            # Handle any exceptions and return an error response
            error_message = str(e)
            response_data = {'error': error_message}
            return jsonify(response_data), 500

# Define the main index route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)

