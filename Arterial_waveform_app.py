def generate_physiologic_waveform(t, sbp, dbp, hr=75):
    # Convert HR to period
    period = 60 / hr
    pressure = np.zeros_like(t)

    for beat_start in np.arange(0, t[-1], period):
        beat_t = t - beat_start
        in_beat = (beat_t >= 0) & (beat_t < period)
        beat_wave = (
            sbp
            - (sbp - dbp) * np.exp(-10 * beat_t[in_beat]) * (1 - np.cos(2 * np.pi * beat_t[in_beat] / period))
        )
        # Add a dicrotic notch (approximate timing ~0.35 of beat duration)
        if len(beat_wave) > 0:
            notch_idx = int(0.35 * len(beat_wave))
            beat_wave[notch_idx] -= 5  # small dip for notch
        pressure[in_beat] = beat_wave
    return pressure
