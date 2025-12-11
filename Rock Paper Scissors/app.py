import streamlit as st
import random

st.title("🎮 Rock Paper Scissors Game")

options = ["rock", "paper", "scissor"]

# Initialize scores in session state
if "user_score" not in st.session_state:
    st.session_state.user_score = 0
if "computer_score" not in st.session_state:
    st.session_state.computer_score = 0

# Let user choose
userpick = st.selectbox("Pick your move:", options)
play_button = st.button("Play Round")

if play_button:
    computerpick = random.choice(options)
    st.write(f"🤖 Computer chose: **{computerpick}**")

    # Determine the winner
    if userpick == computerpick:
        st.info("It's a tie!")
    elif (
        (userpick == "rock" and computerpick == "scissor")
        or (userpick == "scissor" and computerpick == "paper")
        or (userpick == "paper" and computerpick == "rock")
    ):
        st.success("You won this round! 🎉")
        st.session_state.user_score += 1
    else:
        st.error("You lost this round. 😢")
        st.session_state.computer_score += 1

# Display current score
st.subheader("🏆 Scoreboard")
col1, col2 = st.columns(2)
col1.metric("You", st.session_state.user_score)
col2.metric("Computer", st.session_state.computer_score)

# Reset button
if st.button("Reset Game"):
    st.session_state.user_score = 0
    st.session_state.computer_score = 0
    st.success("Game reset!")
    st.rerun()

st.markdown("---")
