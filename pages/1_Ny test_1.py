import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
import numpy as np
import base64
import plotly.express as px
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
from src.scripts import streamlit_settings, switch_pages, toggle_closed_expander

def well_placement_input(text_string):
    if text_string == "Skriv inn adresse":
        st.info("def adressefunksjon()")
    elif text_string == "Skriv inn koordinater":
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input("NS", value = 63)
        with c2:
            long = st.number_input("ØV", value = 10)
            
def temperature_plot(df, color):
    fig = px.line(y=df["Dybde"], x=df["Temperatur"])
    fig.update_traces(line_color=color)
    fig.update_xaxes(title_text='Temperatur [°C"]', side='top')
    fig.update_yaxes(title_text='Dybde [m]', autorange='reversed')
    st.plotly_chart(fig, config={'staticPlot': True}, use_container_width=True)

streamlit_settings()

#st session state
if 'project_name' not in st.session_state:
    st.session_state.project_name = None
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'long' not in st.session_state:
    st.session_state.long = None


if "project_info_expanded" not in st.session_state:
    st.session_state.project_info_expanded = True
if "project_info_check" not in st.session_state:
    st.session_state.project_info_check = False
if st.session_state.project_info_check == True:
    project_info_check = "✅"
else:
    project_info_check = "✗"
    
with st.expander(f"{project_info_check} Informasjon om prosjektet", expanded=st.session_state.project_info_expanded):
    project_name = st.text_input("Navn på prosjektet")
    if len(project_name) > 0:
        st.session_state.project_name = project_name
        
    well_placement_input(selectbox("Plassering av brønn", ["Skriv inn adresse", "Skriv inn koordinater", "Plasser i kart"], no_selection_label="Velg"))
    contact_person = st.text_input(f"Kontaktperson")

    if (len(project_name) > 0) and len(contact_person) > 0:
        if st.button("Registrer", on_click=toggle_closed_expander("project_info_expanded", "project_info_check"), key = "project"):
            st.rerun()

if "technical_info_expanded" not in st.session_state:
    st.session_state.technical_info_expanded = False
if "technical_info_check" not in st.session_state:
    st.session_state.technical_info_check = False
if st.session_state.technical_info_check == True:
    technical_info_check = "✅"
else:
    technical_info_check = "✗"

with st.expander(f"{technical_info_check} Brønn og kollektor", expanded=st.session_state.technical_info_expanded):
    collector_length = st.number_input("Kollektorlengde [m]", min_value = None, step = 10)
    collector_type = selectbox("Kollektortype", ["Egendefinert", "Enkel-U", "Dobbel-U"], no_selection_label="Velg", key = "bk1")
    if collector_type == "Egendefinert":
        collector_type = st.text_input("Skriv inn kollektortype")
        st.markdown("---")
    collector_fluid = selectbox("Kollektorvæske", ["Egendefinert", "HX24", "HX35", "Kilfrost Geo 24%", "Kilfrost Geo 30%", "Kilfrost Geo 35%"], no_selection_label="Velg", key = "bk2")
    if collector_fluid == "Egendefinert":
        collector_fluid = st.text_input("Skriv inn kollektorvæske")
        st.markdown("---")
    casing_diameter = selectbox("Diameter foringsrør", ["Egendefinert", "139 mm"], no_selection_label="Velg", key = "bk4")
    if casing_diameter == "Egendefinert":
        casing_diameter = st.text_input("Skriv inn diameter på foringsrør")
        st.markdown("---")
    if collector_type != None and collector_fluid != None and collector_length != None and casing_diameter != None:
        st.button("Registrer", on_click=toggle_closed_expander("technical_info_expanded", "technical_info_check"), key = "technical")

if "temperature_before_expanded" not in st.session_state:
    st.session_state.temperature_before_expanded = False
if "temperature_before_check" not in st.session_state:
    st.session_state.temperature_before_check = False
if st.session_state.temperature_before_check == True:
    temperature_before_check = "✅"
else:
    temperature_before_check = "✗"  

with st.expander(f"{temperature_before_check} Temperaturprofil før", expanded=st.session_state.temperature_before_expanded):
    date = st.date_input("Måledato (før test)", value = "today")
    ground_water_level = st.number_input("Grunnvansnivå før test [m]", value = 0, step = 5)
    if collector_length < 150:
        STEP = 5
    else:
        STEP = 10
    depth_array = np.arange(0, collector_length + STEP, STEP)
    temperature_array = np.arange(0, collector_length + STEP, STEP)
    temperature_array = np.full(len(temperature_array), None)
    df = pd.DataFrame({
        "Dybde" : depth_array,
        "Temperatur" : temperature_array
    }
    )
    edited_df_before = st.data_editor(
        df, 
        hide_index = True, 
        use_container_width=True,
        column_config={
            "Temperatur": st.column_config.NumberColumn("Temperatur", format="%.1f °C"),
            "Dybde": st.column_config.NumberColumn("Dybde", format="%f m", )
            },
        key = "temperature_before_df"
        )
    #temperature_plot(df = edited_df_before, color = "green")
    if edited_df_before["Temperatur"].isna().sum() == 0:
        st.button("Registrer", on_click=toggle_closed_expander("temperature_before_expanded", "temperature_before_check"), key = "temperature_before")

if "temperature_after_expanded" not in st.session_state:
    st.session_state.temperature_after_expanded = False
if "temperature_after_check" not in st.session_state:
    st.session_state.temperature_after_check = False
if st.session_state.temperature_after_check == True:
    temperature_after_check = "✅"
else:
    temperature_after_check = "✗"  

with st.expander(f"{temperature_after_check} Temperaturprofil etter", expanded=st.session_state.temperature_after_expanded):
    date = st.date_input("Måledato (etter test)", value = "today")
    ground_water_level = st.number_input("Grunnvansnivå etter test[m]", value = 0, step = 5)
    if collector_length < 150:
        STEP = 5
    else:
        STEP = 10
    depth_array = np.arange(0, collector_length + STEP, STEP)
    temperature_array = np.arange(0, collector_length + STEP, STEP)
    temperature_array = np.full(len(temperature_array), None)
    df = pd.DataFrame({
        "Dybde" : depth_array,
        "Temperatur" : temperature_array
    }
    )
    edited_df_after = st.data_editor(
        df, 
        hide_index = True, 
        use_container_width=True,
        column_config={
            "Temperatur": st.column_config.NumberColumn("Temperatur", format="%.1f °C"),
            "Dybde": st.column_config.NumberColumn("Dybde", format="%d m")
            },
        key = "temperature_after_df"
        )
    #temperature_plot(df = edited_df_after, color = "red")
    if edited_df_after["Temperatur"].isna().sum() == 0:
        st.button("Registrer", on_click=toggle_closed_expander("temperature_after_expanded", "temperature_after_check"), key = "temperature_after")


comment = st.text_area("Eventuelle kommentarer")
uploaded_files = st.file_uploader("Last opp eventuelle vedlegg (bilder, testdata, andre filer)", accept_multiple_files=True)

switch_pages(previous_page_destination="Hjem", previous_page_text="Forrige", next_page_destination="Neste", next_page_text = "Ny_test_2")