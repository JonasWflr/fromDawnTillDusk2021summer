import streamlit as st
import altair as alt
import datetime
import pandas as pd
import numpy as np
from io import StringIO
import requests

###########################################################################
# CONFIGS
###########################################################################
# https://docs.google.com/spreadsheets/d/{key}/gviz/tq?tqx=out:csv&sheet={sheet_name}
# get key from url (remove everything behind last '/' (e.g. edit?resourcekey#gid=xxxxxxxx))
# append gviz/tq?tqx=out:csv'

#old:
#GOOGLE_SPREADSHEET_RESULTS = 'https://docs.google.com/spreadsheets/d/1mV3lzutv90A3xjoTANt1-qg7XxZ-8-7LkgdfldQr8CA/gviz/tq?tqx=out:csv'
GOOGLE_SPREADSHEET_RESULTS = 'https://docs.google.com/spreadsheets/d/180e9kmsMor-VCAjljGXQ8voBFR3bEUci7ceaxCU0DTA/gviz/tq?tqx=out:csv&sheet=Formularantworten%201'
GOOGLE_SPREADSHEET_CONTENT = 'https://docs.google.com/spreadsheets/d/180e9kmsMor-VCAjljGXQ8voBFR3bEUci7ceaxCU0DTA/gviz/tq?tqx=out:csv&sheet=InputWebseite'

DEBUG = False # set to False for prod (False disables horizontal scrolling)

TTL_TEXT = 60*60*3 # ttl for text cache (all text elements)
TTL_RESULTS = 60*10*1 # ttl for results cache

# STREAMLIT ADJUSTMENTS
st.set_page_config(
    layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
    page_title='Dawn Till Dusk',  # String or None. Strings get appended with "• Streamlit".
    page_icon=':hibiscus:'  # String, anything supported by st.image, or None.
)
# hide hamburger menu (top right) and footer
if not DEBUG:
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# hide fullscreen button
# remove horizontal scrolling
if not DEBUG:
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


def get_color_legend(gender):
# return color stuff for one gender
# gender in ['Herr','Frau','Junior']
    color_dict = {'Herr': '#f2b713',
              'Frau': '#f2dc13',
              'Junior': '#f26113'}
    color_legend = alt.Color('Geschlecht',
            title="",
            scale=alt.Scale(
                domain=[gender],
                range=[color_dict[gender]] # orange / yellow / redish
            )
        )
    return(color_legend)
tooltip_all = [alt.Tooltip('Name',title=None),
        alt.Tooltip('km',format=',.0f'),
        alt.Tooltip('Höhenmeter',format='.0f'),
        alt.Tooltip('Technik',title='Wie')
    ]

###########################################################################
# FUNCTIONS
###########################################################################
# READ Dummy DATA
#df_data_dummy = pd.read_excel("./test_data.xlsx",engine="openpyxl")#, skiprows=2,nrows=20)
def fill_with_dummy_data(df):
    # fill with dummy data to show plots
    df['km'] = np.random.randint(80, 200, df.shape[0])
    df['Höhenmeter'] = np.random.randint(500, 2000, df.shape[0])
    return(df)

# READ RESULTS FROM GOOGLE
st.cache(ttl=TTL_RESULTS)
def read_data():
    response = requests.get(GOOGLE_SPREADSHEET_RESULTS)
    #response = requests.get('https://docs.google.com/spreadsheets/d/180e9kmsMor-VCAjljGXQ8voBFR3bEUci7ceaxCU0DTA/gviz/tq?tqx=out:csv')
    assert response.status_code == 200, 'Wrong status code'
    response_string = response.content.decode('utf-8')
    TEST = StringIO(response_string)
    df_data_google = pd.read_csv(TEST, sep=',')
    # RENAME FOR EASIER PROCESSING (SAME NAME AS IN WINTER)
    df_data_google = df_data_google.rename(columns={'Fortbewegungsart': 'Technik'})
    # MOVE junior FROM 'Alterskategorie' INTO 'Geschlecht'
    if df_data_google[df_data_google['Alterskategorie']=='Junior*innen'].shape[0]>0:
        df_data_google.loc[df_data_google['Alterskategorie']=='Junior*innen','Geschlecht'] = 'Junior'
    return(df_data_google)

# READ TEXT CONTENT FROM GOOGLE
st.cache(ttl=TTL_TEXT)
def read_text_data():
    response = requests.get(GOOGLE_SPREADSHEET_CONTENT)
    assert response.status_code == 200, 'Wrong status code'
    response_string = response.content.decode('utf-8')
    TEST = StringIO(response_string)
    df_data_google = pd.read_csv(TEST, sep=',')

    # reset id to column 'id'
    df_data_google = df_data_google.set_index('id')
    return(df_data_google)

st.cache(ttl=TTL_TEXT)
def get_text_field(id):
    # returns field from google spreadsheet, used in text
    # use string from column 'id' as id
    df_content_google = read_text_data()
    return(df_content_google.loc[id, 'content'])

# SHOW THE TEXT, WHAT IT IS ETC.
def show_infos(date_race, remaining_days):
    st.title(':bellhop_bell: __Format/Details__')
    st.write(f'''
    __Datum:__ {date_race.strftime('%d.%m.%Y')}\n
    __Start:__ {get_text_field('time_start')}\n
    __Zielschluss:__ {get_text_field('time_end')}\n
    __Fortbewegungsart:__ {get_text_field('format_style')}\n
    __Sieger*in__: {get_text_field('format_siegerin')}\n
    __Kategorien:__ {get_text_field('format_kategorien')}\n
    __Messung:__ {get_text_field('format_messung')}\n
    __Reporting:__ {get_text_field('format_reporting_fields')} per Text/Whatsapp/etc an {get_text_field('format_reporting_contact')} bis um {get_text_field('format_reporting_time')} am Tag des Rennens ({get_text_field('date')}) senden. 
    {get_text_field('format_reporting_addon')}
    
    Bei Anregung oder Fragen, meldet euch einfach im Chat. 

    Wir freuen uns auf einen grossartigen Tag!

    ''')

# SHOW COMPLETE RESULTS WITH PLOTS
def show_plots_seniors(df_selected, gender):
    ###########################
    # DISTANCE
    st.header(f':straight_ruler: __Distanz {gender}en__')
    df_selected = df_selected[(df_selected['Geschlecht']==gender)&(df_selected['Alterskategorie']=='Senior*innen')]
    # df_distance = df_selected#[['km','Höhenmeter','Technik']]
    # df_distance['Rang'] = df_distance[['km']].rank(ascending=False,method='min')
    # df_distance['Rang'] = df_distance['Rang'].astype(int)
    # df_distance = df_distance.sort_values(by=['km'],ascending=False)
    # df_distance.loc[df_distance['Rang'] == 1,'Rang'] = ':trophy:'
    # df_distance.loc[df_distance['Rang'] == 2, 'Rang'] = ':second_place_medal:'
    # df_distance.loc[df_distance['Rang'] == 3, 'Rang'] = ':third_place_medal:'
    # for index, row in df_distance.iterrows():
    #     st.write(f"{row['Rang']:<20} {row['id']: <30}")

    chart_distance = alt.Chart(
        df_selected  # .sort_values(by='km',ascending=False)
    ).mark_bar().encode(
        x='km:Q',
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

def show_plots_seniors2(df_input, gender, emoji_dict):
    ###########################
    st.header(f'__{gender}en__')

    df_input = df_input[
        (df_input['Geschlecht'] == gender) & (df_input['Alterskategorie'] == 'Senior*innen')]

    for style in list(df_input['Technik'].unique()):
        try:
            emoji = emoji_dict[style]
        except:
            emoji = ":tada:"
        st.header(f'{gender}en - {style} {emoji}')
        # create selection for this iteration
        df_selected = df_input[
            df_input['Technik'] == style]
        chart_combi = alt.Chart(
            df_selected
        ).mark_point(filled=True, size=300).encode(
            y='Höhenmeter:Q',
            x=alt.X('km'),
            color=get_color_legend(gender),
            tooltip=tooltip_all,
        )
        st.altair_chart(chart_combi, use_container_width=True)

def show_plot_juniors2(df_input,emoji_dict):
    st.header(f'__ Junior*innen__')

    df_input = df_input[df_input['Alterskategorie'] == 'Junior*innen']

    for style in list(df_input['Technik'].unique()):
        try:
            emoji = emoji_dict[style]
        except:
            emoji = ":tada:"
        st.header(f'Junior*innen - {style} {emoji}')
        # create selection for this iteration
        df_selected = df_input[
            df_input['Technik'] == style]
        chart_combi = alt.Chart(
            df_selected
        ).mark_point(filled=True, size=300).encode(
            y='Höhenmeter:Q',
            x=alt.X('km'),
            color=get_color_legend('Junior'),
            tooltip=tooltip_all,
        )
        st.altair_chart(chart_combi, use_container_width=True)
def show_plot_juniors(df_selected):
    ###########################
    # DISTANCE
    st.header(f':straight_ruler: __Distanz Junior*innen__')
    df_selected = df_selected[(df_selected['Alterskategorie']=='Junior*innen')]
    chart_distance = alt.Chart(
        df_selected  # .sort_values(by='km',ascending=False)
    ).mark_bar().encode(
        x='km:Q',
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
        st.header('__Übersicht__ :hibiscus: :palm_tree:')
        selection_geschlecht = alt.selection_single(fields=['Geschlecht'], bind='legend')
        selection_technik = alt.selection_single(fields=['Technik'], bind='legend')

        chart_combi = alt.Chart(
            df_selected
        ).mark_point(filled=True, size=300).encode(
            y='Höhenmeter:Q',
            x=alt.X('km'),
            color=color_all_legend,
            shape='Technik',
            tooltip=tooltip_all,
            opacity=alt.condition(selection_technik | selection_geschlecht, alt.value(1), alt.value(0.2))
        ).add_selection(selection_geschlecht, selection_technik)
        st.altair_chart(chart_combi, use_container_width=True)

def define_remaining_days_and_df():
    #################
    # DATE STUFF
    today = datetime.date.today()
    # for testing:
    #today = datetime.date(2021,6,19)

    # RACE DATE
    # GET IT FORM SPREADSHEET
    date_race_string = get_text_field('date')
    date_race = datetime.datetime.strptime(date_race_string, '%d.%m.%Y').date()

    # for testing:
    #date_race = datetime.date(2021, 3, 6)
    remaining_days = (date_race - today).days
    df_data_google = read_data()
    df_selected = df_data_google
    # fill with dummy data for testing
    #df_selected = fill_with_dummy_data(df_data_google)

    # fill missing?
  #  df_selected['Technik'] = df_selected['Technik'].fillna(value='Klassisch/Skating')
  #  df_selected.loc[df_selected['Technik']=='-','Technik'] = 'Klassisch/Skating'
    # define id and set as index
    df_selected['id'] = df_selected['Vorname']+' '+df_selected['Name']
    df_selected = df_selected.set_index('id',drop=False)
    return(date_race, remaining_days, df_selected)

def count_by_gender(df_selected,gender):
    return(df_selected[df_selected['Geschlecht'] == gender]['Geschlecht'].count())

def show_prerace_stuff_vert(df_selected, remaining_days):
    if(remaining_days)>0:
        st.title(':sleeping_accommodation: __Nur noch {} Mal schlafen!__'.format(remaining_days))
        st.write(f"Noch nicht angemeldet? [Melde dich jetzt an!]({get_text_field('prerace_form_link')})")
        n_participants = df_selected['id'].count()
        st.subheader('Angemeldet sind momentan {} Athlet\*innen'.format(n_participants))

       #col1, col2 = st.beta_columns(2)
        #df_selected = df_selected.rename(columns={'Fortbewegungsart':'Technik'})
        df_selected['Anzahl Technik'] = df_selected.groupby('Technik')['Technik'].transform('count')
        max_value = df_selected['Anzahl Technik'].max() + 1.5

        chart_technik = alt.Chart(
            df_selected[['Technik','Anzahl Technik','Name']],
            height=300
        ).mark_bar().encode(
            y=alt.Y('Anzahl Technik:Q', axis=None, scale=alt.Scale(domain=(0,max_value))),
            x=alt.X('Technik', sort='-y', title=None, axis=None)
        )

        chart_technik_text = chart_technik.mark_text(
            align='center',
            baseline='middle',
            dy=-24,
            color='black'
        ).encode(
            y=alt.Y('Anzahl Technik:Q'),
            x=alt.X('Technik', sort='-y', title=None, axis=None),
            text='Anzahl Technik:Q'
        )

        chart_technik_text2 = chart_technik.mark_text(
            align='center',
            baseline='middle',
            dy=-10,
            color='black'
        ).encode(
            y=alt.Y('Anzahl Technik:Q'),
            # y=alt.Value(0),
            x=alt.X('Technik', sort='-y', title=None, axis=None),
            text='Technik:N'
        )

        chart_combined = chart_technik+chart_technik_text+chart_technik_text2
        chart_combined.configure_view(strokeWidth=0)
        st.altair_chart(chart_combined, use_container_width=True)

        # GESCHLECHT

        df_selected['Anzahl Geschlecht'] = df_selected.groupby('Geschlecht')['Geschlecht'].transform('count')
        max_value = df_selected['Anzahl Geschlecht'].max() + 1.5

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
    date_race, remaining_days, df_selected = define_remaining_days_and_df()

    # SOME INTRO TEXT BEFORE TITLE
    st.write(f"{get_text_field('pretitle_text')}")
    # SHOW GENERAL RULES AND INFOS
    show_infos(date_race, remaining_days)

    # SHOW PRERACE INFOS
    show_prerace_stuff_vert(df_selected, remaining_days)

    # SHOW THE RESULTS AND PLOTS
    st.title(':trophy: __Resultate__')
    st.write(get_text_field('results_text'))
    emoji_dict = {"Rollski": ":muscle:",
                  "Velo": ":bike:",
                  "Rennen": ":athletic_shoe:"
                  }
    show_plots_seniors2(df_selected,'Frau',emoji_dict)
    show_plots_seniors2(df_selected,'Herr',emoji_dict)
    # JUNIORS
    show_plot_juniors2(df_selected,emoji_dict)

    # SHOW POSTRACE STUFF
    show_combined_plot(df_selected, remaining_days)
    # FOOTER
    #st.write(':palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree: :hibiscus: :palm_tree:')
    st.write('----------------------------------------------')
    st.write(f"{get_text_field('footer')}")

main()

# TODO
# Technik