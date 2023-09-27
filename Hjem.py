import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox


st.set_page_config(page_title="AV Grunnvarme", layout="centered", page_icon="src/data/img/AsplanViak_Favicon_32x32.png", initial_sidebar_state = "collapsed")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

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
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
        if st.button("Kontakt oss"):
            switch_page("Kontakt_oss")
    #-- 
    if st.button("Registrer ny termisk responstest"):
        switch_page("Ny_test_1")
    if st.button("Fortsett registrering av eksisterende termisk responstest"):
        switch_page("Eksisterende_test_1")
    if st.button("Se historiske tester"):
        switch_page("Historiske_tester")
    

    #if st.button("Registrer ny termisk responstest"):
    #    switch_page("plotting")
    #if st.button("Fortsett registrering av eksisterende termisk responstest"):
    #    switch_page("plotting")


