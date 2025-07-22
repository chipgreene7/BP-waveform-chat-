import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# --- Streamlit Setup ---
st.set_page_config(page_title="ICU Arterial Waveform", layout="wide")
st.title("🩺 ICU Arterial Line Waveform Monitor")

# --- Sidebar Inputs ---
st.sidebar.header("🧠 Patient Parameters")
sbp = st.sidebar.slider("Systolic BP (mmHg)", 20, 200, 120)
dbp = st.sidebar.slider("Diastolic BP (mmHg)", 10, 120, 80)

# Enforce DBP < SBP
if dbp >= sbp:
    st.sidebar.warning("⚠️ Diastolic must be less than systolic.")

hr = st.sidebar.slider("Heart Rate (bpm)", 40, 140, 75)
map_val = int(round((sbp + 2 * dbp) / 3))
st.sidebar.markdown(f"**MAP:** {map_val} mmHg")

# --- Constants ---
fs = 100  # sample rate in Hz
window_sec = 5  # seconds of display
samples = window_sec * fs

# --- Waveform Generator ---
def generate_physiologic_waveform(t, sbp, dbp, hr):
    pressure = np.zeros_like(t)
    period = 60 / hr
    amp = sbp - dbp

    for beat_start in np.arange(0, t[-1], period):
        beat_t = t - beat_start
        in_beat = (beat_t >= 0) & (beat_t < period)

        x = beat_t[in_beat] / period  # normalized 0–1

        # Realistic arterial waveform
        shape = (
            0.6 * np.exp(-100 * (x - 0.15) ** 2) +   # systolic upstroke
            0.15 * np.exp(-300 * (x - 0.4) ** 2) -   # subtle dicrotic notch
            0.03 * np.sin(6 * np.pi * x) * (x < 0.8) # soft oscillation
        )

        shape = np.clip(shape, 0, None)
        if shape.size > 0 and np.max(shape) > 0:
            shape /= np.max(shape)

        pressure[in_beat] = dbp + amp * shape

    return pressure

# --- Live Plot ---
plot_placeholder = st.empty()

if st.button("🟢 Start Monitor"):
    st.toast("Starting real-time waveform...", icon="🫀")
    frame_count = 0
    while True:
        t = np.linspace(frame_count / fs, frame_count / fs + window_sec, samples)
        waveform = generate_physiologic_waveform(t, sbp, dbp, hr)

        fig, ax = plt.subplots(facecolor='black')
        ax.plot(t, waveform, color='red', linewidth=2)
        ax.set_facecolor("black")
        ax.set_xlabel("Time (s)", color='white')
        ax.set_ylabel("Pressure (mmHg)", color='white')
        ax.tick_params(colors='white')
        ax.set_title("Arterial Line", color='white')
        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(0, max(200, sbp + 20))
        ax.grid(False)

        # Annotate BP
        bp_text = f"{sbp}/{dbp} ({map_val})"
        ax.text(
            0.98, 0.95, bp_text,
            transform=ax.transAxes,
            fontsize=24,
            color='red',
            ha='right',
            va='top',
            fontweight='bold',
            family='monospace',
            bbox=dict(facecolor='black', edgecolor='red', boxstyle='round,pad=0.3')
        )

        plot_placeholder.pyplot(fig)
        frame_count += 10
        time.sleep(0.1)
