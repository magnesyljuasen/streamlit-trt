import streamlit as st
import pandas as pd
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="TRT", layout="centered", page_icon="src/data/img/AsplanViak_Favicon_32x32.png", initial_sidebar_state="collapsed")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none}</style>""", unsafe_allow_html=True) # ingen sidebar
    st.markdown("""<style>div[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True) # litt av sidebar
    st.markdown('''<style>button[title="View fullscreen"]{visibility: hidden;}</style>''', unsafe_allow_html=True) # hide fullscreen

st.info("Navn på gjeldende prosjekt fra database")

with st.expander("Brønn og kollektor"):
    with st.form("Brønn og kollektor"):
        collector_type = selectbox("Kollektortype", ["Enkel-U", "Dobbel-U"], no_selection_label="Velg", key = "bk1")
        collector_fluid = selectbox("Kollektorvæske", ["HX24", "HX35"], no_selection_label="Velg", key = "bk2")
        collector_fluid = selectbox("Lengde kollektor", ["300 m", "250 m"], no_selection_label="Velg", key = "bk3")
        casing_diameter = selectbox("Diameter foringsrør", ["139 mm"], no_selection_label="Velg", key = "bk4")
        well_diameter = selectbox("Kollektorvæske", ["HX24", "HX35"], no_selection_label="Velg", key = "bk5")
        st.form_submit_button("Send inn")

with st.expander("Temperaturprofil før"):
    df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
    )
    edited_df = st.data_editor(
        df,
        column_config={
            "command": "Streamlit Command",
            "rating": st.column_config.NumberColumn(
                "Your rating",
                help="How much do you like this command (1-5)?",
                min_value=1,
                max_value=5,
                step=1,
                format="%d ⭐",
            ),
            "is_widget": "Widget ?",
        },
        disabled=["command", "is_widget"],
        hide_index=True,
    )
    with st.form("Temperaturprofil før"):
        st.info("Input")
        st.form_submit_button("Send inn")

with st.expander("Temperaturprofil etter"):
    with st.form("Temperaturprofil etter"):
        st.info("Input")
        st.form_submit_button("Send inn")

comment = st.text_area("Eventuelle kommentarer")

add_vertical_space(5)
c1, c2 = st.columns(2)
with c1:
    if st.button("Forrige"):
        switch_page("Ny_test_1")
with c2:
    if st.button("Neste"):
        switch_page("Ny_test_3")


