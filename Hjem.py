import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from src.scripts import streamlit_settings, login

def frontpage(name, authentication_status, username, authenticator):
    # ugyldig passord
    if authentication_status == False:
        st.error('Ugyldig brukernavn/passord')
        st.stop()
    # ingen input
    elif authentication_status == None:
        st.image(Image.open('src/data/img/av_logo.png'), caption = "TRT")
        st.stop()
    # app start
    elif authentication_status:
        #-- 
        if st.button("Registrer termisk responstest"):
            switch_page("Ny_test_1")
        if st.button("Se historiske tester"):
            switch_page("Historiske_tester")
        #if st.button("Leie testrigg?"):
        #    switch_page("Historiske_tester")
        #--
        st.image(Image.open('src/data/img/AsplanViak_illustrasjoner-01.png'))
        c1, c2 = st.columns(2)
        with c1:
            authenticator.logout('Logg ut')
        with c2:
            if st.button("Kontakt oss"):
                switch_page("Kontakt_oss")

streamlit_settings()
name, authentication_status, username, authenticator = login()
frontpage(name, authentication_status, username, authenticator)

st.session_state.name = name


