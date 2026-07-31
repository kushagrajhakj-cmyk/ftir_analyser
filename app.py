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
y_min = st.sidebar.number_input("Y-axis Min (Transmittance)", value=0.0)
y_max = st.sidebar.number_input("Y-axis Max (Transmittance)", value=100.0)

# Toggle for overlapped vs separate plots
plot_mode = st.sidebar.radio("Plot Mode", ["Overlapped", "Separate"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Developed by Kushagra, Petchem Lab**")

# --- Plotting ---
if uploaded_files:
    chart_title = st.text_input("Enter chart title", value="FTIR Spectrum")

    if plot_mode == "Overlapped":
        # Combined overlapped plot
        fig = go.Figure()
        for file in uploaded_files:
            default_name = file.name
            custom_name = st.text_input(f"Name for {default_name}", value=default_name)
            df = load_asc_data(file)
            fig.add_trace(go.Scatter(
                x=df["Wavenumber (cm-1)"],
                y=df["Transmittance (%)"],
                mode="lines",
                line=dict(width=line_thickness),
                name=custom_name
            ))

        fig.update_layout(
            title=dict(text=f"<b>{chart_title}</b>", font=dict(size=title_size, family=font_family, color="black")),
            xaxis=dict(
                title=dict(text="<b>Wavenumber (cm⁻¹)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                autorange="reversed",   # ✅ FTIR convention
                range=[x_max, x_min],   # ✅ invert range explicitly
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            yaxis=dict(
                title=dict(text="<b>Transmittance (%)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                autorange=False,
                range=[y_min, y_max],
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            legend=dict(font=dict(size=tick_size, family=font_family, color="black"))
        )

        st.plotly_chart(fig, use_container_width=True)

        html_file = "ftir_overlapped.html"
        fig.write_html(html_file)
        with open(html_file, "rb") as f:
            st.download_button("Download Interactive HTML", f, file_name=html_file, mime="text/html")

    else:
        # Separate plots for each file
        for file in uploaded_files:
            custom_name = st.text_input(f"Name for {file.name}", value=file.name)
            df = load_asc_data(file)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Wavenumber (cm-1)"],
                y=df["Transmittance (%)"],
                mode="lines",
                line=dict(width=line_thickness),
                name=custom_name
            ))

            fig.update_layout(
                title=dict(text=f"<b>{chart_title} - {custom_name}</b>", font=dict(size=title_size, family=font_family, color="black")),
                xaxis=dict(
                    title=dict(text="<b>Wavenumber (cm⁻¹)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                    autorange="reversed",   # ✅ FTIR convention
                    range=[x_max, x_min],
                    tickfont=dict(size=tick_size, family=font_family, color="black"),
                    showgrid=show_grid
                ),
                yaxis=dict(
                    title=dict(text="<b>Transmittance (%)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                    autorange=False,
                    range=[y_min, y_max],
                    tickfont=dict(size=tick_size, family=font_family, color="black"),
                    showgrid=show_grid
                ),
                legend=dict(font=dict(size=tick_size, family=font_family, color="black"))
            )

            st.plotly_chart(fig, use_container_width=True)

            html_file = f"ftir_{custom_name.replace(' ', '_')}.html"
            fig.write_html(html_file)
            with open(html_file, "rb") as f:
                st.download_button(f"Download {custom_name} HTML", f, file_name=html_file, mime="text/html")
