import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Function to load ASC data ---
def load_asc_data(uploaded_file):
    lines = uploaded_file.read().decode("utf-8").splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#DATA"):
            start_idx = i + 1
            break

    data = []
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                wn = float(parts[0])   # Wavenumber
                tr = float(parts[1])   # Transmittance
                data.append((wn, tr))
            except ValueError:
                continue

    return pd.DataFrame(data, columns=["Wavenumber (cm-1)", "Transmittance (%)"])

# --- Streamlit UI ---
st.title("FTIR Analyser")

uploaded_files = st.file_uploader("Upload one or more ASC files", type=["asc"], accept_multiple_files=True)

# Sidebar customization
st.sidebar.header("Font Settings")
title_size = st.sidebar.number_input("Title Font Size", 10, 40, 20)
axis_title_size = st.sidebar.number_input("Axis Title Font Size", 10, 30, 16)
tick_size = st.sidebar.number_input("Axis Tick Font Size", 8, 25, 14)
font_family = st.sidebar.selectbox("Font Family", ["Arial", "Times New Roman", "Courier New", "Verdana"])

st.sidebar.header("Plot Settings")
show_grid = st.sidebar.checkbox("Show Gridlines", value=True)
line_thickness = st.sidebar.slider("Line Thickness", 1, 6, 2)

st.sidebar.header("Axis Range")
x_min = st.sidebar.number_input("X-axis Min (Wavenumber)", value=400.0)
x_max = st.sidebar.number_input("X-axis Max (Wavenumber)", value=4000.0)
y_min = st.sidebar.number_input("Y-axis Min", value=0.0)
y_max = st.sidebar.number_input("Y-axis Max", value=100.0)

# Plot mode
plot_mode = st.sidebar.radio("Plot Mode", ["Overlapped", "Stacked (Matplotlib style in Plotly)"])

# Stacked settings
offset_value = 0
sequence = []
color_map = {}
custom_names = {}

if plot_mode == "Stacked (Matplotlib style in Plotly)" and uploaded_files:
    st.sidebar.header("Stacked Plot Settings")
    offset_value = st.sidebar.number_input("Vertical Offset (a.u.)", value=5.0, step=1.0)
    sequence = st.sidebar.multiselect(
        "Select plotting sequence",
        options=[f.name for f in uploaded_files],
        default=[f.name for f in uploaded_files]
    )
    for file in uploaded_files:
        color_map[file.name] = st.sidebar.color_picker(f"Color for {file.name}", "#000000")
        custom_names[file.name] = st.sidebar.text_input(f"Custom name for {file.name}", value=file.name)

st.sidebar.markdown("---")
st.sidebar.markdown("**Developed by Kushagra, Petchem Lab**")

# --- Plotting ---
if uploaded_files:
    chart_title = st.text_input("Enter chart title", value="FTIR Spectrum")

    if plot_mode == "Overlapped":
        fig = go.Figure()
        for file in uploaded_files:
            default_name = file.name
            custom_name = st.text_input(f"Custom name for {default_name}", value=default_name)
            df = load_asc_data(file)
            fig.add_trace(go.Scatter(
                x=df["Wavenumber (cm-1)"],
                y=df["Transmittance (%)"],
                mode="lines",
                line=dict(width=line_thickness),
                name=custom_name
            ))

        y_label = "<b>Transmittance (%)</b>"
        show_y_ticks = True

    else:  # Stacked Plotly
        fig = go.Figure()
        for i, fname in enumerate(sequence):
            file = next(f for f in uploaded_files if f.name == fname)
            df = load_asc_data(file)
            y_offset = i * offset_value
            fig.add_trace(go.Scatter(
                x=df["Wavenumber (cm-1)"],
                y=df["Transmittance (%)"] + y_offset,
                mode="lines",
                line=dict(width=line_thickness, color=color_map[fname]),
                name=custom_names[fname]  # ✅ use custom name
            ))

        y_label = "<b>Transmittance (a.u.)</b>"
        show_y_ticks = False

    # Common layout
    fig.update_layout(
        title=dict(text=f"<b>{chart_title}</b>", font=dict(size=title_size, family=font_family, color="black")),
        xaxis=dict(
            title=dict(text="<b>Wavenumber (cm⁻¹)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
            autorange="reversed",
            range=[x_max, x_min],
            tickfont=dict(size=tick_size, family=font_family, color="black"),
            showgrid=show_grid
        ),
        yaxis=dict(
            title=dict(text=y_label, font=dict(size=axis_title_size, family=font_family, color="black")),
            autorange=False,
            range=[y_min, y_max + (offset_value * len(sequence) if plot_mode.startswith("Stacked") else 0)],
            tickfont=dict(size=tick_size, family=font_family, color="black"),
            showgrid=show_grid,
            showticklabels=show_y_ticks   # ✅ hides numeric ticks in stacked mode
        ),
        legend=dict(font=dict(size=tick_size, family=font_family, color="black"))
    )

    st.plotly_chart(fig, use_container_width=True)

    # ✅ Add download option for interactive HTML
    html_file = "ftir_plot.html"
    fig.write_html(html_file)
    with open(html_file, "rb") as f:
        st.download_button("Download Interactive HTML Plot", f, file_name=html_file, mime="text/html")
