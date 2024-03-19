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

st.set_page_config(page_title="TRT", layout="centered", page_icon="src/data/img/AsplanViak_Favicon_32x32.png", initial_sidebar_state="collapsed")

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
client = pymongo.MongoClient("mongodb+srv://magnesyljuasen:jau0IMk5OKJWJ3Xl@cluster0.dlyj4y2.mongodb.net/")
db = client["TRT"]
collection = db["TRT"]
cursor = collection.find({})

project_name_list = []
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

for document in cursor:
    #if document['Firma'] == access_token:                  ##### For at denne ikke skal gi feilmelding, må du slette alle prosjektene i databasen som mangler 'Firma'-nøkkelen ;-)
    if 'hage' in document['Prosjektnavn']:                  ### Midlertidig test
        #st.write(document['Prosjektnavn'])
        project_name_list.append(document['Prosjektnavn'])
        #address_list.append(document['Adresse'])               ##### For at denne ikke skal gi feilmelding, må du slette alle prosjektene i databasen som mangler 'Adresse'-nøkkelen ;-)
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
        
dict_for_df = {'Prosjektnavn': project_name_list, 
               'Breddegrad': lat_list, 
               'Lengdegrad': long_list} 
                # osv ...
    
df = pd.DataFrame(dict_for_df)
st.write(df)
##################################################################################################

map_obj = Map()
map_obj.lat = 60
map_obj.long = 11
map_obj.name = "Test"
map_obj.create_wms_map()
returned_objects = map_obj.show_map()

st.write(returned_objects)

st.markdown("---")
#add_vertical_space(5)
if st.button("Gå tilbake til forside"):
    switch_page("Hjem")


