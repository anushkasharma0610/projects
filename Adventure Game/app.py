import streamlit as st

st.set_page_config(page_title="Whispering Woods", page_icon="🌲", layout="centered")

st.title("🌲 Whispering Woods: A Shape of Shadows 🌲")
st.markdown("Your choices decide whether you survive the mysterious forest...")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.scene = "start"
    st.session_state.choice = None
    st.session_state.done = False

def next_step():
    st.session_state.step += 1
    st.session_state.choice = None

def go_to(scene):
    st.session_state.scene = scene
    next_step()

def restart():
    st.session_state.step = 0
    st.session_state.scene = "start"
    st.session_state.choice = None
    st.session_state.done = False

# --- Step 0 ---
if st.session_state.step == 0:
    st.session_state.scene = "start"
    st.write("You stand at the edge of the forest. Two paths stretch ahead — one **left**, one **right**.")
    st.session_state.choice = st.radio("Choose your path:", ["Go Left 🌫️", "Go Right 🌒"])
    def step0_next():
        if st.session_state.choice == "Go Left 🌫️":
            go_to("left1")
        else:
            go_to("right1")
    st.button("Next ➡️", on_click=step0_next)

# --- Step 1 ---
elif st.session_state.step == 1:
    scene = st.session_state.scene

    if scene == "left1":
        st.write("You take the left path. The trees whisper your name. A flickering lantern glows ahead.")
        st.session_state.choice = st.radio("What do you do?", ["Approach the Lantern 🔦", "Ignore it 🌲"])
        def left1_next():
            if st.session_state.choice == "Approach the Lantern 🔦":
                go_to("lantern1")
            else:
                go_to("darkpath")
        st.button("Next ➡️", on_click=left1_next)

    elif scene == "right1":
        st.write("You take the right path. The air grows colder. You see a wooden cabin with smoke rising.")
        st.session_state.choice = st.radio("What do you do?", ["Enter the Cabin 🏚️", "Keep Walking 🌌"])
        def right1_next():
            if st.session_state.choice == "Enter the Cabin 🏚️":
                go_to("mirror1")
            else:
                go_to("circle1")
        st.button("Next ➡️", on_click=right1_next)

# --- Step 2 ---
elif st.session_state.step == 2:
    scene = st.session_state.scene

    if scene == "lantern1":
        st.write("An old traveler greets you in the dark. He asks for your **name**.")
        st.session_state.choice = st.radio("Do you respond?", ["Tell Him 🗣️", "Stay Silent 🤫"])
        def lantern1_next():
            if st.session_state.choice == "Tell Him 🗣️":
                go_to("fogend")
            else:
                go_to("lantern2")
        st.button("Next ➡️", on_click=lantern1_next)

    elif scene == "lantern2":
        st.write("The traveler fades, leaving the lantern behind.")
        st.session_state.choice = st.radio("What do you do?", ["Take the Lantern 💡", "Leave it 🕯️"])
        def lantern2_next():
            if st.session_state.choice == "Take the Lantern 💡":
                go_to("escape1")
            else:
                go_to("lost1")
        st.button("Next ➡️", on_click=lantern2_next)

    elif scene == "darkpath":
        st.write("You walk deeper into the forest. A soft sound of water flows nearby.")
        st.session_state.choice = st.radio("Do you follow it?", ["Follow the Sound 💧", "Avoid It 🌑"])
        def darkpath_next():
            if st.session_state.choice == "Follow the Sound 💧":
                go_to("river1")
            else:
                go_to("carvings1")
        st.button("Next ➡️", on_click=darkpath_next)

    elif scene == "mirror1":
        st.write("Inside, a dusty mirror stands in the corner.")
        st.session_state.choice = st.radio("What do you do?", ["Clean the Mirror 🪞", "Ignore It 🌙"])
        def mirror1_next():
            if st.session_state.choice == "Clean the Mirror 🪞":
                go_to("mirrortrap")
            else:
                go_to("birdend")
        st.button("Next ➡️", on_click=mirror1_next)

    elif scene == "circle1":
        st.write("You find an ancient stone circle glowing faintly.")
        st.session_state.choice = st.radio("Do you step in?", ["Step In 🔮", "Stay Out 🕯️"])
        def circle1_next():
            if st.session_state.choice == "Step In 🔮":
                go_to("aloneend")
            else:
                go_to("safeend")
        st.button("Next ➡️", on_click=circle1_next)

# --- Final Step ---
else:
    scene = st.session_state.scene

    endings = {
        "fogend": ("He repeats your name slowly... then smiles in the dark. His form melts into fog. 🌫️", "You’ve become one of them."),
        "escape1": ("The lantern lights your path! You follow it until dawn — you made it out! 🌄", ""),
        "lost1": ("You walk on without light. The mist grows thick — you wander endlessly... 🌫️", ""),
        "river1": ("Your reflection waves back differently. You vanish into the moonlight. 💧", ""),
        "carvings1": ("You find carvings of your name, but you run until dawn — and escape! 🌅", ""),
        "mirrortrap": ("Your reflection doesn’t move — it whispers, 'Your turn now.' You’re trapped in the mirror. 🪞", ""),
        "birdend": ("You rest and wake up to birdsong — the forest is gone. You survived! 🕊️", ""),
        "aloneend": ("Time freezes inside the stone circle. When it resumes, you’re alone... forever. 🌀", ""),
        "safeend": ("You stay out of the circle, follow a faint light — and find the forest edge! 🌄", "")
    }

    text, extra = endings.get(scene, ("The forest is quiet.", ""))
    if "🌫️" in text or "🪞" in text or "💧" in text or "🌀" in text:
        st.warning(text)
    else:
        st.success(text)
    if extra:
        st.write(extra)

    st.button("🔁 Play Again", on_click=restart)
