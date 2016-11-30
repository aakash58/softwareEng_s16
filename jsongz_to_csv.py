import json
import csv
import sys
import gzip
import glob
import os

flattened_object = {}


def to_string(s):
    try:
        return str(s)
    except:
        return s.encode("UTF-8")


def flatten_object(key, value):
    """ A dot notation is used to flatten a dict, keys incremented with index count are used in case of list """
    global flattened_object
    if type(value) is dict:
        sub_object_keys = value.keys()
        for sub_object_key in sub_object_keys:
            flatten_object(key + '.' + to_string(sub_object_key), value[sub_object_key])

    elif type(value) is list:
        for index, item in enumerate (value):
            flatten_object(key + '.' + to_string(index), item)

    else:
        flattened_object[to_string(key)] = to_string(value)


def csv_writer(file_name, columns, rows):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=columns)
        writer.writerow(dict(zip(columns, columns)))
        for row in rows:
            writer.writerow(row)

def process_json_file(file_name):
    """ Pass in the input json file and the output csv file will have the same name in the same path
        List can be of any size so need to create a set of columns and so some rows may have blank columns. """
    global flattened_object
    try:    # Because we have Python 2.6.x
        fp = gzip.open(file_name, 'rb')
    except IOError:
        print "No such gzip file found"
    else:
        archive = fp.readlines()
        fp.close()

    columns = []
    json_rows = []

    for object in archive:
        flattened_object = {}
        json_object = json.loads(object)

        for key, val in json_object.iteritems():
            flatten_object(key, val)
        columns += flattened_object.keys()
        json_rows.append(flattened_object)

    columns = list(set(columns))
    print len(json_rows)
    csv_writer(file_name + ".csv", columns, json_rows)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "\nUsage: python jsongz_to_csv.py <file_path_to_directory>"
    else:
        for file in glob.glob(os.path.join(sys.argv[1], '*.gz')):
            process_json_file(file)
