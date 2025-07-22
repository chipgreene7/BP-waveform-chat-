import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime
from io import BytesIO

# Title
st.set_page_config(page_title="Arterial Waveform Simulator", layout="wide")
st.title("🩺 Arterial Waveform Simulator")

# Sidebar input
st.sidebar.header("Patient Blood Pressure Input")
sbp = st.sidebar.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, value=120)
dbp = st.sidebar.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=80)
map_val = round((sbp + 2 * dbp) / 3, 1)
st.sidebar.markdown(f"**MAP:** {map_val} mmHg")

# Waveform generator (synthetic)
def generate_waveform(sbp, dbp, duration=1, sample_rate=100):
    t = np.linspace(0, duration, int(duration * sample_rate))
    pulse_pressure = sbp - dbp
    baseline = dbp
    waveform = (
        baseline +
        0.5 * pulse_pressure * np.sin(2 * np.pi * 1.2 * t) ** 3 +
        0.2 * pulse_pressure * np.sin(4 * np.pi * 1.2 * t)
    )
    return t, waveform

# Container for dynamic plot
plot_placeholder = st.empty()
download_placeholder = st.empty()

# Live waveform simulation
if st.button("Start Waveform Simulation"):
    st.toast("Simulating waveform every second...", icon="⏱️")
    for _ in range(10):  # Simulate for 10 seconds; increase as needed
        t, waveform = generate_waveform(sbp, dbp)
        fig, ax = plt.subplots()
        ax.plot(t, waveform, color='red', lw=2)
        ax.set_ylim(0, 200)
        ax.set_xlim(0, 1)
        ax.set_title("Arterial Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (mmHg)")
        ax.grid(True)

        # Display plot
        plot_placeholder.pyplot(fig)

        # Save image for download
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)

        # Allow download
        timestamp = datetime.now().strftime("%H%M%S")
        download_placeholder.download_button(
            label=f"Download Snapshot ({timestamp})",
            data=buf,
            file_name=f"arterial_waveform_{timestamp}.png",
            mime="image/png"
        )

        time.sleep(1)
