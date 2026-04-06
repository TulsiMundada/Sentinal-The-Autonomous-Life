import streamlit as st
from agents.orchestrator import run_full_cycle

st.set_page_config(page_title="Sentinal - Autonomous Life 🚀")

st.title("🧠 Sentinal - Autonomous Life")
st.markdown("### 🚫 Doomscrolling → 🎯 Productivity Converter")

# Input
goal = st.text_area("What are you doing / struggling with?")
time = st.text_input("Available Time", "2 hours")

if st.button("🚀 Run AI Agents"):

    if not goal:
        st.warning("⚠️ Please enter a goal first!")
    else:
        with st.spinner("🤖 Agents are thinking..."):

            try:
                result = run_full_cycle(goal, time)

                st.success("✅ Analysis Complete!")

                data = result.get("data", result)

                st.subheader("🎯 Goal")
                st.write(data.get("goal"))

                st.subheader("🧩 Plan")
                st.write(data.get("plan"))

                st.subheader("📅 Schedule")
                st.write(data.get("schedule"))

                st.subheader("⚡ Execution")
                st.write(data.get("execution"))

                st.subheader("🧠 Reflection")
                st.write(data.get("reflection"))

            except Exception as e:
                st.error(f"❌ Error: {e}")