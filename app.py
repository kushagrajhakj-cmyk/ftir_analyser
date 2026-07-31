import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Function to load ASC data ---
def load_asc_data(uploaded_file):
    lines = uploaded_file.read().decode("utf-8").splitlines()

    # Find where #DATA starts
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#DATA"):
            start_idx = i + 1
            break

    # Extract data lines after #DATA
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

    df = pd.DataFrame(data, columns=["Wavenumber (cm-1)", "Transmittance (%)"])
    return df

# --- Streamlit UI ---
st.title("FTIR Spectrum Dashboard")

uploaded_files = st.file_uploader("Upload one or more ASC files", type=["asc"], accept_multiple_files=True)

# Font customization
st.sidebar.header("Font Settings")
title_size = st.sidebar.number_input("Title Font Size", min_value=10, max_value=40, value=20)
axis_title_size = st.sidebar.number_input("Axis Title Font Size", min_value=10, max_value=30, value=16)
tick_size = st.sidebar.number_input("Axis Tick Font Size", min_value=8, max_value=25, value=14)
font_family = st.sidebar.selectbox("Font Family", ["Arial", "Times New Roman", "Courier New", "Verdana"])

# Grid and line settings
st.sidebar.header("Plot Settings")
show_grid = st.sidebar.checkbox("Show Gridlines", value=True)
line_thickness = st.sidebar.slider("Line Thickness", min_value=1, max_value=6, value=2)

if uploaded_files:
    # --- Single file case ---
    if len(uploaded_files) == 1:
        df = load_asc_data(uploaded_files[0])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Wavenumber (cm-1)"],
            y=df["Transmittance (%)"],
            mode="lines",
            line=dict(width=line_thickness),
            name=uploaded_files[0].name
        ))

        fig.update_layout(
            title=dict(text=f"<b>FTIR Spectrum ({uploaded_files[0].name})</b>", font=dict(size=title_size, family=font_family, color="black")),
            xaxis=dict(
                title=dict(text="<b>Wavenumber (cm⁻¹)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                autorange="reversed",
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            yaxis=dict(
                title=dict(text="<b>Transmittance (%)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            legend=dict(font=dict(size=tick_size, family=font_family, color="black"))
        )

        st.plotly_chart(fig, use_container_width=True)

        # Save as HTML
        html_file = "ftir_single.html"
        fig.write_html(html_file)
        with open(html_file, "rb") as f:
            st.download_button("Download Interactive HTML", f, file_name=html_file, mime="text/html")

    # --- Multiple file case (overlapped plot) ---
    else:
        combined_fig = go.Figure()
        for file in uploaded_files:
            df = load_asc_data(file)
            combined_fig.add_trace(go.Scatter(
                x=df["Wavenumber (cm-1)"],
                y=df["Transmittance (%)"],
                mode="lines",
                line=dict(width=line_thickness),
                name=file.name
            ))

        combined_fig.update_layout(
            title=dict(text="<b>FTIR Spectra (Overlapped)</b>", font=dict(size=title_size, family=font_family, color="black")),
            xaxis=dict(
                title=dict(text="<b>Wavenumber (cm⁻¹)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                autorange="reversed",
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            yaxis=dict(
                title=dict(text="<b>Transmittance (%)</b>", font=dict(size=axis_title_size, family=font_family, color="black")),
                tickfont=dict(size=tick_size, family=font_family, color="black"),
                showgrid=show_grid
            ),
            legend=dict(font=dict(size=tick_size, family=font_family, color="black"))
        )

        st.plotly_chart(combined_fig, use_container_width=True)

        # Save as HTML
        html_file = "ftir_combined.html"
        combined_fig.write_html(html_file)
        with open(html_file, "rb") as f:
            st.download_button("Download Interactive HTML", f, file_name=html_file, mime="text/html")
