import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="TRT", layout="centered", page_icon="src/data/img/AsplanViak_Favicon_32x32.png", initial_sidebar_state="collapsed")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none}</style>""", unsafe_allow_html=True) # ingen sidebar
    st.markdown("""<style>div[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True) # litt av sidebar
    st.markdown('''<style>button[title="View fullscreen"]{visibility: hidden;}</style>''', unsafe_allow_html=True) # hide fullscreen
    

def well_placement_input(text_string):
    if text_string == "Skriv inn adresse":
        st.info("def adressefunksjon()")
    elif text_string == "Skriv inn koordinater":
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input("NS", value = 63)
        with c2:
            long = st.number_input("ØV", value = 10)

project_name = st.text_input("Navn på prosjektet")
if project_name == "Bygdehaven":
    st.warning("Mente du det allerede eksisterende prosjektet Bygdehaven?")
    if st.button("Gå til eksisterende prosjekt"):
        switch_page("Eksisterende_test")
well_placement_input(selectbox("Plassering av brønn", ["Skriv inn adresse", "Skriv inn koordinater", "Plasser i kart"], no_selection_label="Velg"))
well_id = st.number_input("Brønn ID GRANADA", value = 70135532)
contact_person = st.text_input(f"Kontaktperson")
if len(contact_person) > 0:
    st.success("Registrert", icon = "✅")

add_vertical_space(10)
c1, c2 = st.columns(2)
with c1:
    if st.button("Forrige"):
        switch_page("Hjem")
with c2:
    if st.button("Neste"):
        switch_page("Ny_test_2")