# Smart Utility Hub

A local Flask web app for measurement conversion and retail billing. Use Python 3.9 or newer.

## Run on Windows

Open PowerShell in the folder containing `app.py`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Run on macOS or Linux

Open a terminal in the folder containing `app.py`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open [Smart Utility Hub](http://127.0.0.1:5000/) in a browser. Press Ctrl+C in the terminal to stop the server. JavaScript enables unit selection by category, adding and removing item rows, and the print button.

## Unit converter

Choose length, weight, or temperature, enter a value, and select the source and target units. Length and weight require nonnegative values. Temperature supports Celsius, Fahrenheit, and Kelvin down to absolute zero. The result displays up to 12 significant digits.

## Retail billing

Enter the customer name and optional contact and address. Add up to 50 items with positive whole-number quantities and nonnegative prices with up to two decimal places. Select **Generate invoice**, then **Print invoice** to print or save a PDF through your browser.

| Subtotal (INR) | Discount |
| --- | ---: |
| Below ₹1,000 | 0% |
| ₹1,000 to ₹4,999.99 | 5% |
| ₹5,000 to ₹9,999.99 | 10% |
| ₹10,000 and up | 15% |

The matching rate applies to the full subtotal. The discount is rounded to the nearest paise, with half paise rounded up. The app generates each invoice on submission and keeps no invoice history. Save a copy through the print dialog for your records. Edit `TIERS` and `CURRENCY` in `app.py` to customize billing.
