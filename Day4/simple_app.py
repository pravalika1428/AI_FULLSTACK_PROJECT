import streamlit as st
st.title("welcome to my first app")
st.write("hellooo")
name = st.text_input("enter your name...")
if st.button("Submit"):
    st.write("helloo",name)
  


