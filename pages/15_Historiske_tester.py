import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
import requests
import folium
from folium import plugins
from streamlit_folium import st_folium
import leafmap.foliumap as leafmap
import geopandas
import pymongo
import pandas as pd
import numpy as np
import plotly.express as px
import utm

st.set_page_config(page_title="TRT", layout="wide", page_icon="src/data/img/AsplanViak_Favicon_32x32.png", initial_sidebar_state="collapsed")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none}</style>""", unsafe_allow_html=True) # ingen sidebar
    st.markdown("""<style>div[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True) # litt av sidebar
    st.markdown('''<style>button[title="View fullscreen"]{visibility: hidden;}</style>''', unsafe_allow_html=True) # hide fullscreen
    st.markdown("""<style>.block-container {padding-top: 1rem;padding-bottom: 0rem;padding-left: 5rem;padding-right: 5rem;}</style>""", unsafe_allow_html=True)
    
class Map:
    def __init__(self):
        self.lat = 63
        self.long = 10
        self.name = "Test"
    
    def _draw_polygon(self):
        plugins.Draw(
        export=False,
        position="topleft",
        draw_options={
            "polyline": False,
            "poly": False,
            "circle": False,
            "polygon": True,
            "marker": False,
            "circlemarker": False,
            "rectangle": False,
        },
        ).add_to(self.m)
 
    def create_wms_map(self, selected_display = True):
        if selected_display == True:
            selected_display = st.radio("Visningsalternativer", ["Oversiktskart", "Løsmasserelatert", "Berggrunnsrelatert"])
        selected_zoom = 13
        #--
        m = leafmap.Map(
            center=(self.lat, self.long), 
            zoom=selected_zoom,
            draw_control=False,
            measure_control=False,
            fullscreen_control=False,
            attribution_control=False,
            google_map="ROADMAP",
            shown=True
            )
        #--
        folium.Marker(
        [self.lat, self.long], 
        tooltip=f"{self.name}",
        icon=folium.Icon(icon="glyphicon-home", color="red"),
        ).add_to(m)
        #--
        wms_url_list = [
            "https://geo.ngu.no/mapserver/LosmasserWMS?request=GetCapabilities&service=WMS",
            "https://geo.ngu.no/mapserver/MarinGrenseWMS4?REQUEST=GetCapabilities&SERVICE=WMS",
            "https://geo.ngu.no/mapserver/GranadaWMS5?request=GetCapabilities&service=WMS",
            "https://geo.ngu.no/geoserver/nadag/ows?request=GetCapabilities&service=WMS",
            "https://geo.ngu.no/mapserver/BerggrunnWMS3?request=GetCapabilities&SERVICE=WMS",
            "https://geo.ngu.no/mapserver/BerggrunnWMS3?request=GetCapabilities&SERVICE=WMS",
            "https://geo.ngu.no/mapserver/BerggrunnWMS3?request=GetCapabilities&SERVICE=WMS",
            
        ]
        wms_layer_list = [
            "Losmasse_flate",
            "Marin_grense_linjer",
            "Energibronn",
            "GBU_metode",
            "Berggrunn_lokal_hovedbergarter",
            "Berggrunn_regional_hovedbergarter",
            "Berggrunn_nasjonal_hovedbergarter",
        ]
        wms_name_list = [
            "Løsmasser",
            "Marin grense",            
            "Energibrønner",
            "Grunnundersøkelser",
            "Lokal berggrunn",
            "Regional berggrunn",
            "Nasjonal berggrunn",
        ]
        for i in range(0, len(wms_url_list)):
            display = False
            if selected_display == "Løsmasserelatert" and i < 4:
                display = True 
            if selected_display == "Berggrunnsrelatert" and i == 4:
                display = True
            self._add_wms_layer(
                m,
                wms_url_list[i],
                wms_layer_list[i],
                wms_name_list[i],
                display
            )
        self.m = m
    
    def show_map(self):
        returned_objects = st_folium(self.m, use_container_width=True)
        return returned_objects
    
    def _add_wms_layer(self, map, url, layer, layer_name, display):
        map.add_wms_layer(
            url, 
            layers=layer, 
            name=layer_name, 
            attribution=" ", 
            transparent=True,
            format="image/png",
            shown=display
            )
    
    def _style_function(self, x):
        return {"color":"black", "weight":2}

    def _add_geojson_layer(self, filepath, layer_name):
        uc = "\u00B2"
        buildings_gdf = geopandas.read_file(filepath)
        buildings_df = buildings_gdf[['ID', 'BRA', 'Kategori', 'Standard']]
        #folium.GeoJson(data=buildings_gdf["geometry"]).add_to(m)

        feature = folium.features.GeoJson(buildings_gdf,
        name=layer_name,
        style_function=self._style_function,
        tooltip=folium.GeoJsonTooltip(fields= ["ID", "BRA"],aliases=["ID: ", f"BTA (m{uc}): "],labels=True))
        self.m.add_child(feature)

access_token = st.session_state.get('name')
if access_token == None:
    st.switch_page('Hjem.py')
st.write(access_token)
st.title("Tidligere tester")

# Åsmunds rot ##################################################################################################
# Pretend that you are someone else:
#access_token = 'Seabrokers'

############ Initialize database and lists to be filles: #########################################################################################################################
client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:jau0IMk5OKJWJ3Xl@cluster0.dlyj4y2.mongodb.net/")
db = client["TRT"]
collection = db["TRT"]

# If you are Asplan Viak; see all, if not; see only your own
if access_token == 'Asplan Viak':
    cursor = collection.find({})
else:
    cursor = collection.find({'Firma': access_token})

project_name_list = []
company_list = []
address_list = []
lat_list = []
long_list = []
contact_person_list = []
collector_length_list = []
collector_type_list = []
collector_fluid_list = []
well_diameter_list = []
casing_diameter_list = []
date_before_list = []
ground_water_level_before_list = []
depth_array_before_list = []
temp_array_before_list = []
date_after_list = []
ground_water_level_after_list = []
depth_array_after_list = []
temp_array_after_list = []
power_before_list = []
power_after_list = []
comment_list = []
project_id_list = []
conductivity_list = []
resistance_list = []
rock_type_list = []

############ Find relevant in database: ########################################################################################################################
for document in cursor:        
    project_name_list.append(document['Prosjektnavn'])
    company_list.append(document['Firma'])
    address_list.append(document['Adresse'])
    lat_list.append(document['Latitude'])
    long_list.append(document['Longitude'])
    contact_person_list.append(document['Kontaktperson'])
    collector_length_list.append(document['Kollektorlengde'])
    collector_type_list.append(document['Kollektortype'])
    collector_fluid_list.append(document['Kollektorvæske'])
    well_diameter_list.append(document['Brønndiameter'])
    casing_diameter_list.append(document['Foringsrørdiameter'])
    date_before_list.append(document['Måledato temperaturprofil før test'])
    ground_water_level_before_list.append(document['Grunnvannsnivå før test'])
    depth_array_before_list.append(document['Posisjoner temperaturmålinger før test'])
    temp_array_before_list.append(document['Temperaturmålinger før test'])
    date_after_list.append(document['Måledato temperaturprofil etter test'])
    ground_water_level_after_list.append(document['Grunnvannsnivå etter test'])
    depth_array_after_list.append(document['Posisjoner temperaturmålinger etter test'])
    temp_array_after_list.append(document['Temperaturmålinger etter test'])
    power_before_list.append(document['Strømmåler før'])
    power_after_list.append(document['Strømmåler etter'])
    comment_list.append(document['Kommentar'])
    project_id_list.append(document['Oppdragsnummer'])
    conductivity_list.append(document['Effektiv ledningsevne'])
    resistance_list.append(document['Termisk borehullsmotstand'])
    rock_type_list.append(document['Berggrunnstype'])

############ Find relevant in Excel-file: ########################################################################################################################
excel_df = pd.read_excel('Test_excel_med_TRTer.xlsx')

if access_token == 'Asplan Viak':
    relevant_excel_df = excel_df
else:
    # Find relevant rows:
    relevant_excel_df = pd.DataFrame(columns=list(excel_df.columns))
    for j in range(0,len(excel_df)):
        if str(access_token) in str(excel_df['Oppdragsgiver\n'].iloc[j]):
            found_row = pd.DataFrame(excel_df.loc[j]).transpose()
            relevant_excel_df = pd.concat([relevant_excel_df, found_row], axis=0)
    relevant_excel_df = relevant_excel_df.reset_index(drop=True)

# Append to lists:
for i in range(0,len(relevant_excel_df)):
    project_name_list.append(relevant_excel_df['Navn\n'].iloc[i])
    company_list.append(relevant_excel_df['Oppdragsgiver\n'].iloc[i])
    address_list.append(None)               
    
    try:
        latlon_coord = utm.to_latlon(relevant_excel_df['ØV (UTM 32)\n'].iloc[i], relevant_excel_df['NS (UTM 32)\n'].iloc[i], 32, 'V')
        lat_list.append(latlon_coord[0])
        long_list.append(latlon_coord[1])
    except:
        lat_list.append(None)
        long_list.append(None)
    
    contact_person_list.append(None)
    collector_length_list.append(relevant_excel_df['Lengde kollektor, minus bunnlodd på 1 m [m]'].iloc[i])
    collector_type_list.append(relevant_excel_df['Type kollektor og diameter [mm]\n'].iloc[i])
    collector_fluid_list.append(relevant_excel_df['Kollektorvæske\n'].iloc[i])
    well_diameter_list.append(relevant_excel_df['Diameter borehull [mm]\n'].iloc[i])
    casing_diameter_list.append(relevant_excel_df['Diameter foringsrør [mm]'].iloc[i])
    
    date_before_list.append(None)
    ground_water_level_before_list.append(relevant_excel_df['Grunnvannsnivå\n[m/ under terreng]\n'].iloc[i])
    depth_array_before_list.append(None)
    temp_array_before_list.append(None)
    
    date_after_list.append(None)
    ground_water_level_after_list.append(relevant_excel_df['Grunnvannsnivå\n[m/ under terreng]\n'].iloc[i])
    depth_array_after_list.append(None)
    temp_array_after_list.append(None)
    power_before_list.append(None)
    power_after_list.append(None)
    
    comment_list.append(relevant_excel_df['Kommentar spesielle forhold'].iloc[i])

    project_id_list.append(relevant_excel_df['Oppdragsnummer\n'].iloc[i])
    conductivity_list.append(relevant_excel_df['Effektiv  varmledningsevne [W*/m*K]'].iloc[i])
    resistance_list.append(relevant_excel_df['Termisk borehullsmotstand [m*K/W]'].iloc[i])
    rock_type_list.append(relevant_excel_df['Berggrunn\n'].iloc[i])

############ Construct dataframe: ########################################################################################################################
dict_for_df = {'Prosjektnavn': project_name_list,
               'Firma': company_list,
               'Adresse': address_list, 
               'Breddegrad': lat_list, 
               'Lengdegrad': long_list,
               'Kontaktperson': contact_person_list,
               'Kollektorlengde (m)': collector_length_list,
               'Kollektortype': collector_type_list,
               'Kollektorvæske': collector_fluid_list,
               'Brønndiameter (mm)': well_diameter_list,
               'Foringsrørdiameter (mm)': casing_diameter_list,
               'Måledato før test': date_before_list,
               'Grunnvannsnivå før test (m)': ground_water_level_before_list,
               'Temperaturnoder før test (m)': depth_array_before_list,
               'Temperaturmålinger før test (°C)': temp_array_before_list,
               'Måledato etter test': date_after_list,
               'Grunnvannsnivå etter test (m)': ground_water_level_after_list,
               'Temperaturnoder etter test (m)': depth_array_after_list,
               'Temperaturmålinger etter test (°C)': temp_array_after_list,
               'Strømmåler før test (kWh)': power_before_list,
               'Strømmåler etter test (kWh)': power_after_list,
               'Kommentar': comment_list,
               'Oppdragsnummer': project_id_list,
               'Effektiv varmeledningsevne (W/mK)': conductivity_list,
               'Termisk borehullsmotstand (mK/W)': resistance_list,
               'Berggrunn': rock_type_list
               }

df = pd.DataFrame(dict_for_df)

############ Filter and display dataframe: ########################################################################################################################

if access_token == 'Asplan Viak':
    c1,c2 = st.columns(2)
    
    with c1:
        filter_column = st.selectbox('Velg kolonne det skal filtreres etter', options=list(df.columns), index=None)
    
    with c2:
        if filter_column is not None:
            string_columns = ['Prosjektnavn', 'Firma', 'Adresse', 'Kontaktperson', 'Kollektortype', 'Kollektorvæske','Kommentar', 'Oppdragsnummer', 'Berggrunn']
            number_columns = ['Breddegrad', 'Lengdegrad', 'Kollektorlengde (m)', 'Brønndiameter (mm)', 'Foringsrørdiameter (mm)', 'Grunnvansnivå før test (m)', 'Grunnvansnivå etter test (m)', 'Strømmåler før test (kWh)', 'Strømmåler etter test (kWh)', 'Effektiv varmeledningsevne (W/mK)', 'Termisk borehullsmotstand (mK/W)']
            special_columns = ['Måledato før test', 'Temperaturnoder før test (m)', 'Temperaturmålinger før test (°C)', 'Måledato etter test', 'Temperaturnoder etter test (m)', 'Temperaturmålinger etter test (°C)']

            if filter_column in string_columns:
                filter_str = st.text_input('Nøkkelord:', value=None)
                if filter_str is not None:
                    # Find relevant rows:
                    df_filtered = pd.DataFrame(columns=list(df.columns))
                    for j in range(0,len(df)):
                        if str(filter_str).lower() in str(df[filter_column].iloc[j]).lower():
                            found_row = pd.DataFrame(df.loc[j]).transpose()
                            df_filtered = pd.concat([df_filtered, found_row], axis=0)                    
                    df = df_filtered.reset_index(drop=True)

            elif filter_column in number_columns:
                d1,d2 = st.columns(2)
                with d1:
                    min_filter = st.number_input('Minste verdi', value = None)
                with d2:
                    max_filter = st.number_input('Største verdi', value = None)
                
                if min_filter is not None and max_filter is not None:
                    df_filtered = pd.DataFrame(columns=list(df.columns))
                    for j in range(0,len(df)):
                        try:
                            if df[filter_column].iloc[j] >= min_filter and df[filter_column].iloc[j] <= max_filter:
                                found_row = pd.DataFrame(df.loc[j]).transpose()
                                df_filtered = pd.concat([df_filtered, found_row], axis=0)
                        except:
                            # If it is something wrong with the input; pass
                            pass                  
                    df = df_filtered.reset_index(drop=True)
            
            else:
                st.write('Filtrering på denne kolonnen ikke mulig enda')

    st.markdown('---')

st.dataframe(df,use_container_width=True)
st.markdown('---')

############ Show map: ########################################################################################################################
map = folium.Map(location=[65, 18], zoom_start=5, tiles='openstreetmap',zoom_control=False)

for i in range(0,len(df)):
    if df['Breddegrad'].iloc[i] is not None and df['Breddegrad'].iloc[i] == df['Breddegrad'].iloc[i]:
        folium.Marker([df['Breddegrad'].iloc[i], df['Lengdegrad'].iloc[i]], popup=df['Prosjektnavn'].iloc[i], tooltip=df['Prosjektnavn'].iloc[i]).add_to(map)

chosen_project = st_folium(map,use_container_width=True, returned_objects=['last_object_clicked_tooltip'])
chosen_project = chosen_project['last_object_clicked_tooltip']

############ Show data for chosen project: ########################################################################################################################
if chosen_project != None:
    chosen_index = df.index[df['Prosjektnavn'] == chosen_project].tolist()
    chosen_index = chosen_index[0]

    st.header('Valgt prosjekt:')
    st.markdown('---')

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric('Prosjektnavn:', df['Prosjektnavn'].iloc[chosen_index])
    with c2:
        st.metric('Brønnborer:', df['Firma'].iloc[chosen_index])
    with c3:
        st.metric('Kontaktperson:', df['Kontaktperson'].iloc[chosen_index])
    with c4:
        st.metric('Oppdragsnummer', df['Oppdragsnummer'].iloc[chosen_index])

    st.markdown('---')
    
    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric('Adresse:', df['Adresse'].iloc[chosen_index])
    with c2:
        st.metric('Breddegrad:', df['Breddegrad'].iloc[chosen_index])
    with c3:
        st.metric('Lengdegrad:', df['Lengdegrad'].iloc[chosen_index])

    st.markdown('---')
    
    c1,c2,c3 = st.columns(3)
    with c1:
        if df['Kollektorlengde (m)'].iloc[chosen_index] is not None and df['Kollektorlengde (m)'].iloc[chosen_index] == df['Kollektorlengde (m)'].iloc[chosen_index]:
            st.metric('Kollektorlengde:', f"{df['Kollektorlengde (m)'].iloc[chosen_index]} m")
        else:
            st.metric('Kollektorlengde:',' - ')
    with c2:
        st.metric('Kollektortype:', df['Kollektortype'].iloc[chosen_index])
    with c3:
        st.metric('Kollektorvæske:', df['Kollektorvæske'].iloc[chosen_index])
    
    st.markdown('---')

    c4,c5,c6 =st.columns(3)
    with c4:
        if df['Brønndiameter (mm)'].iloc[chosen_index] is not None and df['Brønndiameter (mm)'].iloc[chosen_index] == df['Brønndiameter (mm)'].iloc[chosen_index]:
            st.metric('Brønndiameter:', f"{df['Brønndiameter (mm)'].iloc[chosen_index]} mm")
        else:
            st.metric('Brønndiameter:', f' - ')
    with c5:
        if df['Foringsrørdiameter (mm)'].iloc[chosen_index] is not None and df['Foringsrørdiameter (mm)'].iloc[chosen_index] == df['Foringsrørdiameter (mm)'].iloc[chosen_index]:
            st.metric('Foringsrørdiameter:', f"{df['Foringsrørdiameter (mm)'].iloc[chosen_index]} mm")
        else:
            st.metric('Foringsrørdiameter:', ' - ')
    with c6:
        st.metric('Berggrunn:', df['Berggrunn'].iloc[chosen_index])

    st.markdown('---')
    
    c1,c2,c3,c4,c5,c6 = st.columns([0.05, 1, 0.05, 0.05, 1, 0.05])
    
    def database_to_array(list_from_database):
        elements = list_from_database.replace('None', 'np.nan').strip('[]').split()
        proper_array = np.array([float(elem) if elem != '0.' and not np.isnan(float(elem)) else None for elem in elements])
        return proper_array
    
    
    with c2:
        if df['Temperaturnoder før test (m)'].iloc[chosen_index] is not None and df['Temperaturnoder før test (m)'].iloc[chosen_index] == df['Temperaturnoder før test (m)'].iloc[chosen_index] and df['Temperaturnoder før test (m)'].iloc[chosen_index] != '[nan]':
            st.subheader('Temperaturprofil før test')
            
            depth_array_before = database_to_array(df['Temperaturnoder før test (m)'].iloc[chosen_index])
            temp_array_before = database_to_array(df['Temperaturmålinger før test (°C)'].iloc[chosen_index])

            min_x = np.nanmin([x for x in temp_array_before if isinstance(x, (int, float))])-0.5
            max_x = np.nanmax([x for x in temp_array_before if isinstance(x, (int, float))])+0.5
            fig = px.line(y=depth_array_before, x=temp_array_before, color_discrete_sequence=['#367A2F', '#FFC358'])
            fig.update_xaxes(title_text='Temperatur [°C]', side='top')
            fig.update_yaxes(title_text='Dybde [m]', autorange='reversed')
            fig.update_xaxes(range=[min_x, max_x])
            #if df['Grunnvannsnivå før test (m)'].iloc[chosen_index] > 0:
            fig.add_shape(type='line', x0=min_x, y0=df['Grunnvannsnivå før test (m)'].iloc[chosen_index], x1=max_x, y1=df['Grunnvannsnivå før test (m)'].iloc[chosen_index], line=dict(color='#007FFF', width=2))
            fig.add_annotation(x=min_x+0.08*(max_x-min_x), y=df['Grunnvannsnivå før test (m)'].iloc[chosen_index]+0.05*depth_array_before[-1], text="Grunnvannsnivå", showarrow=False, font=dict(color="#007FFF", size=14))
            st.plotly_chart(fig, config={'staticPlot': True}, use_container_width=True)

        if df['Strømmåler før test (kWh)'].iloc[chosen_index] is not None and df['Strømmåler før test (kWh)'].iloc[chosen_index] == df['Strømmåler før test (kWh)'].iloc[chosen_index]:
            st.metric('Strømmåler før test:', f"{df['Strømmåler før test (kWh)'].iloc[chosen_index]} kWh")
        else:
            st.metric('Strømmåler før test:', " - ")

    with c5:
        if df['Temperaturnoder etter test (m)'].iloc[chosen_index] is not None and df['Temperaturnoder etter test (m)'].iloc[chosen_index] == df['Temperaturnoder etter test (m)'].iloc[chosen_index] and df['Temperaturnoder etter test (m)'].iloc[chosen_index] != '[nan]':
            st.subheader('Temperaturprofil etter test')

            depth_array_after = database_to_array(df['Temperaturnoder etter test (m)'].iloc[chosen_index])
            temp_array_after = database_to_array(df['Temperaturmålinger etter test (°C)'].iloc[chosen_index])

            min_x = np.nanmin([x for x in temp_array_after if isinstance(x, (int, float))])-0.5
            max_x = np.nanmax([x for x in temp_array_after if isinstance(x, (int, float))])+0.5

            fig = px.line(y=depth_array_after, x=temp_array_after, color_discrete_sequence=['#367A2F', '#FFC358'])
            fig.update_xaxes(title_text='Temperatur [°C]', side='top')
            fig.update_yaxes(title_text='Dybde [m]', autorange='reversed')
            fig.update_xaxes(range=[min_x, max_x])
            #if df['Grunnvannsnivå etter test (m)'].iloc[chosen_index] > 0:
            fig.add_shape(type='line', x0=min_x, y0=df['Grunnvannsnivå etter test (m)'].iloc[chosen_index], x1=max_x, y1=df['Grunnvannsnivå etter test (m)'].iloc[chosen_index], line=dict(color='#007FFF', width=2))
            fig.add_annotation(x=min_x+0.08*(max_x-min_x), y=df['Grunnvannsnivå etter test (m)'].iloc[chosen_index]+0.05*depth_array_before[-1], text="Grunnvannsnivå", showarrow=False, font=dict(color="#007FFF", size=14))
            st.plotly_chart(fig, config={'staticPlot': True}, use_container_width=True)

        if df['Strømmåler etter test (kWh)'].iloc[chosen_index] is not None and df['Strømmåler etter test (kWh)'].iloc[chosen_index] == df['Strømmåler etter test (kWh)'].iloc[chosen_index]:
            st.metric('Strømmåler etter test:', f"{df['Strømmåler etter test (kWh)'].iloc[chosen_index]} kWh")
        else:
            st.metric('Strømmåler etter test:', " - ")


    st.markdown('---')

    c1, c2 = st.columns(2)
    with c1:
        if df['Effektiv varmeledningsevne (W/mK)'].iloc[chosen_index] is not None and df['Effektiv varmeledningsevne (W/mK)'].iloc[chosen_index] == df['Effektiv varmeledningsevne (W/mK)'].iloc[chosen_index]:
            st.metric('Effektiv varmeledningsevne:', f"{df['Effektiv varmeledningsevne (W/mK)'].iloc[chosen_index]} W/mK")
        else:
            st.metric('Effektiv varmeledningsevne:', " - ")
    with c2:
        if df['Termisk borehullsmotstand (mK/W)'].iloc[chosen_index] is not None and df['Termisk borehullsmotstand (mK/W)'].iloc[chosen_index] == df['Termisk borehullsmotstand (mK/W)'].iloc[chosen_index]:
            st.metric('Termisk borehullsmotstand', f"{df['Termisk borehullsmotstand (mK/W)'].iloc[chosen_index]} mK/W")
        else:
            st.metric('Termisk borehullsmotstand', " - ")

##################################################################################################

#map_obj = Map()
#map_obj.lat = 60
#map_obj.long = 11
#map_obj.name = "Test"
#map_obj.create_wms_map()
#returned_objects = map_obj.show_map()

#st.write(returned_objects)

#st.markdown("---")
#add_vertical_space(5)
if st.button("Gå tilbake til forside"):
    switch_page("Hjem")


