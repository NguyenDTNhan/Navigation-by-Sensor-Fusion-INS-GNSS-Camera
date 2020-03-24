"""
Function to read NMEA message from .csv file created by NTRIP client app (can
be any other software also, which records NMEA signals in a file line by line)

Input:
    - path: path including csv file
    - message: the message headline that you want to read e.g. '$GNGGA'

Output:
    - lat: latitude
    - lon: longitude
    - alt: Orthometric height (MSL reference) + geoid in meters
    - t: UTC of position fix in seconds
    - hor_dilut: horizontal dilution of precision (HDOP) in meters
    - h_geoid: geoid separation in meters

Reference: https://www.trimble.com/OEM_ReceiverHelp/V4.44/en/NMEA-0183messages_GGA.html
Author: Nhan Nguyen
Affiliation: Tampere University
Last Modified: 24th Mar 2020
"""

import csv

def read_ublox(path,message):
    #Initialize
    lat = []
    lon = []
    alt = []
    t = []
    hor_dilut = []
    h_geoid = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if row[0] == message:
                t.append(float(row[1]))
                lat_str = row[2]
                lat.append(float(lat_str[0:2]) + float(lat_str[2:]) / 60)
                lon_str = row[4]
                lon.append(float(lon_str[0:3]) + float(lon_str[3:]) / 60)
                h_geoid.append(float(row[11]))

                # Handle horizontal dilution string separately, e.g. measurement is 0,0411 -> 0.0411
                hor_str = row[8]
                idx_1 = hor_str.find(',')
                if idx_1 != -1:
                    hor_str = hor_str.replace(',', '.')
                hor_dilut.append(float(hor_str))
                # Handle altitude string separately, e.g. measurement is 144.01.00 -> 144.01
                alt_str = row[9]
                idx_1 = alt_str.find('.')
                idx_2 = alt_str.find('.', idx_1 + 1)
                if idx_2 == -1:
                    alt.append(float(alt_str) + float(row[11]))
                else:
                    alt.append(float(alt_str[:idx_2]) + float(row[11]))
    return lat, lon, alt, t, hor_dilut, h_geoid