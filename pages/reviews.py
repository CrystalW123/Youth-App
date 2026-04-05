import streamlit as st
from utils.storage import save_review
from utils.styles import apply_custom_styles

apply_custom_styles()

st.title("Leave a Review ⭐")
st.write("Tell us what you think about Youth Hub the reviews are anonymous.")

rating = st.slider("Rating", 1, 5, 5)
review_text = st.text_area("Your review")

if st.button("Submit Review"):
    if review_text.strip():
        save_review(rating, review_text.strip())
        st.success("Thank you for your feedback!")
    else:
        st.warning("Please write a review before submitting.")