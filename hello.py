from flask import Flask, render_template, request, jsonify, redirect, url_for
import csv
from phase3 import main_function as mf, secondary_function as sf

app = Flask(__name__)

deref = {'Subdivision': 0, 'Regions': 1, 'Crimes': 2, 'Specific Offence': 3}

# Access data
f = open("NSW_crimedata.csv")
reader = csv.reader(f)
header = reader.next()
# Create Arrays of unique values
division = []
regions = []
crimes = []
crime_categories = []

for i in reader:
    division.append(i[0])
    regions.append(i[1])
    crimes.append(i[2])
    crime_categories.append(i[3])

division = set(division)
regions = set(regions)
crimes = set(crimes)
crime_categories = set(crime_categories)

# Create array of years and months
years = ['1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008',
         '2009', '2010', '2011', '2012']
months = ['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']
f.close()


# --------------------------------------------------------------------------------------------

@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/pivot/')
def pivot():
    return render_template('index.html', crimes=crimes, crime_categories=crime_categories, regions=regions,
                           division=division, years=years, months=months)


@app.route('/statistics', methods=['GET', 'POST'])
def display():
    # Take initial filters
    category1 = request.form['category1_input']
    category2 = request.form['category2_input']
    # Take optional filters
    subcategory1 = request.form['sub_category1_input']
    subcategory2 = request.form['sub_category2_input']

    # Title of graph
    title = str(category1) + " Vs " + str(category2)
    if category2 in ['Years', 'Months']:
        category2 = category2.lower()[:-1]  # un-capitalize and drop the last s
        mf(deref[category1], title, 0, 15000000, category2)
    elif category2 in deref.keys():
        sf(deref[category1], deref[category2], title)
    else:
        return render_template('Error.html')
    return render_template('output_stats.html')


@app.route('/observations')
def observations():
    return render_template('observations.html')


@app.route('/graph')
def graph():
    return render_template('output_graph.html')


if __name__ == '__main__':
    app.run(debug=True)
