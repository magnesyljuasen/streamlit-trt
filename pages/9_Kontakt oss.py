import streamlit as st

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.title("Kontakt oss")

st.write("Magne Syljuåsen")
st.write(f"Mobil: 451 92 540")

st.write("Sofie Hartvigsen")
st.write(f"Mobil: 948 38 786")

st.write("Johanne Strålberg")
st.write(f"Mobil: 948 47 316")

st.write("Henrik Holmberg")
st.write(f"Mobil: 957 49 363")

st.write("Randi Kalskin Ramstad")
st.write(f"Mobil: 975 13 942")

st.info("Rapporter problem (her kommer det et skjema)")


