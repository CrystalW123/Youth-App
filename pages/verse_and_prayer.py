import streamlit as st

st.title("Verse And Prayer")

st.write("This page will let you pick a topic and receive:")
st.write("Bible Verse")
st.write("Short Explanation")
st.write("Reflection question")

topic = st.selectbox("Choose a topic",
                     ["stress", "wisdom", "anxiety", "fear", "love", "work", "holiness"
                      "joy", "worship"])

st.write(f"You selected: **{topic}**")

st.button("Get Encouragement")