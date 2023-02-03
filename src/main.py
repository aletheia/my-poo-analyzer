import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

from utils import convert, plot_medicine, plot_by_type, type_to_number, number_to_type

csv_path = './export.csv'

df = pd.read_csv(csv_path)

# st.set_page_config(layout="wide")
st.title('My Poo analyzer')


# Convert and normalize dataset
df['Date'] = df['Date'].apply(convert)
df = df.rename(columns={'Farmaci (da <12h)': 'Farmaci',
               'Variazioni nella dieta (ultime 24h)': 'Variazioni'})

dd = df.copy()
dd = dd.dropna(how='all')
dd['Tipo'] = dd['Tipo'].apply(lambda x: type_to_number(x))
dd = dd[dd['Tipo'] > 0]


# Sidebar
start_date = st.sidebar.date_input('Start date', value=df['Date'].min())
end_date = st.sidebar.date_input('End date', value=df['Date'].max())
type_range = st.sidebar.slider('Tipo - Range normalità', 0, 7, (3, 5))
st.sidebar.write(f'Stitichezza: tipo < {type_range[0]}')
st.sidebar.write(
    f'Normale: tipo >= {type_range[0]} e =< {type_range[1]}')
st.sidebar.write(f'Diarrea: tipo > {type_range[1]}')

# Filter dataset by date
dd = dd[dd['Date'] >= pd.to_datetime(start_date)]
dd = dd[dd['Date'] <= pd.to_datetime(end_date)]

st.write(f'Analisi dei dati dal {start_date} al {end_date}')


st.markdown('---')

st.markdown('## Analisi per tipologia')
tplot = plot_by_type(dd)
st.pyplot(tplot.figure)

st.markdown('### Riclassificazione')
st.text('Rappresentazione del dataset in base relativamente al tipo (secondo la scala di Bristol) come classificato, raggruppato per date, conteggiando il numero di eventi di una determinata tipologia')

grouped_by_type = df.groupby('Tipo').count()
grouped_by_type = grouped_by_type[['Date']]
gplot = grouped_by_type.plot(kind='barh')
st.pyplot(gplot.figure)

st.write('Rappresentazione del dataset in base relativamente al tipo (secondo la scala di Bristol) come classificato, raggruppato per date, conteggiando il numero di eventi di una determinata tipologia')

bucketed_by_type = dd.copy()


def classify(x):
    if x < type_range[0]:
        return 'Stitichezza'
    elif x <= type_range[1]:
        return 'Normale'
    else:
        return 'Diarrea'


bucketed_by_type['Tipo'] = bucketed_by_type['Tipo'].apply(classify)
bucketed_by_type = bucketed_by_type.groupby('Tipo').count()
bucketed_by_type = bucketed_by_type[['Date']]
bplot = bucketed_by_type.plot(kind='pie', subplots=True, figsize=(10, 10))
st.pyplot(bplot[0].figure)

st.markdown('---')

st.markdown('## Analisi per data')
st.write('Classificazione dei dati in base alla data dell\'evento')

median = dd['Tipo'].median()
mode = median = dd['Tipo'].mode()[0]
st.write(
    f'La mediana delle evacuazioni è {number_to_type(median)}. \nLa moda è {number_to_type(mode)}')

st.markdown('### Giorni normali e giorni con colite')
byDate = dd.copy()
byDate['Date'] = byDate['Date'].dt.date
bd = byDate.groupby('Date')['Tipo'].max()
bd = bd.reset_index()
days_w_diarrhea = bd[bd['Tipo'] > type_range[1]]['Date'].count()
days_w_normal = bd[(bd['Tipo'] <= type_range[1]) &
                   (bd['Tipo'] > 2)]['Date'].count()

st.write(f'Su un totale di {len(bd)} giorni si sono verificati '
         f'{days_w_normal} con alvo normale, '
         f'{days_w_diarrhea} con almeno un episodio di diarrea.')

st.markdown('### Analisi per giorno della settimana')
fc = byDate[['Date', 'Tipo']].groupby('Date').count()
fcplot = fc.plot(kind='bar', figsize=(16, 9))
st.pyplot(fcplot.figure)

st.write(f'La media di evacuazioni giornaliere è {fc["Tipo"].mean()}.\n'
         f'Giornalmente è più frequente il caso con mediana {fc["Tipo"].median()} evacuazioni'
         f'e moda {fc["Tipo"].mode()[0]} evacuazioni')

st.markdown('---')

st.markdown('## Analisi in base al farmaco assunto')
st.write('Classificazione dei dati in base al farmaco assunto')
st.write('### Farmaci assunti')


def get_unique_strings(input_list):
    split_strings = []
    for string in input_list:
        chunks = []
        for chunk in str(string).split(','):
            chunks.append(chunk.strip())
        split_strings += chunks
    return list(set(split_strings))


dlist = df['Farmaci'].unique().tolist()
drugs = get_unique_strings(dlist)
drugs.sort()
# drugs = list(set(''.join(' ').split(',')))
st.sidebar.write('Farmaci assunti')
selected_drug = st.sidebar.selectbox('Farmaco', drugs)

drug_plot = plot_medicine(df, selected_drug)
st.pyplot(drug_plot.figure)
