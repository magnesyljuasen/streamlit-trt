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
        st.write("")
        st.write("")
        with st.popover("Leie testrigg?", use_container_width=True):
           st.write(""" Vi leier ut vår testrigg for termisk responstest. """)
           
           st.write(""" Kontakt oss!""")
           if st.button("Kontakt oss", key = 'contactUS'):
               switch_page("Kontakt_oss")

        with st.popover('**Vi tilbyr rådgivning innen grunnvarmeprosjekter**', use_container_width=True):
            st.write(""" 
                Vi har solid kompetanse på både lukkede systemer med energibrønner i fjell, 
                åpne systemer med bruk av grunnvann som energikilde, og større energilager. 
            """)

            st.write("""  
                Vi tilbyr en rekke tjenester innen disse fagområdene, alt fra større utredninger 
                og utviklingsprosjekter til forundersøkelser og detaljprosjektering av energibrønnparker. 
            """)

            st.write(""" Vi kan bidra med: """)
            st.caption('Energibrønner i fjell')
            st.write(" - Analyse av termisk responstest")
            st.write(" - EED-beregninger og dimensjonering av brønnparker")
            st.write(" - Utarbeide situasjonsplan med plassering av brønner og samlekummer, samt trasé for varmebærerledning")
            st.write(" - Design og prosjektering av GeoTermoser/Varmelager")
            st.caption("Tidligfasevurderinger")
            st.write(" - Vurdere grunnforholdene og om det er nødvendig med geoteknisk prosjektering ved etablering av brønnpark tilknyttet grunnvarme ")
            st.write(" - Vurdere aktuelle grunnvarmeløsninger")
            st.write(" - Kostnadsestimering og nedbetalingstid")
            st.caption("Energi fra grunnvann")
            st.write(" - Hydrogeologiske forundersøkelser")
            st.write(" - Dimensjonering av produksjons- og infiltrasjonsbrønner (tur-/retur), oppfølging ved boring og testing av nye brønner")
            st.write(" - Rådgivning for instrumentering og oppfølging under drift")
            st.write(" - Tilstandsvurdering og bistand ved vedlikehold av eksisterende brønner")

            st.write(""" Asplan Viak har også solid kompetanse innenfor VVS 
                     og Energirådgivning og kan bistå i alle faser av et prosjekt fra 
                     innledende vurderinger til oppfølging under drift.""")
            
            if st.button("Kontakt oss", key = "Kontaktoss"):
                switch_page("Kontakt_oss")
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


