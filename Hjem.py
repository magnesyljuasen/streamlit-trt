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
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

with open('src/login/config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)
authenticator = stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('Innlogging', 'main')

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')
        
elif authentication_status == None:
    image = Image.open('src/data/img/av_logo.png')
    st.image(image, caption = "TRT")
#App start 
elif authentication_status:
    #-- 
    if st.button("Registrer ny termisk responstest"):
        switch_page("Ny_test_1")
    if st.button("Fortsett registrering av eksisterende termisk responstest"):
        switch_page("Eksisterende_test_1")
    if st.button("Se historiske tester"):
        switch_page("Historiske_tester")
    #--
    image = Image.open('src/data/img/AsplanViak_illustrasjoner-01.png')
    st.image(image)
    #add_vertical_space(10)
    c1, c2 = st.columns(2)
    with c1:
        authenticator.logout('Logg ut')
    with c2:
        if st.button("Kontakt oss"):
            switch_page("Kontakt_oss")
    
    

    #if st.button("Registrer ny termisk responstest"):
    #    switch_page("plotting")
    #if st.button("Fortsett registrering av eksisterende termisk responstest"):
    #    switch_page("plotting")


