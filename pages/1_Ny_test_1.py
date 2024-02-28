import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
import numpy as np
import base64
import plotly.express as px
from PIL import Image
import pymongo
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
from src.scripts import streamlit_settings, switch_pages, toggle_closed_expander

import requests
import re
import folium
from streamlit_folium import st_folium
from datetime import date
import utm
import csv
import json

########## FUNKSJONER #################################################################################################################################################################
def well_placement_input(text_string):
    if text_string == "Skriv inn adresse og plasser på kart":
        c1, c2 = st.columns(2)
        with c1:
            address = st.text_input("Søk etter addresse",value=st.session_state.address)
        with c2:
            place = st.text_input("Legg by/sted til søket (hvis nødvendig)",value=st.session_state.place)
        
        if len(address)>2:
            st.session_state.address = address
            st.session_state.place = place

            [lat,long] = adresse_til_koordinat(address,place)
            if lat != lat or long != long:
                st.info('Adresse ikke funnet, prøv en annen skrivemåte, eller velg å skrive inn koordinater.')
            else:
                #map_with_point(lat,long)
                st.write('Klikk på kartet for å velge plassering av brønnen:')
                m = folium.Map(location=[lat, long], zoom_start=16)
                if st.session_state.lat != None:
                    folium.Marker([st.session_state.lat, st.session_state.long]).add_to(m)
                m.add_child(folium.LatLngPopup())
                coord_json = st_folium(m,height=400,width=725)
                
                if coord_json['last_clicked']:
                    lat = coord_json['last_clicked']['lat']
                    long = coord_json['last_clicked']['lng']
                    
                    st.session_state.lat = float(lat)
                    st.session_state.long = float(long)
                
                    c1,c2 = st.columns(2)
                    with c1:
                        st.metric('Valgt breddegrad:',st.session_state.lat)
                    with c2:
                        st.metric('Valgt lengdegrad:',st.session_state.long)
                    

    elif text_string == "Skriv inn koordinater":
        coord_system_options = ['EU89 - Geografisk, grader (Lat/Lon)', 'EU89, UTM-sone 31', 'EU89, UTM-sone 32', 'EU89, UTM-sone 33']
        projection = st.selectbox('Velg koordinatsystem',options=coord_system_options,index=st.session_state.coord_system_index)
        if projection != coord_system_options[st.session_state.coord_system_index]:
            st.session_state.changed_coords = 0
            st.session_state.coord_system_index = coord_system_options.index(projection)
        
        if projection == 'EU89 - Geografisk, grader (Lat/Lon)':
            if st.session_state.lat != None:
                ns_value = st.session_state.long
                ov_value = st.session_state.lat
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
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(st.session_state.lat, st.session_state.long, 31, 'V')
                    st.session_state.lat_31 = utm_tuple[0]
                    st.session_state.long_31 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_31
                ov_value = st.session_state.lat_31
                
            elif projection == 'EU89, UTM-sone 32':
                zone = 32
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(st.session_state.lat, st.session_state.long, 32, 'V')
                    st.session_state.lat_32 = utm_tuple[0]
                    st.session_state.long_32 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_32
                ov_value = st.session_state.lat_32
            
            elif projection == 'EU89, UTM-sone 33':
                zone = 33
                if st.session_state.changed_coords < 1:
                    utm_tuple = utm.from_latlon(st.session_state.lat, st.session_state.long, 33, 'V')
                    st.session_state.lat_33 = utm_tuple[0]
                    st.session_state.long_33 = utm_tuple[1]
                    st.session_state.changed_coords = st.session_state.changed_coords + 1
                ns_value = st.session_state.long_33
                ov_value = st.session_state.lat_33

        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input("Breddegrad/Latitude (Nord-koordinat/ØV)", value = ov_value, step=step_length, format=number_format)
        with c2:
            long = st.number_input("Lengdegrad/Longitude (Øst-koordinat/NS)", value = ns_value, step=step_length, format=number_format)
        
        if zone > 0:
            #utm_tuple = utm.to_latlon(lat/10, long/10, zone, 'V')
            utm_tuple = utm.to_latlon(lat, long, zone, 'V')
            lat = utm_tuple[0]
            long = utm_tuple[1]
        
        st.session_state.lat = lat
        st.session_state.long = long
        map_with_point(st.session_state.lat,st.session_state.long)
    
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
        #m.add_child(folium.LatLngPopup())
        st_folium(m,height=400,width=725)

def temperature_plot(df, before_after):
    min_x = np.min(df['Temperatur'])-0.5
    max_x = np.max(df['Temperatur'])+0.5
    fig = px.line(y=df["Dybde"], x=df["Temperatur"], title=f'Temperatur i brønn {before_after} test', color_discrete_sequence=['#367A2F', '#FFC358'])
    fig.update_xaxes(title_text='Temperatur [°C]', side='top')
    fig.update_yaxes(title_text='Dybde [m]', autorange='reversed')
    fig.update_xaxes(range=[min_x, max_x])
    st.plotly_chart(fig, config={'staticPlot': True}, use_container_width=True)

streamlit_settings()

########## INFORMASJON OM PROSJEKTET #################################################################################################################################################################
if 'project_name' not in st.session_state:
    st.session_state.project_name = ""

if 'placement_type_index' not in st.session_state:
    st.session_state.placement_type_index = 1

if 'address' not in st.session_state:
    st.session_state.address = ''
if 'place' not in st.session_state:
    st.session_state.place = ''
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

if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'long' not in st.session_state:
    st.session_state.long = None

if 'contact_person' not in st.session_state:
    st.session_state.contact_person = ""

if "project_info_expanded" not in st.session_state:
    st.session_state.project_info_expanded = True
if "project_info_check" not in st.session_state:
    st.session_state.project_info_check = False
if st.session_state.project_info_check == True:
    project_info_check = "✅"
else:
    project_info_check = "✗"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
with st.expander(f"{project_info_check} Informasjon om prosjektet", expanded=st.session_state.project_info_expanded):
    project_name = st.text_input("Navn på prosjektet", value = st.session_state.project_name)
    if len(project_name) > 0:
        st.session_state.project_name = project_name
    
    placement_options = ["Skriv inn koordinater","Skriv inn adresse og plasser på kart"]
    placement_selection = st.selectbox("Plassering av brønn", options=placement_options, index=st.session_state.placement_type_index)
    well_placement_input(placement_selection)
    if placement_selection != placement_options[st.session_state.placement_type_index]:
        st.session_state.changed_coords = 0
        st.session_state.placement_type_index = placement_options.index(placement_selection)

    contact_person = st.text_input(f"Kontaktperson", value = st.session_state.contact_person)
    if len(contact_person) > 0:
        st.session_state.contact_person = contact_person

    if (len(project_name) > 0) and len(contact_person) > 0:
        if st.button("Registrer", on_click=toggle_closed_expander("project_info_expanded", "project_info_check"), key = "project"):
            st.experimental_rerun()

########## BRØNN OG KOLLEKTOR #################################################################################################################################################################
if 'collector_length' not in st.session_state:
    st.session_state.collector_length = 0

if 'collector_type_index' not in st.session_state:
    st.session_state.collector_type_index = 0
if 'collector_type' not in st.session_state:
    st.session_state.collector_type = ''
if 'collector_type_custom' not in st.session_state:
    st.session_state.collector_type_custom = ''

if 'collector_fluid_index' not in st.session_state:
    st.session_state.collector_fluid_index = 0
if 'collector_fluid' not in st.session_state:
    st.session_state.collector_fluid = 0
if 'collector_fluid_custom' not in st.session_state:
    st.session_state.collector_fluid_custom = 0

if 'well_diameter_index' not in st.session_state:
    st.session_state.well_diameter_index = 0
if 'well_diameter' not in st.session_state:
    st.session_state.well_diameter = 0
if 'well_diameter_custom' not in st.session_state:
    st.session_state.well_diameter_custom = 0

if 'casing_diameter_index' not in st.session_state:
    st.session_state.casing_diameter_index = 0
if 'casing_diameter' not in st.session_state:
    st.session_state.casing_diameter = 0
if 'casing_diameter_custom' not in st.session_state:
    st.session_state.casing_diameter_custom = 0

if "technical_info_expanded" not in st.session_state:
    st.session_state.technical_info_expanded = False
if "technical_info_check" not in st.session_state:
    st.session_state.technical_info_check = False
if st.session_state.technical_info_check == True:
    technical_info_check = "✅"
else:
    technical_info_check = "✗"

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with st.expander(f"{technical_info_check} Brønn og kollektor", expanded=st.session_state.technical_info_expanded):

    collector_length = st.number_input("Kollektorlengde [m]", min_value = None, value = st.session_state.collector_length, step = 10)
    if collector_length > 0:
        if collector_length != st.session_state.collector_length:
            st.session_state.df_before = pd.DataFrame()
            st.session_state.depth_array_before = np.arange(0,0)
            st.session_state.temp_array_before = np.arange(0,0)
            st.session_state.df_after = pd.DataFrame()
            st.session_state.depth_array_after = np.arange(0,0)
            st.session_state.temp_array_after = np.arange(0,0)
        st.session_state.collector_length = collector_length 

    collector_type_list = ['',"Enkel-U", "Dobbel-U","Egendefinert"]    
    collector_type = st.selectbox("Kollektortype", collector_type_list, index=st.session_state.collector_type_index, placeholder = "Velg", key = "bk1") 
    if collector_type != '':
        st.session_state.collector_type_index = collector_type_list.index(collector_type)
    if collector_type == "Egendefinert":
        c1,c2,c3 = st.columns([0.05,1,0.05])
        with c2:
            collector_type = st.text_input("Skriv inn kollektortype",value =st.session_state.collector_type_custom)
        st.session_state.collector_type_custom = collector_type
    st.session_state.collector_type = collector_type
    
    collector_fluid_list = ['', "HX24", "HX35", "Kilfrost Geo 24 %", "Kilfrost Geo 30 %", "Kilfrost Geo 35 %", "Egendefinert"]
    collector_fluid = st.selectbox("Kollektorvæske", options = collector_fluid_list, index=st.session_state.collector_fluid_index, placeholder="Velg", key = "bk2")
    if collector_fluid != '':
        st.session_state.collector_fluid_index = collector_fluid_list.index(collector_fluid)
    if collector_fluid == "Egendefinert":
        c1,c2,c3 = st.columns([0.05,1,0.05])
        with c2:
            collector_fluid = st.text_input("Skriv inn kollektorvæske",value=st.session_state.collector_fluid_custom)
        st.session_state.collector_fluid_custom = collector_fluid
    st.session_state.collector_fluid = collector_fluid
    
    well_diameter_list = ['', "115 mm", "Egendefinert"]
    well_diameter_str = st.selectbox("Diameter borehull", options=well_diameter_list, index=st.session_state.well_diameter_index, placeholder="Velg", key = "bk3")
    st.session_state.well_diameter_index = well_diameter_list.index(well_diameter_str)
    if well_diameter_str == "Egendefinert":
        c1,c2,c3 = st.columns([0.05,1,0.05])
        with c2:
            well_diameter = st.number_input("Egendefinert borehull-diameter (mm)", value=st.session_state.well_diameter_custom, min_value=0, step=1)
        st.session_state.well_diameter_custom = well_diameter
    elif 'mm' in well_diameter_str:
        well_diameter = int(well_diameter_str.replace(' mm',''))
    else:
        well_diameter = None
    if well_diameter_str != '':
        st.session_state.well_diameter = well_diameter

    casing_diameter_list = ['', "139 mm", "Egendefinert"]
    casing_diameter_str = st.selectbox("Diameter foringsrør", options=casing_diameter_list, index=st.session_state.casing_diameter_index, placeholder="Velg", key = "bk4")
    st.session_state.casing_diameter_index = casing_diameter_list.index(casing_diameter_str)
    if casing_diameter_str == "Egendefinert":
        c1,c2,c3 = st.columns([0.05,1,0.05])
        with c2:
            casing_diameter = st.number_input("Egendefinert foringsrør-diameter (mm)", value=st.session_state.casing_diameter_custom, min_value=0, step=1)
        st.session_state.casing_diameter_custom = casing_diameter
    elif 'mm' in casing_diameter_str:
        casing_diameter = int(casing_diameter_str.replace(' mm',''))
    else:
        casing_diameter = None
    if casing_diameter_str != '':
        st.session_state.casing_diameter = casing_diameter
    
    if collector_type != None and collector_fluid != None and collector_length != None and well_diameter != None and casing_diameter != None:
        st.button("Registrer", on_click=toggle_closed_expander("technical_info_expanded", "technical_info_check"), key = "technical")

########## TEMPERATURPROFIL FØR #################################################################################################################################################################
if 'date_before' not in st.session_state:
    st.session_state.date_before = date.today()
if 'ground_water_level_before' not in st.session_state:
    st.session_state.ground_water_level_before = 0
if 'step_before' not in st.session_state:
    st.session_state.step_before = 10
if 'df_before' not in st.session_state or 'df_before' == 'RESET':
    st.session_state.df_before = pd.DataFrame()
if 'depth_array_before' not in st.session_state or 'depth_array_before' == 'RESET':
    st.session_state.depth_array_before = np.arange(0,0)
if 'temp_array_before' not in st.session_state or 'temp_array_before' == 'RESET':
    st.session_state.temp_array_before = np.arange(0,0)

if "temperature_before_expanded" not in st.session_state:
    st.session_state.temperature_before_expanded = False
if "temperature_before_check" not in st.session_state:
    st.session_state.temperature_before_check = False
if st.session_state.temperature_before_check == True:
    temperature_before_check = "✅"
else:
    temperature_before_check = "✗"  

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with st.expander(f"{temperature_before_check} Temperaturprofil før", expanded=st.session_state.temperature_before_expanded):
    date_before = st.date_input("Måledato (før test)", value = st.session_state.date_before)
    st.session_state.date_before = date_before
    ground_water_level_before = st.number_input("Grunnvansnivå før test [m]", value = st.session_state.ground_water_level_before, step = 1)
    st.session_state.ground_water_level_before = ground_water_level_before
    step_before = st.number_input('Oppløsning på temperaturmålinger (m)', min_value=1, step=1, value=st.session_state.step_before, key='step_before_key')
    if step_before != st.session_state.step_before:
        st.session_state.df_before = pd.DataFrame()
        st.session_state.depth_array_before = np.arange(0,0)
        st.session_state.temp_array_before = np.arange(0,0)
    st.session_state.step_before = step_before
    
    depth_array = np.arange(0, collector_length + step_before, step_before)
    temperature_array = np.arange(0, collector_length + step_before, step_before)
    temperature_array = np.full(len(temperature_array), None)
    if st.session_state.df_before.empty:
        df_before = pd.DataFrame({"Dybde" : depth_array, "Temperatur" : temperature_array})
    else:
        df_before = st.session_state.df_before
    
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
    st.session_state.date_before = date_before
    st.session_state.ground_water_level_before = ground_water_level_before
    st.session_state.depth_array_before = np.array(edited_df_before['Dybde'])
    st.session_state.temp_array_before = np.array(edited_df_before['Temperatur'])

    temperature_plot(df = edited_df_before, before_after='før')
    #if edited_df_before["Temperatur"].count() >= 5:   #Lar deg gå videre hvis det er fylt inn minst 5 tall
    if edited_df_before["Temperatur"].isna().sum() == 0:
        st.session_state.df_before = edited_df_before
        st.button("Registrer", on_click=toggle_closed_expander("temperature_before_expanded", "temperature_before_check"), key = "temperature_before")

########## TEMPERATURPROFIL ETTER #################################################################################################################################################################
if 'date_after' not in st.session_state:
    st.session_state.date_after = date.today()
if 'ground_water_level_after' not in st.session_state:
    st.session_state.ground_water_level_after = 0
if 'step_after' not in st.session_state:
    st.session_state.step_after = 10
if 'df_after' not in st.session_state:
    st.session_state.df_after = pd.DataFrame()
if 'depth_array_after' not in st.session_state:
    st.session_state.depth_array_after = np.arange(0,0)
if 'temp_array_after' not in st.session_state:
    st.session_state.temp_array_after = np.arange(0,0)

if "temperature_after_expanded" not in st.session_state:
    st.session_state.temperature_after_expanded = False
if "temperature_after_check" not in st.session_state:
    st.session_state.temperature_after_check = False
if st.session_state.temperature_after_check == True:
    temperature_after_check = "✅"
else:
    temperature_after_check = "✗"  

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with st.expander(f"{temperature_after_check} Temperaturprofil etter", expanded=st.session_state.temperature_after_expanded):
    date_after = st.date_input("Måledato (etter test)", value = st.session_state.date_after)
    st.session_state.date_after = date_after
    ground_water_level_after = st.number_input("Grunnvansnivå etter test [m]", value = st.session_state.ground_water_level_after, step = 1)
    st.session_state.ground_water_level_after = ground_water_level_after
    step_after = st.number_input('Oppløsning på temperaturmålinger (m)', min_value=1, step=1, value=st.session_state.step_after, key='step_after_key')
    if step_after != st.session_state.step_after:
        st.session_state.df_after = pd.DataFrame()
        st.session_state.depth_array_after = np.arange(0,0)
        st.session_state.temp_array_after = np.arange(0,0)
    st.session_state.step_after = step_after
    
    depth_array = np.arange(0, collector_length + step_after, step_after)
    temperature_array = np.arange(0, collector_length + step_after, step_after)
    temperature_array = np.full(len(temperature_array), None)
    if st.session_state.df_after.empty:
        df_after = pd.DataFrame({"Dybde" : depth_array, "Temperatur" : temperature_array})
    else:
        df_after = st.session_state.df_after
    
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
    st.session_state.date_after = date_after
    st.session_state.ground_water_level_after = ground_water_level_after
    st.session_state.depth_array_after = np.array(edited_df_after['Dybde'])
    st.session_state.temp_array_after = np.array(edited_df_after['Temperatur'])

    temperature_plot(df = edited_df_after, before_after='etter')
    #if edited_df_after["Temperatur"].count() >= 5:   #Lar deg gå videre hvis det er fylt inn minst 5 tall
    if edited_df_after["Temperatur"].isna().sum() == 0:
        st.session_state.df_after = edited_df_after
        st.button("Registrer", on_click=toggle_closed_expander("temperature_after_expanded", "temperature_after_check"), key = "temperature_after")

########## STRØMMÅLER FØR #################################################################################################################################################################
if 'power_before' not in st.session_state:
    st.session_state.power_before = 0

if "power_before_expanded" not in st.session_state:
    st.session_state.power_before_expanded = False
if "power_before_check" not in st.session_state:
    st.session_state.power_before_check = False
if st.session_state.power_before_check == True:
    power_before_check = "✅"
else:
    power_before_check = "✗"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with st.expander(f"{power_before_check} Strømmåler før", expanded=st.session_state.power_before_expanded):
    power_before = st.number_input("Strømmåler før", value = st.session_state.power_before)
    power_before_file = st.file_uploader("Last gjerne opp bilde av strømmåler før test")
    if power_before > 0:
        st.session_state.power_before = power_before
    if power_before > 0:
        st.button("Registrer", on_click=toggle_closed_expander("power_before_expanded", "power_before_check"), key = "power_before_button") 
    
########## STRØMMÅLER ETTER #################################################################################################################################################################
if 'power_after' not in st.session_state:
    st.session_state.power_after = 0

if "power_after_expanded" not in st.session_state:
    st.session_state.power_after_expanded = False
if "power_after_check" not in st.session_state:
    st.session_state.power_after_check = False
if st.session_state.power_after_check == True:
    power_after_check = "✅"
else:
    power_after_check = "✗"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with st.expander(f"{power_after_check} Strømmåler etter", expanded=st.session_state.power_after_expanded):
    power_after = st.number_input("Strømmåler etter", value = st.session_state.power_after)
    power_after_file = st.file_uploader("Last gjerne opp bilde av strømmåler etter test")
    if power_after > 0:
        st.session_state.power_after = power_after
    if power_after > 0:
        st.button("Registrer", on_click=toggle_closed_expander("power_after_expanded", "power_after_check"), key = "power_after_button") 
    
########## KOMMENTARER #################################################################################################################################################################
if 'comment' not in st.session_state:
    st.session_state.comment = ''
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
comment = st.text_area("Eventuelle kommentarer", value=st.session_state.comment)
st.session_state.comment = comment
uploaded_files = st.file_uploader("Last opp eventuelle vedlegg (bilder, testdata, andre filer)", accept_multiple_files=True)

make_file_button = st.button('Lag fil/Fullfør/(...)')

########## SIDEBYTTE #################################################################################################################################################################
switch_pages(previous_page_destination="Hjem", previous_page_text="Forrige", next_page_destination="Neste", next_page_text = "Ny_test_2")


#client = pymongo.MongoClient(**st.secrets["mongo"])
#client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:ocCjTVUFd7ox5jUQ@atlascluster.gkdobnl.mongodb.net/")
#mydb = client["trt_database"]
#mycol = mydb["prosjekter"]

#new_data = {
#    'prosjektnavn': f'{project_name}', 
#    'kollektorvæske': f'{collector_fluid}', 
#    'kontaktperson': f'{contact_person}',
#    'kollektortype' : f'{collector_type}',
#    'kollektorvæske' : f'{collector_fluid}',
#    'kollektorlengde' : f'{collector_length}',
#    'diameter_foringsrør' : f'{casing_diameter}',
#    'temperaturprofil_før_dato' : f'{date_before}',
#    }

#filter_criteria = {'prosjektnavn': f'{project_name}'}
#mycol.update_one(filter_criteria, {'$set': new_data}, upsert=True)

########## LAGRE TIL CSV-FIL #################################################################################################################################################################

if make_file_button == True:

    filename = f"TRT_info_{st.session_state.project_name}.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        writer.writerow(['Prosjektnavn', st.session_state.project_name])
        writer.writerow(['Latitude', st.session_state.lat])
        writer.writerow(['Longitude', st.session_state.long])
        writer.writerow(['Kontaktperson', st.session_state.contact_person])
        
        writer.writerow(['Kollektorlengde', st.session_state.collector_length])
        writer.writerow(['Kollektortype', st.session_state.collector_type])
        writer.writerow(['Kollektorvæske', st.session_state.collector_fluid])
        writer.writerow(['Brønndiameter', st.session_state.well_diameter])
        writer.writerow(['Foringsrørdiameter', st.session_state.casing_diameter])
        
        writer.writerow(['Måledato temperaturprofil før test', st.session_state.date_before])
        writer.writerow(['Grunnvannsnivå før test', st.session_state.ground_water_level_before])
        writer.writerow(['Posisjoner temperaturmålinger før test', st.session_state.depth_array_before])
        writer.writerow(['Temperaturmålinger før test', st.session_state.temp_array_before])
        
        writer.writerow(['Måledato temperaturprofil etter test', st.session_state.date_after])
        writer.writerow(['Grunnvannsnivå etter test', st.session_state.ground_water_level_after])
        writer.writerow(['Posisjoner temperaturmålinger etter test', st.session_state.depth_array_after])
        writer.writerow(['Temperaturmålinger etter test', st.session_state.temp_array_after])

        writer.writerow(['Strømmåler før', st.session_state.power_before])
        writer.writerow(['Strømmåler etter', st.session_state.power_after])

        writer.writerow(['Kommentar', st.session_state.comment])


    ########## LAGRE TIL JSON-FIL #################################################################################################################################################################
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:jau0IMk5OKJWJ3Xl@cluster0.dlyj4y2.mongodb.net/")  # Assuming MongoDB is running locally

    db = client["TRT"]  # Replace "your_database_name" with your actual database name

    collection = db["TRT"]  # Replace "your_collection_name" with your actual collection name
    
    # Define your JSON document
    
    filename_json = f"TRT_info_{st.session_state.project_name}.json"
    dict_for_json = {
        'Prosjektnavn': st.session_state.project_name,
        'Latitude': st.session_state.lat,
        'Longitude': st.session_state.long,
        'Kontaktperson': st.session_state.contact_person,
        'Kollektorlengde': st.session_state.collector_length,
        'Kollektortype': st.session_state.collector_type,
        'Kollektorvæske': st.session_state.collector_fluid,
        'Brønndiameter': st.session_state.well_diameter,
        'Foringsrørdiameter': st.session_state.casing_diameter,
        'Måledato temperaturprofil før test': str(st.session_state.date_before),
        'Grunnvannsnivå før test': st.session_state.ground_water_level_before,
        'Posisjoner temperaturmålinger før test': str(st.session_state.depth_array_before),
        'Temperaturmålinger før test': str(st.session_state.temp_array_before),
        'Måledato temperaturprofil etter test': str(st.session_state.date_after),
        'Grunnvannsnivå etter test': st.session_state.ground_water_level_after,
        'Posisjoner temperaturmålinger etter test': str(st.session_state.depth_array_after),
        'Temperaturmålinger etter test': str(st.session_state.temp_array_after),
        'Strømmåler før': st.session_state.power_before,
        'Strømmåler etter': st.session_state.power_after,
        'Kommentar': st.session_state.comment
    }
    
    with open(filename_json, "w") as outfile:
        json.dump(dict_for_json, outfile, default=str)

    # Insert the JSON document into the collection


    key_to_check = {"Prosjektnavn": dict_for_json["Prosjektnavn"]}
    # Check if a document with the specified key already exists
    existing_document = collection.find_one(key_to_check)
    # Insert the JSON document into the collection only if it doesn't already exist
    collection.update_one(key_to_check, {"$set": dict_for_json}, upsert=True)


    cursor = collection.find({})  # Find all documents in the collection# Iterate over the cursor to access each documentfor document in cursor:     print(document)
    for document in cursor:
        st.write(document)