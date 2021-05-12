import streamlit as st
import altair as alt
import datetime
import pandas as pd
import numpy as np
from io import StringIO
import requests

# STREAMLIT ADJUSTMENTS
st.set_page_config(
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
	page_title='Dawn Till Dusk',  # String or None. Strings get appended with "• Streamlit".
	page_icon=':hibiscus:'  # String, anything supported by st.image, or None.
)
# hide hamburger menu (top right) and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# hide fullscreen button
# remove horizontal scrolling
hide_streamlit_fullscreen = """
  <style>
    /* Disable overlay (fullscreen mode) buttons */
    .overlayBtn {
      display: none;
    }

    /* Remove horizontal scroll */
    .element-container {
      width: auto !important;
    }

  </style>
"""
st.markdown(hide_streamlit_fullscreen, unsafe_allow_html=True)

###############################################
# Definitions
site_width=400
color_all = alt.Color('Geschlecht',
        title="",
        scale=alt.Scale(
            domain=['Herr','Frau','Junior'],
            range=['#f2b713','#f2dc13','#f26113'] # orange / yellow / redish
        ),
        legend=None
    )
color_all_legend = alt.Color('Geschlecht',
        title="",
        scale=alt.Scale(
            domain=['Herr','Frau','Junior'],
            range=['#f2b713','#f2dc13','#f26113'] # orange / yellow / redish
        )
    )
tooltip_all = [alt.Tooltip('id',title=None),
        alt.Tooltip('Km',format=',.0f'),
        alt.Tooltip('Höhenmeter',format='.0f'),
        alt.Tooltip('Technik',title='Stilart')
    ]

#####################################################################################
# READ Dummy DATA
#df_data_dummy = pd.read_excel("./test_data.xlsx",engine="openpyxl")#, skiprows=2,nrows=20)
def fill_with_dummy_data(df):
    # fill with dummy data to show plots
    df['Km'] = np.random.randint(80, 200, df.shape[0])
    df['Höhenmeter'] = np.random.randint(500, 2000, df.shape[0])
    return(df)

# READ FROM GOOGLE
st.cache(ttl=60*1)
def read_data():
    GOOGLE_SPREADSHEET = 'https://docs.google.com/spreadsheets/d/1mV3lzutv90A3xjoTANt1-qg7XxZ-8-7LkgdfldQr8CA/gviz/tq?tqx=out:csv'
    response = requests.get(GOOGLE_SPREADSHEET)
    assert response.status_code == 200, 'Wrong status code'
    response_string = response.content.decode('utf-8')
    TEST = StringIO(response_string)
    df_data_google = pd.read_csv(TEST, sep=',')
    # MOVE junior FROM 'Alterskategorie' INTO 'Geschlecht'
    df_data_google.loc[df_data_google['Alterskategorie']=='Junior*innen','Geschlecht'] = 'Junior'
    return(df_data_google)

# SHOW THE TEXT, WHAT IS IT ETC.
def show_infos():
    st.title(':bellhop_bell: __Format/Details__')

    st.write('''
    __Datum:__ 6.3.2021\n
    __Start:__ 06.49\n
    __Zielschluss:__ 18.13\n
    __Technik:__ frei wählbar

    __Sieger*in__: Wer am __meisten Kilometer__ läuft in dieser Zeit.
    Du bist eher der Typ "Bergfloh"? Dann laufe so viele __positiv Höhenmeter__ wie du kannst und sichere dir den ersten Rang in der Kategorie "Bergpreis".\n
    __Kategorien:__ Frauen, Männer, Junior*innen

    __Spezialwertung:__ Team Schweden vs. Team Doppelstock; weitere Battles sind gerne gesehen ;)

    __Messung:__ jede\*r Läufer\*in misst die Kilometer selbst mit einem Gerät/App nach Wunsch.

    __Reporting:__ Kilometer, Höhenmeter und Lauftechnik per Text/Whatsapp/etc an Michael +41 (0)79 961 73 12 bis um 20.00 Uhr am Tag des Rennens (6.3.2021) senden. 

    Bei Anregung oder Fragen, meldet euch einfach im Chat. 

    Wir freuen uns auf einen grossartigen Lauf!

    ''')

# SHOW COMPLETE RESULTS WITH PLOTS
def show_plots_seniors(df_selected, gender):
    ###########################
    # DISTANCE
    st.header(f':straight_ruler: __Distanz {gender}en__')
    df_selected = df_selected[(df_selected['Geschlecht']==gender)&(df_selected['Alterskategorie']=='Senior*innen')]
    # df_distance = df_selected#[['Km','Höhenmeter','Technik']]
    # df_distance['Rang'] = df_distance[['Km']].rank(ascending=False,method='min')
    # df_distance['Rang'] = df_distance['Rang'].astype(int)
    # df_distance = df_distance.sort_values(by=['Km'],ascending=False)
    # df_distance.loc[df_distance['Rang'] == 1,'Rang'] = ':trophy:'
    # df_distance.loc[df_distance['Rang'] == 2, 'Rang'] = ':second_place_medal:'
    # df_distance.loc[df_distance['Rang'] == 3, 'Rang'] = ':third_place_medal:'
    # for index, row in df_distance.iterrows():
    #     st.write(f"{row['Rang']:<20} {row['id']: <30}")

    chart_distance = alt.Chart(
        df_selected  # .sort_values(by='Km',ascending=False)
    ).mark_bar().encode(
        x='Km:Q',
        y=alt.Y('id', sort='-x', title=None),
        color=color_all,
        tooltip=tooltip_all
    )
    st.altair_chart(chart_distance, use_container_width=True)

    ###########################
    # ALTITUDE
    st.header(f':snow_capped_mountain: __Höhenmeter {gender}en__')
    chart_altitude = alt.Chart(
        df_selected
    ).mark_bar().encode(
        y='Höhenmeter:Q',
        x=alt.X('id', sort='-y',title=None),
        color= color_all,
        tooltip= tooltip_all
    )
    st.altair_chart(chart_altitude, use_container_width=True)

def show_plot_juniors(df_selected):
    ###########################
    # DISTANCE
    st.header(f':straight_ruler: __Distanz Junior*innen__')
    df_selected = df_selected[(df_selected['Alterskategorie']=='Junior*innen')]
    chart_distance = alt.Chart(
        df_selected  # .sort_values(by='Km',ascending=False)
    ).mark_bar().encode(
        x='Km:Q',
        y=alt.Y('id', sort='-x', title=None),
        color=color_all,
        tooltip=tooltip_all
    )
    st.altair_chart(chart_distance, use_container_width=True)

def show_combined_plot(df_selected, remaining_days):
    ###########################
    # COMBINED
    if (remaining_days) <= 0:
        st.title('Ausser Konkurrenz')
        st.header(':muscle: __Kombiniert__')
        selection_geschlecht = alt.selection_single(fields=['Geschlecht'], bind='legend')
        selection_technik = alt.selection_single(fields=['Technik'], bind='legend')

        chart_combi = alt.Chart(
            df_selected
        ).mark_point(filled=True, size=300).encode(
            y='Höhenmeter:Q',
            x=alt.X('Km'),
            color=color_all_legend,
            shape='Technik',
            tooltip=tooltip_all,
            opacity=alt.condition(selection_technik | selection_geschlecht, alt.value(1), alt.value(0.2))
        ).add_selection(selection_geschlecht, selection_technik)
        st.altair_chart(chart_combi, use_container_width=True)

def define_remaining_days_and_df():
    #################
    # CHOOSE DATE
    today = datetime.date.today()
    # for testing:
    #today = datetime.date(2021,3,6)
    # st.write(today)
    date_race = datetime.date(2021, 3, 6)
    remaining_days = (date_race - today).days
    df_data_google = read_data()
    df_selected = df_data_google
    # fill with dummy data for testing
    #df_selected = fill_with_dummy_data(df_data_google)

    # fill missing?
    df_selected['Technik'] = df_selected['Technik'].fillna(value='Klassisch/Skating')
    df_selected.loc[df_selected['Technik']=='-','Technik'] = 'Klassisch/Skating'
    # define id and set as index
    df_selected['id'] = df_selected['Vorname']+' '+df_selected['Name']
    df_selected = df_selected.set_index('id',drop=False)
    return(remaining_days, df_selected)

def count_by_gender(df_selected,gender):
    return(df_selected[df_selected['Geschlecht'] == gender]['Geschlecht'].count())

def show_prerace_stuff_vert(df_selected, remaining_days):
    if(remaining_days)>0:
        st.title(':sleeping_accommodation: __Nur noch {} Mal schlafen!__'.format(remaining_days))
        st.write('Noch nicht angemeldet? [Melde dich jetzt an!](http://bit.ly/3pg5KX3)')
        n_participants = df_selected['id'].count()
        st.subheader('Angemeldet sind momentan {} Langläufer\*innen'.format(n_participants))

       #col1, col2 = st.beta_columns(2)
       # df_selected['Anzahl Technik'] = df_selected.groupby('Technik')['Technik'].transform('count')
        df_selected['Anzahl Geschlecht'] = df_selected.groupby('Geschlecht')['Geschlecht'].transform('count')
        max_value = df_selected['Anzahl Geschlecht'].max()+1.5

        # chart_technik = alt.Chart(
        #     df_selected[['Technik','Anzahl Technik','Name']],
        #     height=300
        # ).mark_bar().encode(
        #     y=alt.Y('Anzahl Technik:Q', axis=None, scale=alt.Scale(domain=(0,max_value))),
        #     x=alt.X('Technik', sort='-y', title=None, axis=None)
        # )
        #
        # chart_technik_text = chart_technik.mark_text(
        #     align='center',
        #     baseline='middle',
        #     dy=-24,
        #     color='black'
        # ).encode(
        #     y=alt.Y('Anzahl Technik:Q'),
        #     x=alt.X('Technik', sort='-y', title=None, axis=None),
        #     text='Anzahl Technik:Q'
        # )
        #
        # chart_technik_text2 = chart_technik.mark_text(
        #     align='center',
        #     baseline='middle',
        #     dy=-10,
        #     color='black'
        # ).encode(
        #     y=alt.Y('Anzahl Technik:Q'),
        #     # y=alt.Value(0),
        #     x=alt.X('Technik', sort='-y', title=None, axis=None),
        #     text='Technik:N'
        # )
        #
        # chart_combined = chart_technik+chart_technik_text+chart_technik_text2
        # chart_combined.configure_view(strokeWidth=0)
        # col1.altair_chart(chart_combined, use_container_width=True)

        # KATEGORIE
        chart_kat = alt.Chart(
            df_selected[['Geschlecht', 'Anzahl Geschlecht', 'Name']],
            height=300
        ).mark_bar().encode(
            y=alt.Y('Anzahl Geschlecht:Q', axis=None, scale=alt.Scale(domain=(0,max_value))),
            x=alt.X('Geschlecht', sort='-y', title=None, axis=None),
            color=color_all
        )

        chart_kat_text = chart_kat.mark_text(
            align='center',
            baseline='middle',
            dy=-24,
            color='black'
        ).encode(
            y=alt.Y('Anzahl Geschlecht:Q'),
            x=alt.X('Geschlecht', sort='-y', title=None),
            text='Anzahl Geschlecht:Q'
        )

        chart_kat_text2 = chart_kat.mark_text(
            align='center',
            baseline='middle',
            dy=-10,
            color='white'
        ).encode(
            y=alt.Y('Anzahl Geschlecht:Q'),
            x=alt.X('Geschlecht', sort='-y', title=None),
            text='Geschlecht:N'
        )

        chart_combined = chart_kat + chart_kat_text + chart_kat_text2
        chart_combined.configure_view(strokeOpacity=0)
        st.altair_chart(chart_combined, use_container_width=True)

#####################################################################################
#####################################################################################
#####################################################################################

def main():
    # IMAGE
    st.image('banner_dawn_till_dusk.jpeg', width=site_width, use_column_width='always')
    remaining_days, df_selected = define_remaining_days_and_df()

    # SHOW GENERAL RULES AND INFOS
    show_infos()

    # SHOW PRERACE INFOS
    show_prerace_stuff_vert(df_selected, remaining_days)


    # SHOW THE RESULTS AND PLOTS
    st.title(':trophy: __Resultate__')
    show_plots_seniors(df_selected,'Frau')
    show_plots_seniors(df_selected,'Herr')
    # JUNIORS
    show_plot_juniors(df_selected)

    # SHOW POSTRACE STUFF
    show_combined_plot(df_selected, remaining_days)
    # FOOTER
    #st.write(':palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree:')
    st.write('----------------------------------------------')
    st.write(':palm_tree: Mehr Infos gibt es in unserer WhatsApp-Gruppe. :palm_tree:')

main()

# TODO
# Technik