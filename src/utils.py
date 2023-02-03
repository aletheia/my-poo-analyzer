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


def plot_medicine(df, medicine, x_interval=2):
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
    fig = dfa.plot(x='Date', y='Tipo', kind='scatter', figsize=(16, 9))
    fig.axhline(y=2.5, color='g', linestyle='-')
    fig.axhline(y=4.5, color='g', linestyle='-')
    fig.xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))
    fig.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

    # plt.gcf().autofmt_xdate()
    # ax.ylim([1, 7])

    grouped_by_type = dfa
    grouped_by_type['Tipo'] = grouped_by_type['Tipo'].apply(
        lambda x: number_to_type(x))
    grouped_by_type = grouped_by_type.groupby('Tipo').count()
    grouped_by_type = grouped_by_type[['Date']]
    grouped_by_type.plot(kind='barh')
    return fig


def plot_by_type(df):
    rr = df[['Date', 'Tipo']]
    tplot = rr.plot(x='Date', y='Tipo', kind='scatter', figsize=(26, 9))
    tplot.axhline(y=2.5, color='g', linestyle='-')
    tplot.axhline(y=4.5, color='g', linestyle='-')
    tplot.xaxis.set_major_locator(mdates.DayLocator(interval=1))
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
