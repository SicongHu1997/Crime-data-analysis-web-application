import csv
from collections import defaultdict as dd
import numpy as np
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
import random

# initialize jijna template and css for pivot table
style = """
    {% extends "header.html" %}
    {% block content %}
        <style>
        table {
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 95%;}
        td, th {
            border: 1px solid #dddddd;
            text-align: center;
            padding: 8px;
        }
        tr:nth-child(even) {
            background-color: #dddddd;
        }
        .btn{
            margin: 100px;
            align: centre;
        }
        </style>
        """
input_strings_rows = {0: 'sub-division', 1: 'regions', 2: 'offence', 3: 'crime'}
deref = {'Subdivision': 0, 'Regions': 1, 'Crimes': 2, 'Specific Offence': 3}

data = list(csv.reader(open('NSW_crimedata.csv', 'rU')))
headers = data[0]  # 1D list of column headings
rows = data[1:]  # 2D list of rows
columns = zip(*rows)  # 2D list of columns

unique_subdivs = list(set(columns[0]))
unique_lgas = list(set(columns[1]))
unique_offences = list(set(columns[2]))
unique_crimes = list(set(columns[3]))

subdiv_lgas_ref = dd(list)
for rowx in rows:
    if rowx[1] not in subdiv_lgas_ref[rowx[0]]:
        subdiv_lgas_ref[rowx[0]] += [rowx[1]]


def set_color(data_list):
    """
    :param data_list: The list of all values in the pivot table

    :return: A dictionary containing the values from the array(data_list) and its corresponding hex color value
    """
    data_list = np.unique(data_list)
    dic = {}
    order = 0
    for val in data_list:
        b = 0
        ratio = float(order) / (len(data_list) - 1)
        if ratio < 0.5:
            g = 255
            r = int(2 * 255 * ratio)
        else:
            r = 255
            g = int(255 - 2 * 255 * (ratio - 0.5))
        dic[val] = '#%02X%02X%02X' % (r, g, b)
        order += 1
    dic[0] = '#FFEEFF'
    return dic


def secondary_function(row_val, col_val, title, filterval='ALL YEARS', filterby=None,
                       filename='templates/output_stats.html'):
    """

    :param row_val:         Index of the row
    :param col_val:         Index of the column
    :param filename:        Output filename //blanked out later
    :param title:           // Title of the pivot table
    :param filterby:        'year' or 'subdiv'
    :param filterval:       the value of year or subdivision
    :return:
    """
    year_indices_dict = {}
    c = 4
    for i in range(1995, 2013):
        year_indices_dict[i] = c
        c += 12

    ret_dict = dd(int)
    uniquerows, uniquecols = list(set(columns[row_val])), list(set(columns[col_val]))

    for row in rows:
        if filterby is None:
            ret_dict[row[row_val] + row[col_val]] += sum(int(i) for i in row[4:])
        elif filterby == 'year':
            ret_dict[row[row_val] + row[col_val]] += sum(
                int(i) for i in row[year_indices_dict[filterval]:year_indices_dict[filterval] + 13])
        elif filterby == 'subdiv':
            if row[0] == filterval:
                ret_dict[row[row_val] + row[col_val]] += sum(int(i) for i in row[4:])
    values = sorted(ret_dict.values())
    colors_dict = set_color(values)
    s = ''
    s += style
    s += '''<H1><p align=center> {} </p></H1>\n'''.format(title + ('' if filterby is None else ' in ' + str(filterval)))
    s += '<BODY>\n'
    s += "<table border=2>\n"
    s += ' <tr>\n\t<td> &nbsp \t</td>\n'
    valid_rows_list = []
    for rowval in uniquerows:
        value = 0
        for colval in uniquecols:
            try:
                value += ret_dict[rowval + colval]
            except KeyError:
                pass
        if value != 0:
            valid_rows_list += [rowval]
    for colval in uniquecols:
        s += '\t<th>' + str(colval) + '\t</th>\n'
    for rowval in valid_rows_list:
        s += '\t<tr><th>' + str(rowval) + '\t</th>\n'
        for colval in uniquecols:
            try:
                value = ret_dict[rowval + colval]
                s += '\t<td bgcolor="{}" title="{}" >'.format(str(colors_dict[value]),
                                            colval + ' in ' + rowval if row_val < col_val else rowval + ' in ' + colval)
                s += str(value) + '\t</td>\n'
            except KeyError:
                pass
        s += '</tr>'
    s += '</table>\t</body><br><br><br>\n{%endblock%}'
    f = open(filename, 'w')
    f.write(s)
    f.close()


# secondary_function(0, 2, 'Subdiv V Off', unique_subdivs[random.randint(0, len(unique_subdivs))], 'subdiv')
# secondary_function(1, 3, 'LGA V Crimes')


def main_function(row_val, title, lowerbound, upperbound, input_type):
    """
    :param row_val:     The row code for input_one (referenced from input_string_rows line 6)
    :param title:       Title of the graph and Pivot Table (Leave '' for now)
    :param lowerbound:  Lowerbound of the data to be shown in pivot
    :param upperbound:  Upperbound ------------ "" ----------------
    :param input_type:  'year' or 'month'
    :return: calls the generate_html functions to create the pivot table and its graphical rep.
    """
    any_dict = dd(dict)
    year_keys = {}
    month_keys = {'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April', 'May': 'May', 'Jun': 'June',
                  'Jul': 'July', 'Aug': 'August', 'Sep': 'September', 'Oct': 'October', 'Nov': 'November',
                  'Dec': 'December', 1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                  7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
                  }

    for unique_rows in list(set(columns[row_val])):  # initialize  dictionary keys
        any_dict[unique_rows] = {}
    for row in rows:
        for header in headers:  # initialize the nested keys according to correct values
            if input_type == 'year':
                try:
                    year = int(header.split('-')[1])
                    if year + 2000 > 2012:
                        year_keys[year] = year + 1900
                    else:
                        year_keys[year] = year + 2000
                    any_dict[row[row_val]][year_keys[year]] = 0
                except IndexError:
                    pass

            elif input_type == 'month':
                try:  # initialize the nested keys according to correct values
                    month = header.split('-')[0]
                    any_dict[row[row_val]][month_keys[month]] = 0
                except KeyError:
                    pass
    for row in rows:
        if input_type == 'year':
            for i in range(4, len(headers), 12):  # populate the dictionary
                any_dict[row[row_val]][year_keys[int(headers[i].split('-')[1])]] += sum(int(x) for x in row[i:i + 12])
        elif input_type == 'month':
            for i in range(4, len(headers)):  # populate the dictionary
                any_dict[row[row_val]][month_keys[headers[i].split('-')[0]]] += int(row[i])
    if input_type == 'year':
        generate_html(any_dict, year_keys, title, lowerbound, upperbound)
    else:
        generate_html(any_dict, month_keys, title, lowerbound, upperbound)


def generate_html(dictionary, column_keys, title, lowerbound, upperbound):
    """
    :param dictionary:  The dictionary containing all values to be filled into the pivot table
    :param column_keys: Another dictionary to reference the values in the pivot table
    :param title:       The title of the Pivot Table (Supplied while calling location_v_years/(month)
    :param lowerbound:  Lowerbound of data to be included in the pivot table
    :param upperbound:  Upperbound ------------" "------------------------
    :return:    Generates the BODY of the Pivot table an stores it to statistics.html (your file Terry)

    """

    all_values_arr = []  # array to store values of the pivot table (conditional formatting purposes)

    maxval, minval = 0, float('inf')
    for value in dictionary.values():
        if sum(value.values()) in range(lowerbound, upperbound + 1):  # value satisfies filter add to pivot table
            all_values_arr += value.values()
        for datapoint in value.values():
            if datapoint > maxval:
                maxval = datapoint
            if datapoint < minval:
                minval = datapoint

    all_values_arr.sort()
    colors_dict = set_color(all_values_arr)
    # CODE BELOW MAKES THE HTML FILE AND CALLS THE GENERATE_GRAPH function
    s = ""
    s += style
    s += "<H1><p align=center>" + title + "</p></H1></HEAD>\n"
    s += '<BODY>\n'
    s += "<table border=2>\n"
    s += ' <tr>\n\t<td> &nbsp \t</td>\n'
    for year in sorted(list(set(column_keys.values()))):   # generate columns labels
        s += '\t<th>' + str(year) + '\t</th>\n'
    s += '\t<th> Total Crimes \t</th>\n'
    s += '</tr>\n'
    for region in sorted(dictionary.keys()):
        tempsum = sum(dictionary[region].values())          # row aggregated value
        if tempsum in range(lowerbound, upperbound + 1):
            s += '<tr>\n\t<th>' + str(region) + '\t</th>\n'     # row label
            for year in sorted(list(set(column_keys.values()))):
                try:
                    value = dictionary[region][year]
                    s += '\t<td bgcolor="{}" title="{}" >'.format(str(colors_dict[value]), 'Crimes in ' + region)
                    s += str(value) + '\t</td>\n'
                except KeyError:
                    pass
            s += '\t<td title = {}>'.format('Total Crimes in ' + region) + str(tempsum) + '\t</td>\n'
            s += '</tr>'
        else:
            dictionary.pop(region)          # value does not satisfy filters
    s += '</TABLE> \n'
    s += '\n </BODY>'
    # code below creates html file for pivot
    f = open('templates/output_stats.html', 'w')
    f.write(s)
    f.close()
    pivot_type = 'year'
    if 'January' in dictionary.values()[0]:
        pivot_type = 'month'
    generate_graph(dictionary, column_keys, pivot_type, lowerbound, upperbound, title)


def generate_graph(dictionary, column_keys, graph_type, lowerbound, upperbound, title):
    plt_wt, plt_ht = 1580, 750
    p = figure(plot_width=plt_wt, plot_height=plt_ht, toolbar_location='above')
    head = ''
    head += "<H1><p align=center>" + title + " Visualization </p></H1></HEAD>\n"
    if graph_type == 'year':
        sorted_years = sorted(column_keys.values())
        for area in sorted(dictionary.keys()):
            x_data = [dictionary[area][year] for year in sorted_years]
            if sum(x_data) in range(lowerbound, upperbound + 1):
                p.line(sorted_years, x_data, legend=area,
                       line_color="#%06x" % random.randint(0, 0xFFFFFF), line_width=1.4)
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "10pt"
    elif graph_type == 'month':
        sorted_years = [i for i in range(1, 13)]
        for area in sorted(dictionary.keys()):
            x_data = [dictionary[area][column_keys[year]] for year in sorted_years]
            if sum(x_data) in range(lowerbound, upperbound + 1):
                p.line(sorted_years, x_data, legend=area,
                       line_color="#%06x" % random.randint(0, 0xFFFFFF), line_width=1.4)
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "10pt"
    html = file_html(p, CDN, "my plot")
    graph_data = html[50:-7]
    head += graph_data
    head += '\n {%endblock%}'           # close off block
    with open('templates/output_stats.html', 'a') as f:
        f.write(head)
        # file = open("templates/output_graph.html", 'w')
        # file.write(head)
        # file.close()
