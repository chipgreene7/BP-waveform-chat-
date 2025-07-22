import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# --- Streamlit Setup ---
st.set_page_config(page_title="ICU Arterial Waveform", layout="wide")
st.title("🩺 ICU Arterial Line Waveform Monitor")

# --- Sidebar Inputs ---
st.sidebar.header("🧠 Patient Parameters")
sbp = st.sidebar.slider("Systolic BP (mmHg)", 80, 200, 120)
dbp = st.sidebar.slider("Diastolic BP (mmHg)", 40, 120, 80)
hr = st.sidebar.slider("Heart Rate (bpm)", 40, 140, 75)
map_val = round((sbp + 2 * dbp) / 3, 1)
st.sidebar.markdown(f"**MAP:** `{map_val}` mmHg")

# --- Constants ---
fs = 100  # 100 Hz sample rate
window_sec = 5  # 5-second scrolling window
samples = window_sec * fs
t = np.linspace(0, window_sec, samples)

# --- Physiologic Arterial Waveform Function ---
def generate_waveform(t, sbp, dbp, hr):
    pressure = np.zeros_like(t)
    period = 60 / hr

    for beat_start in np.arange(0, t[-1], period):
        beat_t = t - beat_start
        in_beat = (beat_t >= 0) & (beat_t < period)
        # Arterial waveform shape: fast rise, dicrotic notch, slow fall
        shape = (
            sbp
            - (sbp - dbp) * np.exp(-6 * beat_t[in_beat]) * (1 - np.cos(2 * np.pi * beat_t[in_beat] / period))
        )
        # Dicrotic notch at ~35% of systole
        if len(shape) > 0:
            notch_idx = int(0.35 * len(shape))
            if 0 <= notch_idx < len(shape):
                shape[notch_idx] -= 4  # Dip for dicrotic notch
        pressure[in_beat] = shape
    return pressure

# --- Live Plotting ---
plot_placeholder = st.empty()

if st.button("🟢 Start Monitor"):
    st.toast("Starting real-time arterial waveform...", icon="🫀")
    frame_count = 0
    while True:
        # Update X and Y
        t = np.linspace(frame_count / fs, frame_count / fs + window_sec, samples)
        waveform = generate_waveform(t, sbp, dbp, hr)

        # Plotting
        fig, ax = plt.subplots()
        ax.plot(t, waveform, color='crimson', linewidth=2)
        ax.set_ylim(40, 200)
        ax.set_xlim(t[0], t[-1])
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (mmHg)")
        ax.set_title("Real-Time Arterial Blood Pressure")
        ax.grid(True)
        plot_placeholder.pyplot(fig)

        frame_count += 10  # scroll forward
        time.sleep(0.1)
