import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

from utils import convert, plot_by_drug, plot_by_type, type_to_number, number_to_type, type_bucketize, get_unique_strings, figure_to_be_plotted, plot_by_values

csv_path = './export.csv'

df = pd.read_csv(csv_path)

# st.set_page_config(layout="wide")
st.title('My Poo analyzer')


# Convert and normalize dataset
df['Date'] = df['Date'].apply(convert)
df = df.rename(columns={'Farmaci (da <12h)': 'Farmaci',
               'Variazioni nella dieta (ultime 24h)': 'Variazioni',
                        'Altri sintomi': 'Sintomi',
                        })
dd = df.copy()
dd = dd.dropna(how='all')
dd = dd.drop(columns=['Nastriformi?'], axis=1)
dd['Tipo'] = dd['Tipo'].apply(lambda x: type_to_number(x))
dd = dd[dd['Tipo'] > 0]

# Build unique drugs list
drug_list = dd['Farmaci'].unique().tolist()
drug_list = get_unique_strings(drug_list)
drug_list = [x for x in drug_list if (x != 'nan') & (x != '<NA>') & (x != '')]
drug_list.sort()

# Build unique diet list
diet_list = dd['Variazioni'].unique().tolist()
diet_list = get_unique_strings(diet_list)
diet_list = [x for x in diet_list if (x != 'nan') & (x != '<NA>') & (x != '')]
diet_list.sort()

# Build unique symptoms list
symptoms_list = dd['Sintomi'].unique().tolist()
symptoms_list = get_unique_strings(symptoms_list)
symptoms_list = [x for x in symptoms_list if (
    x != 'nan') & (x != '<NA>') & (x != '')]
symptoms_list.sort()

# Sidebar
st.sidebar.markdown('## Filtri')
st.sidebar.markdown('### Date')
start_date = st.sidebar.date_input('Data di inizio', value=df['Date'].min())
end_date = st.sidebar.date_input('Data di fine', value=df['Date'].max())

st.sidebar.markdown('---')
st.sidebar.markdown('### Tipo')
type_range = st.sidebar.slider('Tipo - Range normalità', 0, 7, (3, 5))
st.sidebar.markdown(
    f'##### Stitichezza: tipo < {type_range[0]}  ')
st.sidebar.markdown(
    f'##### Normale: tipo >= {type_range[0]} e =< {type_range[1]} ')
st.sidebar.markdown(f'##### Diarrea: tipo > {type_range[1]}')

st.sidebar.markdown('---')
st.sidebar.markdown('#### Farmaci assunti')
selected_drug = st.sidebar.multiselect('Farmaco', drug_list)
st.sidebar.markdown('#### Variazioni nella dieta')
selected_diet = st.sidebar.multiselect('Variazione', diet_list)
st.sidebar.markdown('#### Sintomi')
selected_symptoms = st.sidebar.multiselect('Sintomo', symptoms_list)


# Filter dataset by date
dd = dd[dd['Date'] >= pd.to_datetime(start_date)]
dd = dd[dd['Date'] <= pd.to_datetime(end_date)]

dd['BucketedType'] = dd['Tipo'].apply(
    type_bucketize, args=(type_range[0], type_range[1]))

st.markdown(
    f'Analisi dei dati dal **{start_date.strftime("%d/%m/%Y")}** al **{end_date.strftime("%d/%m/%Y")}**')


dataset = dd.copy()


def fi(x, value):
    try:
        return x.find(value) > -1
    except:
        return False


for drug in drug_list:
    dataset[drug] = dataset['Farmaci'].apply(fi, args=(drug,))

for diet in diet_list:
    dataset[diet] = dataset['Variazioni'].apply(fi, args=(diet,))

for symptom in symptoms_list:
    dataset[symptom] = dataset['Sintomi'].apply(fi, args=(symptom,))

dataset = dataset[dataset['Date'] >= pd.to_datetime(start_date)]
dataset = dataset[dataset['Date'] <= pd.to_datetime(end_date)]


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
bucketed_by_type = bucketed_by_type[['Date', 'BucketedType']]
bucketed_by_type = bucketed_by_type.groupby('BucketedType').count()
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
st.markdown('---')
st.markdown('## Analisi in base al farmaco assunto')

top_data_container = st.container()
with top_data_container:
    left, right = st.columns(2)
    with left:
        st.markdown(
            f'**Farmaci assunti nel periodo {start_date} - {end_date}**')
        st.pyplot(plot_by_values(dataset, drug_list))
    with right:
        st.markdown(
            f'**Feci normali nel periodo {start_date} - {end_date} in relazione all\'assunzione di farmaci**')
        pl = plot_by_values(
            dataset[dataset['BucketedType'] == 'Normale'], drug_list)
        if (pl is not None):
            st.pyplot(pl)
        else:
            st.markdown('Nessun dato nel periodo selezionato')

st.markdown('---')
bottom_data_container = st.container()
with bottom_data_container:

    left, right = st.columns(2)
    with left:
        st.markdown(
            f'**Feci stitiche nel periodo {start_date} - {end_date} in relazione all\'assunzione di farmaci**')
        pl = plot_by_values(
            dataset[dataset['BucketedType'] == 'Stitichezza'], drug_list)
        if (pl is not None):
            st.pyplot(pl)
        else:
            st.markdown('Nessun dato nel periodo selezionato')

    with right:
        st.markdown(
            f'**Feci diarroiche nel periodo {start_date} - {end_date} in relazione all\'assunzione di farmaci**')
        pl = plot_by_values(
            dataset[dataset['BucketedType'] == 'Diarrea'], drug_list)
        if (pl is not None):
            st.pyplot(pl)
        else:
            st.markdown('Nessun dato nel periodo selezionato')


if len(selected_drug) > 0:
    st.markdown(
        f'Classificazione dei dati in base all\'assuzione di **{selected_drug}**')
else:
    st.markdown(
        f'Selezionare almeno un farmaco per visualizzare i dati')

rf = dataset.copy()
if (len(selected_drug) > 0):
    for drug in selected_drug:
        rf = rf[rf[drug]]
    drug_plot = figure_to_be_plotted(rf)
    st.pyplot(drug_plot.figure)

st.markdown('---')
st.markdown('## Analisi in base alle variazioni nella dieta')
st.pyplot(plot_by_values(dataset, diet_list))

if len(selected_diet) > 0:
    st.markdown(
        f'Classificazione dei dati in base ad una dieta di tipo **{selected_diet}**')
else:
    st.markdown(
        f'Selezionare almeno un regime alimentare per visualizzare i dati')

rf = dataset.copy()
if (len(selected_diet) > 0):
    for diet in selected_diet:
        rf = rf[rf[diet]]
    if len(rf) > 0:
        diet_plot = figure_to_be_plotted(rf)
        st.pyplot(diet_plot.figure)
    else:
        st.markdown('##### Nessun dato trovato')

st.markdown('---')

st.markdown('## Analisi in base ai sintomi')
st.pyplot(plot_by_values(dataset, symptoms_list))


if len(selected_symptoms) > 0:
    st.markdown(
        f'Classificazione dei dati in base ai sintomi **{selected_symptoms}**')
else:
    st.markdown(
        f'Selezionare almeno un sintomo per visualizzare i dati')

rf = dataset.copy()
if (len(selected_symptoms) > 0):
    for symton in selected_symptoms:
        rf = rf[rf[symton]]
    if len(rf) > 0:
        symton_plot = figure_to_be_plotted(rf)
        st.pyplot(symton_plot.figure)
    else:
        st.markdown('##### Nessun dato trovato')

st.markdown('---')
st.markdown('## Raw data')
st.dataframe(dataset)
