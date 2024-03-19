import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import pymongo
import requests
import re
import folium
from streamlit_folium import st_folium
from datetime import date
from datetime import datetime
import utm
import json
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
from src.scripts import streamlit_settings, switch_pages, toggle_closed_expander, login
import time

####################################################
#################### Funksjoner ####################
####################################################

def well_placement_input(text_string):
    address = address_loaded
    lat = lat_loaded
    long = long_loaded
    lat_lon_check = False
    if text_string == "Skriv inn adresse og plasser på kart":
        c1,c2 = st.columns([2,1])
        with c1:
            address = st.text_input("Søk etter adresse", value=address_loaded)
        with c2:
            place = st.text_input("By/sted (hvis nødvendig)")
        if len(address)>2:
            [lat_search,long_search] = adresse_til_koordinat(address,place)
            if lat_search != lat_search or long_search != long_search:
                st.info('Adresse ikke funnet, prøv en annen skrivemåte, eller velg å skrive inn koordinater.')
            else:
                #map_with_point(lat,long)
                st.write('Klikk på kartet for å velge plassering av brønnen:')
                m = folium.Map(location=[lat_search, long_search], zoom_start=16)
                if lat_loaded != None:
                    folium.Marker([lat_loaded, long_loaded]).add_to(m)
                m.add_child(folium.LatLngPopup())
                coord_json = st_folium(m, height=400, use_container_width=True, returned_objects=['last_clicked'])
                if coord_json['last_clicked']:
                    lat = coord_json['last_clicked']['lat']
                    long = coord_json['last_clicked']['lng']
                else:
                    lat = lat_loaded
                    long = long_loaded
                    c1,c2 = st.columns(2)
                if lat != 0 and long != 0:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric('Valgt breddegrad:', f"{round(lat, 4):,}".replace(".", ","))
                    with c2:
                        st.metric('Valgt lengdegrad:', f"{round(long, 4):,}".replace(".", ","))
                    lat_lon_check = True
    elif text_string == "Skriv inn koordinater":
        coord_system_options = ['EU89 - Geografisk, grader (Lat/Lon)', 'EU89, UTM-sone 31', 'EU89, UTM-sone 32', 'EU89, UTM-sone 33']
        c1,c2,c3 = st.columns([0.05,1,0.05])
        with c2:
            projection = st.selectbox('Velg koordinatsystem', options=coord_system_options, index=st.session_state.coord_system_index)
        if projection != coord_system_options[st.session_state.coord_system_index]:
            st.session_state.changed_coords = 0
            st.session_state.coord_system_index = coord_system_options.index(projection)
        if projection == 'EU89 - Geografisk, grader (Lat/Lon)':
            if lat_loaded != None:
                ns_value = long_loaded
                ov_value = lat_loaded
            else: 
                ns_value = 0.0
                ov_value = 0.0
            zone = 0
            number_format = "%.6f"
            step_length = 0.000001
        else:
            number_format = "%.1f"
            step_length = 0.1
            if projection == 'EU89, UTM-sone 31':
                zone = 31
                #if lat_loaded != None:
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(lat_loaded, long_loaded, 31, 'V')
                    st.session_state.lat_31 = utm_tuple[0]
                    st.session_state.long_31 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_31
                ov_value = st.session_state.lat_31
            elif projection == 'EU89, UTM-sone 32':
                zone = 32
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(lat_loaded, long_loaded, 32, 'V')
                    st.session_state.lat_32 = utm_tuple[0]
                    st.session_state.long_32 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_32
                ov_value = st.session_state.lat_32
            elif projection == 'EU89, UTM-sone 33':
                zone = 33
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(lat_loaded, long_loaded, 33, 'V')
                    st.session_state.lat_33 = utm_tuple[0]
                    st.session_state.long_33 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_33
                ov_value = st.session_state.lat_33
        c1, c2, c3, c4 = st.columns([0.05,0.5,0.5,0.05])
        with c2:
            lat = st.number_input("Breddegrad/Latitude (Nord-koordinat/ØV)", value = ov_value, step=step_length, format=number_format)
        with c3:
            long = st.number_input("Lengdegrad/Longitude (Øst-koordinat/NS)", value = ns_value, step=step_length, format=number_format)
        if zone > 0:
            utm_tuple = utm.to_latlon(lat, long, zone, 'V')
            lat = utm_tuple[0]
            long = utm_tuple[1]
            #lat_lon_check = True
        if lat != 0 or long != 0:
            lat_lon_check = True
            map_with_point(lat, long)
    return address, lat, long, lat_lon_check
    
def adresse_til_koordinat(adresse,sted):
    API_KEY = "400f888f4da9461387721ccbd1a0e0db"
    address = f'{adresse}, {sted}'
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&limit=1&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            result = data["features"][0]
            latitude = result["geometry"]["coordinates"][1]
            longitude = result["geometry"]["coordinates"][0]
        except:
            try:
                if 'gate' in address:
                    address = address.replace('gate',' gate')
                elif 'vei' in address:
                    address = address.replace('vei',' vei')
                else:
                    pattern = r"_(\d+)_[a-zA-Z]+?$"
                    match = re.search(pattern, address)
                    if match:
                        substring = match.group(0)
                        address = address.replace(substring, "")
                url = f"https://api.geoapify.com/v1/geocode/search?text={address}&limit=1&apiKey={API_KEY}"
                response = requests.get(url)
                data = response.json()
                result = data["features"][0]
                latitude = result["geometry"]["coordinates"][1]
                longitude = result["geometry"]["coordinates"][0]
            except:
                latitude = float('nan')
                longitude = float('nan')
    return latitude, longitude

def map_with_point(lat,long):
    m = folium.Map(location=[lat, long], zoom_start=16)
    folium.Marker(
        [lat, long]).add_to(m)
    st_folium(m,height=400,width=725)

def temperature_plot(df, before_after, ground_water_line):
    min_x = np.min(df['Temperatur'])-0.5
    max_x = np.max(df['Temperatur'])+0.5
    fig = px.line(y=df["Dybde"], x=df["Temperatur"], title=f'Temperatur i brønn {before_after} test', color_discrete_sequence=['#367A2F', '#FFC358'])
    fig.update_xaxes(title_text='Temperatur [°C]', side='top')
    fig.update_yaxes(title_text='Dybde [m]', autorange='reversed')
    fig.update_xaxes(range=[min_x, max_x])
    if ground_water_line != None:
        fig.add_shape(type='line', x0=min_x, y0=ground_water_line, x1=max_x, y1=ground_water_line, line=dict(color='#007FFF', width=2))
        fig.add_annotation(x=max_x-0.08*(max_x-min_x), y=ground_water_line+0.05*df['Dybde'].iloc[-1], text="Grunnvannsnivå", showarrow=False, font=dict(color="#007FFF", size=14))
    st.plotly_chart(fig, config={'staticPlot': True}, use_container_width=True)

def send_to_database():
    filename_json = f"TRT_info_{project_name}.json"
    dict_for_json = {
        'Prosjektnavn': project_name,
        'Adresse': address,
        'Latitude': lat,
        'Longitude': long,
        'Kontaktperson': contact_person,
        'Kollektorlengde': collector_length,
        'Kollektortype': collector_type,
        'Kollektorvæske': collector_fluid,
        'Brønndiameter': well_diameter,
        'Foringsrørdiameter': casing_diameter,
        'Måledato temperaturprofil før test': str(date_before),
        'Grunnvannsnivå før test': ground_water_level_before,
        'Posisjoner temperaturmålinger før test': str(depth_array_before),
        'Temperaturmålinger før test': str(temp_array_before),
        'Måledato temperaturprofil etter test': str(date_after),
        'Grunnvannsnivå etter test': ground_water_level_after,
        'Posisjoner temperaturmålinger etter test': str(depth_array_after),
        'Temperaturmålinger etter test': str(temp_array_after),
        'Strømmåler før': power_before,
        'Strømmåler etter': power_after,
        'Kommentar': comment
    }

    with open(filename_json, "w") as outfile:
        json.dump(dict_for_json, outfile, default=str)

    # Insert the JSON document into the collection
    key_to_check = {"Prosjektnavn": dict_for_json["Prosjektnavn"]}
    # Check if a document with the specified key already exists
    existing_document = collection.find_one(key_to_check)
    # Insert the JSON document into the collection only if it doesn't already exist
    collection.update_one(key_to_check, {"$set": dict_for_json}, upsert=True)

    return dict_for_json

####################################################
#################### Streamlit #####################
####################################################

streamlit_settings()
st.header('Registrering av termisk responstest')

selected_project_type = st.radio("Valg", options=["Registrer nytt prosjekt", "Fortsett på eksisterende prosjekt"], label_visibility='collapsed')

if selected_project_type == 'Registrer nytt prosjekt': 
    project_name_loaded = ''
    address_loaded = ''
    lat_loaded = 0.0
    long_loaded = 0.0
    contact_person_loaded = ''
    collector_length_loaded = 0
    collector_type_loaded = ''
    collector_fluid_loaded = ''
    well_diameter_loaded = 0
    casing_diameter_loaded = 0
    date_before_loaded = ''
    ground_water_level_before_loaded = None
    depth_array_before_loaded = ''
    temp_array_before_loaded = ''
    date_after_loaded = ''
    ground_water_level_after_loaded = None
    depth_array_after_loaded = ''
    temp_array_after_loaded = ''
    power_before_loaded = None
    power_after_loaded = None
    comment_loaded = ''

client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:jau0IMk5OKJWJ3Xl@cluster0.dlyj4y2.mongodb.net/")
db = client["TRT"]
collection = db["TRT"]
cursor = collection.find({})

if selected_project_type == 'Fortsett på eksisterende prosjekt':
    existing_projects = []
    for doc in cursor:
        existing_projects.append(doc['Prosjektnavn'])
    project_loaded = st.selectbox('Velg prosjekt', options=existing_projects)

if selected_project_type == 'Fortsett på eksisterende prosjekt':
    client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:jau0IMk5OKJWJ3Xl@cluster0.dlyj4y2.mongodb.net/")
    db = client["TRT"]
    collection = db["TRT"]
    cursor = collection.find({})
    for document in cursor:
        if document['Prosjektnavn'] == project_loaded:
            #st.write(document)                                                  ##### AKTIVER DENNE FOR Å VISE DICT I DATABASE
            project_name_loaded = document['Prosjektnavn']
            address_loaded = document['Adresse']
            lat_loaded = document['Latitude']
            long_loaded = document['Longitude']
            contact_person_loaded = document['Kontaktperson']
            collector_length_loaded = document['Kollektorlengde']
            collector_type_loaded = document['Kollektortype']
            collector_fluid_loaded = document['Kollektorvæske']
            well_diameter_loaded = document['Brønndiameter']
            casing_diameter_loaded = document['Foringsrørdiameter']
            date_before_loaded = document['Måledato temperaturprofil før test']
            ground_water_level_before_loaded = document['Grunnvannsnivå før test']
            depth_array_before_loaded = document['Posisjoner temperaturmålinger før test']
            temp_array_before_loaded = document['Temperaturmålinger før test']
            date_after_loaded = document['Måledato temperaturprofil etter test']
            ground_water_level_after_loaded = document['Grunnvannsnivå etter test']
            depth_array_after_loaded = document['Posisjoner temperaturmålinger etter test']
            temp_array_after_loaded = document['Temperaturmålinger etter test']
            power_before_loaded = document['Strømmåler før']
            power_after_loaded = document['Strømmåler etter']
            comment_loaded = document['Kommentar']
            break

if selected_project_type != '':
####################################################
#################### CSS for tabs ##################
####################################################

    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            width: 100%;
            gap: 5px;
            justify-content: space-around; /* Adjust as needed */
        }

        .stTabs [data-baseweb="tab"] {
            flex-grow: 1;
            height: 50px;
            white-space: pre-wrap;
            background-color: #F6F8F1;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
        }

        .stTabs [aria-selected="true"] {
            background-color: #F0F4E3;
            border-bottom: none;
        }
    </style>
    """, unsafe_allow_html=True)

##############################################
#################### Tabs ####################
##############################################
    
    #if "tab1_done" not in st.session_state:
    #    st.session_state.tab1_done = False
    #if "tab2_done" not in st.session_state:
    #    st.session_state.tab2_done = False
    #if "tab3_done" not in st.session_state:
    #    st.session_state.tab3_done = False
    #if "tab4_done" not in st.session_state:
    #    st.session_state.tab4_done = False
    #if "tab5_done" not in st.session_state:
    #    st.session_state.tab5_done = False
    #if "tab6_done" not in st.session_state:
    #    st.session_state.tab6_done = False

    #if st.session_state.tab1_done == True:
    #    tab1_name = 'Om prosjektet ☑'
    #else:
    #    tab1_name = 'Om prosjektet'

    #if st.session_state.tab2_done == True:
    #    tab2_name = 'Brønn & kollektor ☑'
    #else:
    #    tab2_name = 'Brønn & kollektor'

    #if st.session_state.tab3_done == True:
    #    tab3_name = 'Temperatur **før** ☑'
    #else:
    #    tab3_name = 'Temperatur **før**'

    #if st.session_state.tab4_done == True:
    #    tab4_name = 'Temperatur **etter** ☑'
    #else:
    #    tab4_name = 'Temperatur **etter**'

    #if st.session_state.tab5_done == True:
    #    tab5_name = 'Strømmåler ☑'
    #else:
    #    tab5_name = 'Strømmåler'

    #if st.session_state.tab6_done == True:
    #    tab6_name = 'Kommentar ☑'
    #else:
    #    tab6_name = 'Kommentar'

    tab1_name = 'Om prosjektet'
    tab2_name = 'Brønn & kollektor'
    tab3_name = 'Temperatur **før**'
    tab4_name = 'Temperatur **etter**'
    tab5_name = 'Strømmåler'
    tab6_name = 'Kommentar'



    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([tab1_name, tab2_name, tab3_name, tab4_name, tab5_name, tab6_name])
    with tab1:
###################################################################
#################### Informasjon om prosjektet ####################
###################################################################
        if 'coord_system_index' not in st.session_state:
            st.session_state.coord_system_index = 0
        if 'lat_31' not in st.session_state:
            st.session_state.lat_31 = 0.0
        if 'long_31' not in st.session_state:
            st.session_state.long_31 = 0.0
        if 'lat_32' not in st.session_state:
            st.session_state.lat_32 = 0.0
        if 'long_32' not in st.session_state:
            st.session_state.long_32 = 0.0
        if 'lat_33' not in st.session_state:
            st.session_state.lat_33 = 0.0
        if 'long_33' not in st.session_state:
            st.session_state.long_33 = 0.0
        
        if 'changed_coords' not in st.session_state:
            st.session_state.changed_coords = 0

        st.subheader('Informasjon om prosjektet')
        project_name_check = False
        project_name = st.text_input("Navn på prosjektet", value = project_name_loaded)
        if len(project_name) > 0:
            project_name_check = True

        contact_person_check = False
        contact_person = st.text_input(f"Kontaktperson", value = str(contact_person_loaded))
        if len(contact_person) > 0:
            contact_person_check = True

        #placement_selection = st.selectbox("Plassering av brønn", options=["Skriv inn adresse og plasser på kart", "Skriv inn koordinater"], index=0)
        placement_selection = "Skriv inn adresse og plasser på kart"
        [address, lat, long, lat_lon_check] = well_placement_input(placement_selection)

#        if len(contact_person) > 0:
#            st.session_state.contact_person = contact_person
            
#        if (len(project_name) > 0) and len(contact_person) > 0:
            #st.session_state.tab1_done = True
#            tab1_done = True
        

    with tab2:
############################################################
#################### Brønn og kollektor ####################
############################################################

        st.subheader('Brønn og kollektor')
        collector_length_check = False
        if collector_length_loaded == 0:
            collector_length_loaded = None
        collector_length = st.number_input("Kollektorlengde [m]", min_value = None, value = collector_length_loaded, step = 10)
        if collector_length == None:
            collector_length = 0

            #if collector_length > 0:
                #if collector_length != st.session_state.collector_length:
                #    st.session_state.df_before = pd.DataFrame()
                #    st.session_state.depth_array_before = np.arange(0,0)
                #    st.session_state.temp_array_before = np.arange(0,0)
                #    st.session_state.df_after = pd.DataFrame()
                #    st.session_state.depth_array_after = np.arange(0,0)
                #    st.session_state.temp_array_after = np.arange(0,0)
                #st.session_state.collector_length = collector_length 
        if collector_length > 0: 
            collector_length_check = True

        collector_type_check = False
        collector_type_list = ['',"Enkel-U", "Dobbel-U","Egendefinert"]
        if collector_type_loaded in collector_type_list: 
            collector_type_index = collector_type_list.index(collector_type_loaded)
        else:
            collector_type_index = 3
        collector_type = st.selectbox("Kollektortype", collector_type_list, index=collector_type_index, placeholder = "Velg", key = "bk1")  
        
        if collector_type == "Egendefinert":
            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                collector_type = st.text_input("Skriv inn kollektortype", value = collector_type_loaded)
        if collector_type != '':
            collector_type_check = True
        
        collector_fluid_check = False
        collector_fluid_list = ['', "HX24", "HX35", "Kilfrost Geo 24 %", "Kilfrost Geo 30 %", "Kilfrost Geo 35 %", "Egendefinert"]
        if collector_fluid_loaded in collector_fluid_list:
            collector_fluid_index = collector_fluid_list.index(collector_fluid_loaded)
        else:
            collector_fluid_index = 6

        collector_fluid = st.selectbox("Kollektorvæske", options = collector_fluid_list, index=collector_fluid_index, placeholder="Velg", key = "bk2")
        if collector_fluid == "Egendefinert":
            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                collector_fluid = st.text_input("Skriv inn kollektorvæske",value=collector_fluid_loaded)
        if collector_fluid != '':
            collector_fluid_check = True
        
        well_diameter_check = False
        well_diameter_list = ['', "115 mm", "Egendefinert"]
        if well_diameter_loaded == 0:
            well_diameter_index = 0
        elif f'{str(well_diameter_loaded)} mm' in well_diameter_list:
            well_diameter_index = well_diameter_list.index(f'{str(well_diameter_loaded)} mm')
        else:
            well_diameter_index = 2
        well_diameter_str = st.selectbox("Diameter borehull", options=well_diameter_list, index=well_diameter_index, placeholder="Velg", key = "bk3")
        if well_diameter_str == "Egendefinert":
            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                well_diameter = st.number_input("Egendefinert borehull-diameter (mm)", value=well_diameter_loaded, min_value=0, step=1)
        elif 'mm' in well_diameter_str:
            well_diameter = int(well_diameter_str.replace(' mm',''))
        else:
            well_diameter = 0
        if well_diameter > 0:
            well_diameter_check = True

        casing_diameter_check = False
        casing_diameter_list = ['', "139 mm", "Egendefinert"]
        if casing_diameter_loaded == 0:
            casing_diameter_index = 0
        elif f'{str(casing_diameter_loaded)} mm' in casing_diameter_list:
            casing_diameter_index = casing_diameter_list.index(f'{str(casing_diameter_loaded)} mm')
        else:
            casing_diameter_index = 2
        casing_diameter_str = st.selectbox("Diameter foringsrør", options=casing_diameter_list, index=casing_diameter_index, placeholder="Velg", key = "bk4")
        if casing_diameter_str == "Egendefinert":
            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                casing_diameter = st.number_input("Egendefinert foringsrør-diameter (mm)", value=casing_diameter_loaded, min_value=0, step=1)
        elif 'mm' in casing_diameter_str:
            casing_diameter = int(casing_diameter_str.replace(' mm',''))
        else:
            casing_diameter = 0
        if casing_diameter > 0:
            casing_diameter_check = True

    with tab3:
        ########## TEMPERATURPROFIL FØR #################################################################################################################################################################
        st.subheader('Temperaturprofil før test')
        date_before_check = False
        if date_before_loaded == '':
            date_before_startvalue = date.today()
        else:
            date_before_startvalue = datetime.strptime(date_before_loaded, '%Y-%m-%d')
        date_before = st.date_input("Måledato (før test)", value = date_before_startvalue)
        if date_before_loaded != date.today():
            date_before_check = True
        
        ground_water_level_before_check = False
        ground_water_level_before = st.number_input("Grunnvannsnivå før test [m]", value = ground_water_level_before_loaded, step = 1)
        if ground_water_level_before != None:
            ground_water_level_before_check = True

        temp_array_before_check = False
        if depth_array_before_loaded == '':
            step_before_startvalue = 10
        else:
            elements = depth_array_before_loaded.replace('None', 'np.nan').strip('[]').split()
            loaded_array_before = np.array([int(elem) for elem in elements])
            if loaded_array_before[-1] is not None:
                try:
                    step_before_startvalue = int(loaded_array_before[1])
                except:
                    step_before_startvalue = 10
            else:
                step_before_startvalue = 10
        step_before = st.number_input('Oppløsning på temperaturmålinger [m]', min_value=1, step=1, value=step_before_startvalue, key='step_before_key')
        
        if depth_array_before_loaded == '' or depth_array_before_loaded == '[0]':
            depth_array = np.arange(0, collector_length + step_before, step_before)
            temperature_array = np.arange(0, collector_length + step_before, step_before)
            temperature_array = np.full(len(temperature_array), float('nan'))
        else:
            depth_array = loaded_array_before

        with st.form("j"):
            if temp_array_before_loaded == '' or temp_array_before_loaded == '[nan]':
                temperature_array = np.arange(0, collector_length + step_before, step_before)
                temperature_array = np.full(len(temperature_array), float('nan'))
            else:
                elements2 = temp_array_before_loaded.replace('None', 'nan').strip('[]').split()
                temperature_array = np.array([float(elem) for elem in elements2])
            
            df_before = pd.DataFrame({"Dybde" : depth_array, "Temperatur" : temperature_array})
            
            edited_df_before = st.data_editor(
                df_before, 
                hide_index = True, 
                use_container_width=True,
                column_config={
                    "Temperatur": st.column_config.NumberColumn("Temperatur", format="%.1f °C"),
                    "Dybde": st.column_config.NumberColumn("Dybde", format="%f m", )
                    },
                key = "temperature_before_df"
                )

            depth_array_before = np.array(edited_df_before['Dybde'])
            temp_array_before = np.array(edited_df_before['Temperatur'])

            #if edited_df_before["Temperatur"].count() >= 5:   #Lar deg gå videre hvis det er fylt inn minst 5 tall
            if edited_df_before["Temperatur"].isna().sum() == 0:
                temp_array_before_check = True

            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                submitted = st.form_submit_button("Oppdater tabell")
                if submitted:
                    st.rerun()

        temperature_plot(df = edited_df_before, before_after='før', ground_water_line=ground_water_level_before)

    with tab4:
        ########## TEMPERATURPROFIL ETTER #################################################################################################################################################################
        
        st.subheader('Temperaturprofil etter test')
        # Hvordan sjekke om denne datoen er riktig? Denne kan jo være date.today() uten at det er feil.
        if date_after_loaded == '':
            date_after_startvalue = date.today()
        else:
            date_after_startvalue = datetime.strptime(date_after_loaded, '%Y-%m-%d')
        date_after = st.date_input("Måledato (etter test)", value = date_after_startvalue)
        
        ground_water_level_after_check = False
        ground_water_level_after = st.number_input("Grunnvannsnivå etter test [m]", value = ground_water_level_after_loaded, step = 1)
        if ground_water_level_after != None:
            ground_water_level_after_check = True

        temp_array_after_check = False
        if depth_array_after_loaded == '':
            step_after_startvalue = 10
        else:
            elements = depth_array_after_loaded.replace('None', 'np.nan').strip('[]').split()
            loaded_array_after = np.array([int(elem) for elem in elements])
            if loaded_array_after[-1] is not None:
                try:
                    step_after_startvalue = int(loaded_array_after[1])
                except:
                    step_after_startvalue = 10
            else:
                step_after_startvalue = 10
        step_after = st.number_input('Oppløsning på temperaturmålinger [m]', min_value=1, step=1, value=step_after_startvalue, key='step_after_key')
            
        with st.form("k"):
            if depth_array_after_loaded == '' or depth_array_after_loaded == '[0]':
                depth_array = np.arange(0, collector_length + step_after, step_after)
                temperature_array = np.arange(0, collector_length + step_after, step_after)
                temperature_array = np.full(len(temperature_array), float('nan'))
            else:
                depth_array = loaded_array_after

            if temp_array_after_loaded == '' or temp_array_after_loaded == '[nan]':
                temperature_array = np.arange(0, collector_length + step_after, step_after)
                temperature_array = np.full(len(temperature_array), float('nan'))
            else:
                elements2 = temp_array_after_loaded.replace('None', 'nan').strip('[]').split()
                temperature_array = np.array([float(elem) for elem in elements2])
            
            df_after = pd.DataFrame({"Dybde" : depth_array, "Temperatur" : temperature_array})
            
            edited_df_after = st.data_editor(
                df_after, 
                hide_index = True, 
                use_container_width=True,
                column_config={
                    "Temperatur": st.column_config.NumberColumn("Temperatur", format="%.1f °C"),
                    "Dybde": st.column_config.NumberColumn("Dybde", format="%f m", )
                    },
                key = "temperature_after_df"
                )

            depth_array_after = np.array(edited_df_after['Dybde'])
            temp_array_after = np.array(edited_df_after['Temperatur'])

            #if edited_df_after["Temperatur"].count() >= 5:   #Lar deg gå videre hvis det er fylt inn minst 5 tall
            if edited_df_after["Temperatur"].isna().sum() == 0:
                temp_array_after_check = True
            c1,c2,c3 = st.columns([0.05,1,0.05])
            with c2:
                submitted = st.form_submit_button("Oppdater tabell")
                if submitted:
                    st.rerun()
        
        temperature_plot(df = edited_df_after, before_after='etter', ground_water_line=ground_water_level_after)

    with tab5:
        ########## STRØMMÅLER #################################################################################################################################################################
        st.subheader('Strømmåler før og etter test')
        
        power_before_check = False
        power_before = st.number_input("Strømmåler før", value = power_before_loaded)
        if power_before != None:
            power_before_check = True
        #power_before_file = st.file_uploader("Last gjerne opp bilde av strømmåler før test")

        power_after_check = False
        power_after = st.number_input("Strømmåler etter", value = power_after_loaded)
        if power_after != None:
            power_after_check = True
        #power_after_file = st.file_uploader("Last gjerne opp bilde av strømmåler etter test")

    with tab6:    
        ########## KOMMENTARER #################################################################################################################################################################
        st.subheader('Kommentarer')
        comment = st.text_area("Eventuelle kommentarer", value=comment_loaded)
        #uploaded_files = st.file_uploader("Last opp eventuelle vedlegg (bilder, testdata, andre filer)", accept_multiple_files=True)
        if len(comment) > 0:
            #st.session_state.tab6_done = True
            tab6_done = True

    #st.markdown('---')
    #make_file_button = st.button('Lag fil/Fullfør/(...)')

    ########## LAGRE TIL JSON-FIL #################################################################################################################################################################

    # Hvis databasen ikke er oppdatert: Rerun én gang slik at den blir det.
    dict_for_json_loaded = send_to_database()
    
    if selected_project_type == 'Fortsett på eksisterende prosjekt':
        document.pop("_id")
        if document != dict_for_json_loaded:
            st.rerun()
    
    
    # Define your JSON document

    #filename_json = f"TRT_info_{project_name}.json"
    #dict_for_json = {
    #    'Prosjektnavn': project_name,
    #    'Adresse': address,
    #    'Latitude': lat,
    #    'Longitude': long,
    #    'Kontaktperson': contact_person,
    #    'Kollektorlengde': collector_length,
    #    'Kollektortype': collector_type,
    #    'Kollektorvæske': collector_fluid,
    #    'Brønndiameter': well_diameter,
    #    'Foringsrørdiameter': casing_diameter,
    #    'Måledato temperaturprofil før test': str(date_before),
    #    'Grunnvannsnivå før test': ground_water_level_before,
    #    'Posisjoner temperaturmålinger før test': str(depth_array_before),
    #    'Temperaturmålinger før test': str(temp_array_before),
    #    'Måledato temperaturprofil etter test': str(date_after),
    #    'Grunnvannsnivå etter test': ground_water_level_after,
    #    'Posisjoner temperaturmålinger etter test': str(depth_array_after),
    #    'Temperaturmålinger etter test': str(temp_array_after),
    #    'Strømmåler før': power_before,
    #    'Strømmåler etter': power_after,
    #    'Kommentar': comment
    #}

    #with open(filename_json, "w") as outfile:
    #    json.dump(dict_for_json, outfile, default=str)

    # Insert the JSON document into the collection
    #key_to_check = {"Prosjektnavn": dict_for_json["Prosjektnavn"]}
    # Check if a document with the specified key already exists
    #existing_document = collection.find_one(key_to_check)
    # Insert the JSON document into the collection only if it doesn't already exist
    #collection.update_one(key_to_check, {"$set": dict_for_json}, upsert=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Gå tilbake til forside"):
            switch_page('Hjem')
    with c2:
        submit_button = st.button('Send inn skjema')
        
    checks = [project_name_check, contact_person_check, lat_lon_check, collector_length_check, collector_type_check, collector_fluid_check, well_diameter_check, casing_diameter_check, date_before_check,
              ground_water_level_before_check, temp_array_before_check, ground_water_level_after_check, temp_array_after_check, power_before_check, power_after_check]
    checked_inputs_names = ['• Navn på prosjektet', '• Kontaktperson', '• Plassering av brønn', '• Kollektorlengde', '• Kollektortype', '• Kollektorvæske', '• Diameter borehull', '• Diameter foringsrør', 
                            '• Måledato før test', '• Grunnvannsnivå før test', '• Temperaturmålinger før test', '• Grunnvannsnivå etter test', '• Temperaturmålinger etter test', '• Strømmåler før test',
                            '• Strømmåler etter test']
    missing_inputs = []
    
    if submit_button:
        for i in range(0,len(checks)):
            if checks[i] == False:
                missing_inputs.append(checked_inputs_names[i])

        if len(missing_inputs) > 0:
            missing_inputs_str = '''  \n  '''.join(missing_inputs)
            st.warning(f"""
            **Følgende felter må fylles ut:**   
               {missing_inputs_str}   
            """)
        else:
            st.success('Innsending vellykket')
        #st.rerun()
