import csv
import glob
import pandas as pd
from datetime import datetime
import openpyxl
import pytz

DEFAULT_CURRENCY = 'USD'
DEFAULT_UNIT = 'Gallons'
DEFAULT_FUEL = 'Diesel'

# Change first line: Card #,Card Description,Trx Date,Transaction #,Store Number,Store City,Store State,Country,Product,Driver,Odometer,Trailer,Trip,Vehicle,Quantity,Fuel,Merchandise,Detail Total,Invoice Amount

# input format (PFJ): Card #,Card Description,Trx Date,Transaction #,Store Location,Product,Driver ID,Odometer,
# Trailer,Trip,Vehicle ID,Quantity,Fuel,Merchandise,Detail Total,Invoice Amt output format (Keep Truckin): Date', ',
# Time (UTC)', ',Jurisdiction', ',Driver,Vehicle', ',Fuel Type', ',Gallons/Liters', ',Volume', ', USD/CAD', ',
# Total Cost', ',Vendor Name', ', Location,Miles/Kilometers,Odometer,Reference #,Notes


def merge():
    merged_data = pd.DataFrame()
    for f in glob.glob("/Users/yingfeng/PycharmProjects/PFJ>KT/merge/*.xlsx"):
        merged_data = pd.read_excel(f)
        merged_data = merged_data.append(merged_data, ignore_index=True)
    print(merged_data.to_string())
    merged_data.to_csv("new_combined_file.csv")
    # merge all excel under one directory, output as "input.csv"
    # for use when cannot export as quarters
    # TODO merge excel


def import_csv():
    data_read = pd.read_csv('input.csv')
    return data_read


# Write CSV file
'''with open('test.csv', 'wt') as fp:
    writer = csv.writer(fp, delimiter=',')
    # writer.writerow(['your', 'header', 'foo'])  # write header
    writer.writerows(data)'''


def split_date_time(date):
    # 6/30/2021 9:44 AM
    # date =
    date_time = datetime.strptime(date, '%m/%d/%Y %H:%M %p')
    # mm/dd/yyyy
    date = date_time.strftime('%m/%d/%Y')

    # hhmm in UTC
    time = date_time.strftime('%H%M')
    # print(date)
    # print(time)
    return date, time


def fuel_tax():
    data_read = import_csv()
    print(data_read.to_string())
    # print initial data

    # split_date_time('6/30/2021 9:44')
    # data_diesel = data_read.query('Product == `TruckDiesel`')
    # data_diesel = data_read.reset_index(drop=True)

    '''for index, row in data_read.iterrows():
        if data_read'''
    data_diesel = data_read[data_read['Product'].str.contains('Truck Diesel', na=False)]
    data_diesel.reset_index(inplace=True, drop=True)
    # remove none Truck Diesel data, reset index
    print(data_diesel.to_string())
    # print corrected data
    data_export = pd.DataFrame(
        columns=['Date', 'Time(UTC)', 'Jurisdiction', 'Driver', 'Vehicle', 'Fuel Type', 'Gallons/Liters', 'Volume',
                 'USD/CAD', 'Total Cost', 'Vendor Name', 'Location', 'Miles/Kilometers', 'Odometer', 'Reference #',
                 'Notes'])
    data_diesel_date = data_diesel["Trx Date"]
    data_diesel_store = data_diesel["Store Number"].astype(int)
    data_diesel_state = data_diesel["Store State"]
    data_diesel_volume = data_diesel["Quantity"]
    data_diesel_vehicle = data_diesel["Vehicle"].astype(int)
    data_diesel_invoice_amount = data_diesel["Invoice Amount"]

    # Fuel Type*, Gallons/Liters*, USD/CAD* fill
    # print(data_diesel_date.to_string())

    data_diesel_converted_time = pd.DataFrame(columns=['Date', 'Time(UTC)'])

    for index, row in data_diesel.iterrows():
        # split_date_time(row['Trx Date'])

        # print(row['Trx Date'])
        d, t = split_date_time(row['Trx Date'])
        temp_d_t = [d, t]
        # append split date and time to data_diesel_converted_time
        data_diesel_converted_time.append(temp_d_t)
        data_diesel_converted_time_length = len(data_diesel_converted_time)
        data_diesel_converted_time.loc[data_diesel_converted_time_length] = temp_d_t

    print(data_diesel_converted_time.to_string())
    # data_export = pd.concat([data_diesel_converted_time, data_diesel_state, data_diesel_vehicle, data_diesel_vehicle])

    # dump data into export csv
    data_export['Date'] = data_diesel_converted_time['Date']
    data_export['Time(UTC)'] = data_diesel_converted_time['Time(UTC)']
    data_export['Jurisdiction'] = data_diesel_state
    data_export['Fuel Type'] = DEFAULT_FUEL
    data_export['Gallons/Liters'] = DEFAULT_UNIT
    data_export['USD/CAD'] = DEFAULT_CURRENCY
    for index, value in data_diesel_vehicle.items():
        try:
            value = int(value)
        except:
            value = 0
        data_diesel_vehicle[index] = value
    # TODO: fix error
    print(data_diesel_vehicle.to_string())
    data_export['Vehicle'] = data_diesel_vehicle
    data_export['Volume'] = data_diesel_volume
    # TODO: fix error
    for index, value in data_diesel_invoice_amount.items():
        try:
            value = str(value).replace('$', '')
        except:
            None
        data_diesel_invoice_amount[index] = value
    data_export['Total Cost'] = data_diesel_invoice_amount

    # data_diesel_store = data_diesel_store.astype(int)
    # .astype returns an array

    for index, value in data_diesel_store.items():
        value = "PFJ #" + str(value)
        data_diesel_store[index] = value
    # TODO: fix error
    print(data_diesel_store.to_string())
    data_export['Vendor Name'] = data_diesel_store

    print(data_export.to_string())
    # TODO: export vehicle, store number as integer
    return data_export.to_csv('output.csv', sep=',', index=False)


def replace_first_line():
    with open("output.csv") as f:
        lines = f.readlines()

    lines[0] = "Date*,Time (UTC)*,Jurisdiction*,Driver,Vehicle*,Fuel Type*,Gallons/Liters*,Volume*,USD/CAD*,Total Cost*,Vendor Name*,Location,Miles/Kilometers,Odometer,Reference #,Notes\n"

    with open("output.csv", "w") as f:
        f.writelines(lines)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    merge()
    print()
    fuel_tax()
    replace_first_line()
