import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st


def convert(x):
    try:
        return pd.to_datetime(x, format='%B %d, %Y %H:%M')
    except Exception:
        try:
            return pd.to_datetime(x, format='%B %d, %Y %H:%M (EDT)')
        except Exception:
            return pd.to_datetime(x, format='%B %d, %Y')


def plot_by_drug(df, medicine, x_interval=2):
    fa = df.copy()
    fa['Farmaci'] = fa['Farmaci'].dropna()

    def fi(x):
        try:
            return x.find(medicine) > -1
        except:
            return False

    fa[medicine] = fa['Farmaci'].apply(fi)
    dfa = fa[fa[medicine]]

    dfa = dfa.set_index('Date')
    dfa = dfa['Tipo']
    dfa = dfa.reset_index()
    dfa['Tipo'] = dfa['Tipo'].apply(lambda x: type_to_number(x))
    fig = dfa.plot(x='Date', y='Tipo', kind='scatter', figsize=(16, 9), rot=45)
    fig.axhline(y=2.5, color='g', linestyle='-')
    fig.axhline(y=4.5, color='g', linestyle='-')
    fig.xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))
    fig.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    grouped_by_type = dfa
    grouped_by_type['Tipo'] = grouped_by_type['Tipo'].apply(
        lambda x: number_to_type(x))
    grouped_by_type = grouped_by_type.groupby('Tipo').count()
    grouped_by_type = grouped_by_type[['Date']]
    grouped_by_type.plot(kind='barh')
    return fig


def figure_to_be_plotted(df, x_interval=2):
    dfa = df.copy()
    dfa = dfa.set_index('Date')
    dfa = dfa['Tipo']
    dfa = dfa.reset_index()
    #dfa['Tipo'] = dfa['Tipo'].apply(lambda x: type_to_number(x))
    fig = dfa.plot(x='Date', y='Tipo', kind='scatter', figsize=(16, 9), rot=45)
    fig.axhline(y=2.5, color='g', linestyle='-')
    fig.axhline(y=4.5, color='g', linestyle='-')
    fig.xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))
    fig.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    return fig


def plot_by_type(df, x_interval=2):
    rr = df[['Date', 'Tipo']]
    tplot = rr.plot(x='Date', y='Tipo', kind='scatter',
                    figsize=(26, 9), rot=45)
    tplot.axhline(y=2.5, color='g', linestyle='-')
    tplot.axhline(y=4.5, color='g', linestyle='-')
    tplot.xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))
    tplot.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    # tplot.gcf().autofmt_xdate()
    return tplot


def type_to_number(x):
    type_to_number = {
        '5- Frammenti morbidi con bordi ben definiti': 5,
        '4- morbide a forma di salsiccia o serpente': 4,
        '3- a salsiccia con crepe in superficie': 3,
        '6- Frammenti morbidi con bordi frastagliati': 6,
        '7- liquide senza pezzi solidi': 7,
        '2- a forma di salsiccia nodose': 2,
        '1- a palline feci caprine feci a scibala': 1,
        'Non determinato': 0
    }
    return type_to_number[x]


def number_to_type(x):
    number_to_type = {
        5: '5- Frammenti morbidi con bordi ben definiti',
        4: '4- morbide a forma di salsiccia o serpente',
        3: '3- a salsiccia con crepe in superficie',
        6: '6- Frammenti morbidi con bordi frastagliati',
        7: '7- liquide senza pezzi solidi',
        2: '2- a forma di salsiccia nodose',
        1: '1- a palline feci caprine feci a scibala',
        0: 'Non determinato'
    }
    return number_to_type[x]


def type_bucketize(x, min, max):
    if x < min:
        return 'Stitichezza'
    elif x <= max:
        return 'Normale'
    else:
        return 'Diarrea'


def get_unique_strings(input_list):
    split_strings = []
    for string in input_list:
        chunks = []
        for chunk in str(string).split(','):
            chunks.append(chunk.strip())
        split_strings += chunks
    return list(set(split_strings))


def plot_by_values(df, values, figsize=(16, 9)):
    if (len(values) > 0 and len(df) > 0):
        counter = dict()
        for symptom in values:
            s = df[symptom].value_counts()
            counter[symptom] = s.to_dict()[True] if True in s else 0

        plt_dataframe = pd.DataFrame.from_dict(counter, orient='index')
        pie_plot = plt_dataframe.plot(
            kind='pie', figsize=figsize, subplots=True)
        return pie_plot[0].figure
    else:
        return None
