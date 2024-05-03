import streamlit_authenticator as stauth

# Asplan Viak : GRUNNVARME123
# Båsum : 3933rrtqsygq
# Seabrokers : vs7iew1n5fl3
# Nordenfjelske : n7z92oeke8kx
# Vestnorsk : zw7us0zn0c44
hashed_passwords = stauth.Hasher(['GRUNNVARME123', '3933rrtqsygq', 'vs7iew1n5fl3', 'n7z92oeke8kx', 'zw7us0zn0c44']).generate()
print(hashed_passwords)

    