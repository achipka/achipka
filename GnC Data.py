import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Create a custom business day calendar for the year 2023
cal = np.busdaycalendar(
    holidays=['2022-01-17', '2022-02-21', '2022-04-15', '2022-05-30', '2022-06-20', '2022-07-04', '2022-09-05', '2022-11-24', '2022-12-26', '2023-01-01', '2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04', '2023-11-23', '2023-12-25', '2024-01-01', '2024-01-15', '2024-02-19', '2024-03-29', '2024-05-27', '2024-06-19', '2024-07-04', '2024-09-02', '2024-11-28', '2024-12-25', '2025-01-01', '2025-01-09', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26', '2025-06-19', '2025-07-04', '2025-09-01', '2025-11-27', '2025-12-25']
)

# Read the Excel file
file_path = r"C:\Users\andrew\OneDrive - Andrew Chipka\Penny Stocks\Gap n Crap\GnC.xlsx"  # Replace with your file path
df = pd.read_excel(file_path)

# Define your function that uses name and date
def yfin(name, date, index, ex):
    try:
        stock = yf.Ticker(name)
        dateObject = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        shares = stock.info.get('sharesOutstanding')
        country = stock.info.get('country', 'Unknown')  # Use 'Unknown' if country is not available
        sector = stock.info.get('industry', 'Unknown')  # Use 'Unknown' if sector is not available


        today = dateObject

        # Helper function to get the closing price of a stock for a specific date
        def get_close_price(days_offset):
            target_date = today - timedelta(days=days_offset)
            busday = np.busday_offset(target_date.date(), 0, roll='backward', busdaycal=cal)
            busday_datetime = datetime.utcfromtimestamp(pd.Timestamp(busday).timestamp())
            busday_datetime = busday_datetime.replace(tzinfo=None)
            history = stock.history(start=busday_datetime, end=busday_datetime + timedelta(days=1), interval="1d", prepost=False)
            if not history.empty:
                return history['Close'].iloc[0]
            return None

        # Calculate historical closing prices
        close_1_month = get_close_price(30)
        close_2_months = get_close_price(60)
        close_3_months = get_close_price(90)
        close_6_months = get_close_price(180)
        close_1_year = get_close_price(365)
        close_2_years = get_close_price(730)

        # Get today's price data
        todayOnly = today.strftime("%Y-%m-%d")
        previous_busday = np.busday_offset(datetime.strptime(todayOnly, "%Y-%m-%d").date(), -1, roll='backward', busdaycal=cal)
        before_busday = np.busday_offset(previous_busday, -1, roll='backward', busdaycal=cal)
        next_busday = np.busday_offset(datetime.strptime(todayOnly, "%Y-%m-%d").date(), 1, roll='forward', busdaycal=cal)
        aft_busday = np.busday_offset(next_busday, 1, roll='forward', busdaycal=cal)

        # Convert to Python datetime objects
        previous_busday = datetime.utcfromtimestamp(pd.Timestamp(previous_busday).timestamp()).date()
        before_busday = datetime.utcfromtimestamp(pd.Timestamp(before_busday).timestamp()).date()
        next_busday = datetime.utcfromtimestamp(pd.Timestamp(next_busday).timestamp()).date()
        aft_busday = datetime.utcfromtimestamp(pd.Timestamp(aft_busday).timestamp()).date()

        previous_busday = datetime.combine(previous_busday, datetime.min.time())
        before_busday = datetime.combine(before_busday, datetime.min.time())
        next_busday = datetime.combine(next_busday, datetime.min.time())
        aft_busday = datetime.combine(aft_busday, datetime.min.time())

        ps = datetime.strptime(todayOnly, '%Y-%m-%d') + timedelta(hours=16)  # afterhours start (4pm)
        pe = datetime.strptime(todayOnly, '%Y-%m-%d') + timedelta(hours=20)  # afterhours end (8pm)
        pst = datetime.strptime(next_busday.strftime('%Y-%m-%d'), '%Y-%m-%d') + timedelta(hours=4)  # premarket start (4am)
        pet = datetime.strptime(next_busday.strftime('%Y-%m-%d'), '%Y-%m-%d') + timedelta(hours=9, minutes=30)  # premarket end (9:30am)
            
        # Data Scope (chronological order)
        yy = stock.history(start=before_busday, end=previous_busday, interval="1d", prepost=False)
        y = stock.history(start=previous_busday, end=today, interval="1d", prepost=False)
        pm = stock.history(start=ps, end=pe, interval='30m', prepost=True)
        m = stock.history(start=today, end=next_busday, interval="1d", prepost=False)
        pmt = stock.history(start=pst, end=pet, interval='30m', prepost=True)
        t = stock.history(start=next_busday, end=aft_busday, interval="1d", prepost=True)
        
        # Retrieve data before the date
        bdc = yy['Close'].iloc[-1]  # Use the last row if multiple rows exist
        pdc = y['Close'].iloc[0]
        pdl = y['Low'].iloc[0]
        pdv = y['Volume'].sum()
        
        pm_h = pm['High'].max() 
        pm_l = pm['Low'].min() 
        pm_v = pm['Volume'].sum()
        
        today_o = m['Open'].iloc[0]
        today_c = m['Close'].iloc[0]
        today_v = m['Volume'].sum()
        mkt_h = m['High'].max()
        mkt_l = m['Low'].min()
        
        # Initialize the result dictionary
        result = {
            "Index": index,
            "Name": name,
            "Ex": ex,
            "Date": date,
            
            "BDC": bdc,
            "PDL": pdl,
            "PDC": pdc,

            "PM H": pm_h,
            "PM L": pm_l,
            "O": today_o,
            "H": mkt_h,
            "L": mkt_l,
            "C": today_c,
            
            "PDV": pdv,
            "Vol": today_v,
            
            "SO": shares,
            "Close 1 Month": close_1_month,
            "Close 2 Months": close_2_months,
            "Close 3 Months": close_3_months,
            "Close 6 Months": close_6_months,
            "Close 1 Year": close_1_year,
            "Close 2 Years": close_2_years,
            "Country": country,
            "Sector": sector,
            "Error": None  # No error
        }

        # Attempt to retrieve data after the date
        try:
            # Get afterhours data from the current date
            pm_today = stock.history(start=ps, end=pe, interval='30m', prepost=True)
            pmt_h = pm_today[pm_today.index.time <= datetime.strptime(todayOnly, '%Y-%m-%d').replace(hour=20, minute=0).time()]['High'].max()
            pmt_l = pm_today[pm_today.index.time <= datetime.strptime(todayOnly, '%Y-%m-%d').replace(hour=20, minute=0).time()]['Low'].min()
            
            # Limit the next premarket data to before 9:30 AM
            t_before_market = t[t.index.time <= datetime.strptime(next_busday.strftime('%Y-%m-%d'), '%Y-%m-%d').replace(hour=9, minute=30).time()]
            
            # Check if afterhours high is greater than the next premarket high
            if t_before_market['High'].max() > pmt_h:
                pmt_h = t_before_market['High'].max()
            
            # Check if afterhours low is less than the next premarket low
            if t_before_market['Low'].min() < pmt_l:
                pmt_l = t_before_market['Low'].min()
            
            tmr_l = t_before_market['Low'].min()
            tmr_o = t_before_market['Open'].iloc[0]
            
            # Add additional data to the result dictionary
            result.update({
                "N PM H": pmt_h,
                "N PM L": pmt_l,
                "NDO": tmr_o,
                "NL": tmr_l
            })
        except Exception as e:
            print(f"Error processing after-market data for {name} on {date}: {e}")
            result["Error"] = f"Partial data retrieved: {e}"

        return result

    except Exception as e:
        print(f"Error processing {name} on {date}: {e}")
        return {
            "Index": index,
            "Name": name,
            "Ex": ex,
            "Date": date,
            "BDC": None,
            "PDL": None,
            "PDC": None,
            "PM H": None,
            "PM L": None,
            "O": None,
            "H": None,
            "L": None,
            "C": None,
            "N PM H": None,
            "N PM L": None,
            "NDO": None,
            "NL": None,
            "PDV": None,
            "Vol": None,
            "SO": None,
            "Close 1 Month": None,
            "Close 2 Months": None,
            "Close 3 Months": None,
            "Close 6 Months": None,
            "Close 1 Year": None,
            "Close 2 Years": None,
            "Country": None,
            "Sector": None,
            "Error": str(e)  # Store the error message
        }

# Process each row in the DataFrame
results = []
for index, row in df.iterrows():
    name = row['Name']  # Assuming 'Name' is the header of the first column
    date = row['Date']  # Assuming 'Date' is the header of the second column
    index = row['Index']
    ex = row["Ex"]
    
    if pd.isna(date):
        continue  # Skip rows where date is NaN
    
    print(name)
    print(date)

    # Call the yfin function with name and date
    result = yfin(name, date, index, ex)
    
    # Append the result to the list
    results.append(result)

# Create a DataFrame from the results with specified column order
columns_order = ["Index", "Name", "Ex", "Date", "BDC", "PDL", "PDC", "PM H", "PM L", "O", "H", "L", "C", 
                 "Close 1 Month", "Close 2 Months", "Close 3 Months", "Close 6 Months", "Close 1 Year", "Close 2 Years",
                 "N PM H", "N PM L", "NDO", "NL", "PDV", "Vol", "SO", "Country", "Sector", "Error"]
result_df = pd.DataFrame(results, columns=columns_order)

# Save the updated DataFrame back to the original Excel file
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    result_df.to_excel(writer, sheet_name='Sheet1', index=False)
