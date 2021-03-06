# -*- coding: utf-8 -*-
import csv
from datetime import datetime


def parse(file_path, unit):
    """
    Parses the log file generated by the pOnewheel app and makes the data available through a list of dictionaries
    Each dictionary contains an entry for each column with the value found in the cell at that row
    """
    print 'Loading log file ', file_path, '...'
    data = []
    with open(file_path) as logfile:
        log_reader = csv.DictReader(logfile)
        for row in log_reader:
            data.append({
                'time': parse_millisecond_time(row['time']),
                'speed': parse_speed(row['speed'], unit),
                'battery': parse_battery(row['battery']),
                'roll': parse_angle(row['tilt_angle_roll'], invert=True),
                'pitch': parse_angle(row['tilt_angle_pitch']),
                'motor_temp': parse_temperature(row['motor_temp'], unit),
                'distance': parse_distance(row['odometer'], unit)
            })
    print 'Loaded ', len(data), 'rows'
    return data


def parse_distance(original, unit):
    """
    Converts the original distance to the desired unit system
    :param original:
    :param unit:
    :return:
    """
    if unit[0] == unit[1]:
        try:
            return float(original)
        except ValueError:
            return None
    if unit[1] == 'm':  # imperial to metric
        return mile_to_km(original)
    else:  # metric to imperial
        return km_to_mile(original)


def parse_speed(original, unit):
    """
    Converts the original speed to the desired unit system
    """
    return parse_distance(original, unit)


def parse_millisecond_time(time_str):
    """
    Parses the timestamp string to a datetime object. The timestamp string should fit the format
    yyyy-MM-dd'T'HH:mm:ss.SSSZ
    """
    # remove timezone info
    time_str = time_str[:-5]
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')


def parse_battery(charge):
    """
    Parses the battery value to an integer
    """
    try:
        return int(charge)
    except ValueError:
        return None


def parse_angle(angle_text, invert=False):
    """
    Converts the original angle to values between -180 and 180, with 0 being horizontal
    """
    try:
        angle = float(angle_text) / 10 - 180
        if invert:
            angle = -angle
        return angle
    except ValueError:
        return None


def parse_temperature(original, unit):
    """
    Converts the original temperature to the desired unit system
    """
    if unit[0] == unit[1]:
        try:
            return float(original)
        except ValueError:
            return None
    if unit[1] == 'm':  # imperial to metric
        return f_to_c(original)
    else:  # unit[1] == 'i'
        return c_to_f(original)


def mile_to_km(mile):
    """
    Converts Miles to Kilometers
    """
    try:
        return float(mile) * 1.609344
    except ValueError:
        return None


def km_to_mile(km):
    """
    Converts Kilometers to Miles
    """
    try:
        return float(km) / 1.609344
    except ValueError:
        return None


def f_to_c(f_temp):
    """
    Converts from Farenheint to Celsius
    """
    try:
        return (float(f_temp) - 32.0) * 5.0 / 9.0
    except ValueError:
        return None


def c_to_f(c_temp):
    """
    Converts from Celsius to Farenheint
    """
    try:
        return (float(c_temp) * 9.0 / 5.0) + 32.0
    except ValueError:
        return None
