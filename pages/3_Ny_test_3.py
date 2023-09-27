import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.info("Navn på gjeldende prosjekt fra database")

if st.button("Lagre utkast"):
    st.success("Takk! Utkastet er lagret", icon = "✅")

if st.button("Send inn ferdig utfylt skjema"):
    st.success("Takk! ditt skjema er innsendt", icon = "✅")

add_vertical_space(10)
c1, c2 = st.columns(2)
with c1:
    if st.button("Forrige"):
        switch_page("Ny_test_2")
with c2:
    if st.button("Gå tilbake til forside"):
        switch_page("Hjem")
