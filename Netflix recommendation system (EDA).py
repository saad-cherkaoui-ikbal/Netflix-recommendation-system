%matplotlib notebook

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import regex as re
from datetime import datetime
import calendar
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.gridspec as gridspec

data = pd.read_csv('netflix_titles.csv')
data.shape #(7787, 12)

# in the country column, all countries that were involved in the production were included
# in the cast column, all actors were included
# in listed_in column, all genres that can be applied were included
# in the duration column, it can be either the number of seasons, or the length in minutes


## Checking for missing values

def missing(df):
    miss = df.isna().sum().sort_values(ascending=False)
    
    miss_percent = 100 * df.isna().sum()//len(df)
    miss_table = pd.concat([miss, miss_percent], axis=1).rename(columns = {0 : 'Missing Values', 1 : '% Value'})
    
    cm = sns.light_palette('black', as_cmap=True)
    miss_table = miss_table.style.background_gradient(cmap=cm)
    
    return miss_table
missing(data) # this returns a dataframe with the number of missing values and the percentages for each column


## In order to visualize the distribution of countries/actors/genres across the dataset, 
## the following function helps separate the names and genres when there's more than one :

from collections import Counter

def count(data, column) :
    return Counter([thing.strip() for thing in data[column].fillna('missing') for thing in thing.split(',')])

actor_count = count(data, 'cast') # the occurrence of each individual genre actor in the dataset
country_count = count(data, 'country') # the occurrence of each individual country in the dataset
genre_count = count(data, 'listed_in') # the occurrence of each individual genre in the dataset

 # An additional function that can be useful later on :
 
 def mask(x, column) :
    return data[column].fillna('missing').apply(lambda z: x in z)    
 # this function returns the part of the dataframe that verifies the condition
 
 
 
 ####### Vizualisation
 
 ## This first function allows to plot a bar chart, showing the distributions of Movies/TV Shows across countries for a specific period of time
 ## The 'indiv' paramater can also be changed to plot the distributions across genres too
 
 def involvment_plot(data, indiv='country', num=10, year1=data['release_year'].min(), year2=data['release_year'].max()) :

    plt.figure(figsize=(20,10))
    
    top = count(data[(data['release_year']>=year1) & (data['release_year']<=year2)], indiv).most_common()[:num]
    data = data[(data['release_year']>=year1) & (data['release_year']<=year2)]
    
    i=0
    bar_labels=[]
    x_pos=[]

    for l in top :
        lol = l[0]
        a = data[mask(lol, indiv)].groupby('type').size()
        if 'Movie' in data[mask(lol, indiv)].groupby('type').size().index :
            bars = plt.bar(0+i, a['Movie'], width=0.2, color='blue', edgecolor='black', alpha=0.8)
            for bar in bars:
                plt.gca().text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(bar.get_height()), 
                         ha='center', fontsize=11)
        if 'TV Show' in data[mask(lol, indiv)].groupby('type').size().index :
            bars = plt.bar(0.2+i, a['TV Show'], width=0.2, color='blue', edgecolor='black', alpha=0.3)
            for bar in bars:
                plt.gca().text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(bar.get_height()), 
                         ha='center', fontsize=11)
        bar_labels+=[lol]
        x_pos+=[0.1+i]
        i+=0.5
    _=plt.xticks(x_pos, bar_labels)
    _=plt.legend(['Movies', 'Tv-shows'])
    _=plt.title('{} involvement in \nMovies/TV-shows'.format(indiv), y=1.0, pad=-50, fontsize=20)
    plt.tick_params(
        axis='both',          # changes apply to the y-axis
        which='both',      # both major and minor ticks are affected
        left=False,        # ticks along the bottom edge are off
        labelleft=False,   # labels of left axis are off
        right=False,       # ticks along the top edge are off (no need)
        bottom=False)

involvment_plot(data, indiv='listed_in', num=20, year1=2019, year2=2020) ## distributions across countries for the period [2019, 2020]
x = plt.gca().xaxis
for item in x.get_ticklabels() :
    item.set_rotation(20)
    

# Another interesting thing to do is to plot a dynamic pie chart that shows the distribution of Movies/TV Shows across different periods of time
# This plot clearly shows that that there has been a surge in the production of tv shows in the last 5 years

plt.figure()

def type_pie(data=data, year1=data['release_year'].min(), year2=data['release_year'].max()) :
    data = data[(data['release_year']>=year1) & (data['release_year']<=year2)]
    a = data.groupby('type').size()
    _=my_plt.pie(a, labels=a.index, autopct='%1.1f%%')

gdspec = gridspec.GridSpec(4, 4)
my_plt = plt.subplot(gdspec[0:5, 0:5])

start=1980
end=2010
type_pie(data, year1=start, year2=end)
_=my_plt.set_title('Movie/Tv Show distribution by date release\n from {} to {}'.format(int(start), int(end)), y=1.0, pad=-20, fontsize=10)


axcolor = 'lightgoldenrodyellow'
axyear1 = plt.axes([0.16, 0.1, 0.7, 0.03], facecolor=axcolor)
axyear2 = plt.axes([0.16, 0.05, 0.7, 0.03], facecolor=axcolor)

syear1 = Slider(axyear1, 'Start', data['release_year'].min(), data['release_year'].max(), valinit=start)
syear2 = Slider(axyear2, 'End', data['release_year'].min(), data['release_year'].max(), valinit=end)


def update(val):
    start = syear1.val
    end = syear2.val
    my_plt.cla()
    type_pie(data, year1=start, year2=end)
    plt.gcf().canvas.draw_idle()
    _=my_plt.set_title('Movie/Tv Show distribution by date release\n from {} to {}'.format(int(start), int(end)), y=1.0, pad=-20, fontsize=10)


syear1.on_changed(update)
syear2.on_changed(update)

# In terms of the date Movies/TV Shows were added to the Netflix catalogue, it would be interesting to see how content was added throughout the years

plt.figure()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15,5))


# Movies/TV Shows included by year

def count_year(data) :
    return Counter([datetime.strptime(date.strip(), '%B %d, %Y').year for date in data[~data['date_added'].isnull()]['date_added'] ])

x = count_year(data[data['type']=='Movie'])
x1 = sorted(x.items(), key=lambda pair: pair[0], reverse=True)
a, b = zip(*x1)
ax1.plot(a, b, '-o', label='Movies')

y = count_year(data[data['type']=='TV Show'])
y1=sorted(y.items(), key=lambda pair: pair[0], reverse=True)
a, b = zip(*y1)
ax1.plot(a, b, '-o', label='TV Shows')

z = count_year(data)
z1=sorted(z.items(), key=lambda pair: pair[0], reverse=True)
a, b = zip(*z1)
ax1.plot(a, b, '-o', label='All')

ax1.legend()
_=ax1.set_title('Movies/TV Shows added\n by year')

# Movies/TV Shows included by month

def count_month(data) :
    return Counter([datetime.strptime(date.strip(), '%B %d, %Y').month for date in data[~data['date_added'].isnull()]['date_added'] ])

x = count_month(data[data['type']=='Movie'])
x1 = sorted(x.items(), key=lambda pair: pair[0])
a, b = zip(*x1)
ax2.plot([calendar.month_abbr[l] for l in a], b, '-o', label='Movies')

y = count_month(data[data['type']=='TV Show'])
y1=sorted(y.items(), key=lambda pair: pair[0])
a, b = zip(*y1)
ax2.plot([calendar.month_abbr[l] for l in a], b, '-o', label='TV Shows')

z = count_month(data)
z1=sorted(z.items(), key=lambda pair: pair[0])
a, b = zip(*z1)
ax2.plot([calendar.month_abbr[l] for l in a], b, '-o', label='All')

ax2.legend()
_=ax2.set_title('Movies/TV Shows added\n by month')

# We can clearly see from the first plot the beginning of Netflix's streaming service in 2007, after which content rapidly increased throughout the years
# The second plot shows that there might be a monthly seasonal effect, this requires further testing

## In order to fully take advantage of the 'rating' column, a bit of research was conducted which resulted in putting all the Movies/TV Shows into 5 distinct categories

kids = ['TV-Y', 'TV-Y7', 'TV-Y7-FV']
allpublic = ['G', 'TV-G']
supervision = ['PG', 'PG-13', 'TV-PG', 'R']
mature = ['TV-MA', 'TV-14', 'NC-17']
unrated = ['NR', 'UR']

my_dict = {
    **dict.fromkeys(kids, 'kids'),
    **dict.fromkeys(allpublic, 'all public'),
    **dict.fromkeys(supervision, 'with supervision'),
    **dict.fromkeys(mature, 'mature'),
    **dict.fromkeys(unrated, 'unrated'),
}

data['category'] = data['rating'].replace(my_dict).fillna('missing') # adding a 'category' column to the dataset

## Now from some plotting : a pie chart that shows the distribution of categories in the data, across the selected periods of time
## It's worth noting that the mask() function defined previously can be used to only show the distribution for a specified country

def pie_category(data) :    
    plt.figure()

    def category_pie(data=data, year1=data['release_year'].min(), year2=data['release_year'].max()) :
        data = data[(data['release_year']>=year1) & (data['release_year']<=year2)]
        a = data.groupby('category').size()
        if 'missing' in a.index:       
            a.drop('missing', axis=0, inplace=True)
        _=my_plt.pie(a, labels=a.index, autopct='%1.1f%%')

    gdspec = gridspec.GridSpec(4, 4)
    my_plt = plt.subplot(gdspec[0:5, 0:5])

    start=1980
    end=2010
    category_pie(data, year1=start, year2=end)
    _=my_plt.set_title('Category distribution from {} to {}'.format(int(start), int(end)), y=1.0, pad=-20, fontsize=10)


    axcolor = 'lightgoldenrodyellow'
    axyear1 = plt.axes([0.16, 0.1, 0.7, 0.03], facecolor=axcolor)
    axyear2 = plt.axes([0.16, 0.05, 0.7, 0.03], facecolor=axcolor)

    syear1 = Slider(axyear1, 'Start', data['release_year'].min(), data['release_year'].max(), valinit=start)
    syear2 = Slider(axyear2, 'End', data['release_year'].min(), data['release_year'].max(), valinit=end)


    def update(val):
        start = syear1.val
        end = syear2.val
        my_plt.cla()
        category_pie(data, year1=start, year2=end)
        plt.gcf().canvas.draw_idle()
        _=my_plt.set_title('Category distribution from {} to {}'.format(int(start), int(end)), y=1.0, pad=-20, fontsize=10)


    syear1.on_changed(update)
    syear2.on_changed(update)

pie_category(data[mask('Canada', 'country')]) # The distribution across categories in Canada (the period can be chosen dynamically thanks to the "nbAgg" matplotlib backend

## A lot can be done with this dataset in terms of exploratory data analysis, 
## but I will stop here for now and move on to building the recommendation engine in the next document
