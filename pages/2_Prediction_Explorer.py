import streamlit as st
import pandas as pd
import traceback
import altair as alt
# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("Prediction Explorer")
st.markdown("###### Explore Models forecasts and uncertainty")
st.caption(
    'Required columns: INIT_DATE_TIME, FCST_DATE_TIME, LZ, Models, Price'
)

uploaded = st.file_uploader("Upload CSV", type=["csv"])

# --------------------------------------------------
# Main App
# --------------------------------------------------
if uploaded:
    df = pd.read_csv(uploaded)

    # -------------------------------
    # Preview
    # -------------------------------
    st.subheader("Data Preview")
    st.dataframe(df.head(25))

    # -------------------------------
    # Tabs Layout
    # -------------------------------
    tab1, tab2, tab3, tab4= st.tabs([
        "Filter",
        "GroupBy",
        "Pivot",
        "Charts",
    ])

    # ===============================
    # TAB 1 — FILTERING
    # ===============================
    with tab1:
        st.subheader("Filter Data (Up to 3 Columns)")

        df_filtered = df.copy()

        # ------------------------------------------------
        # Helper to detect datetime-like columns
        # ------------------------------------------------
        def is_datetime_col(series):
            return (
                pd.api.types.is_datetime64_any_dtype(series) or
                ("date" in series.name.lower())
            )

        # ------------------------------------------------
        # Generic filter function
        # ------------------------------------------------
        def apply_filter(df_in, col, idx):
            series = df_in[col]

            # ---------- DATETIME ----------
            if (
                pd.api.types.is_datetime64_any_dtype(series) or
                "date" in col.lower()
            ):
                # Normalize datetime column
                series_dt = pd.to_datetime(series, errors="coerce")

                # Unique sorted values
                unique_dts = series_dt.dropna().sort_values().unique()

                if len(unique_dts) == 0:
                    return df_in  # nothing to filter

                sel = st.selectbox(
                    f"{col} value",
                    options=unique_dts,
                    index=0,
                    key=f"filter_dt_{idx}"
                )

                # Compare normalized datetime
                return df_in[pd.to_datetime(df_in[col], errors="coerce") == sel]

            # ---------- NUMERIC ----------
            elif pd.api.types.is_numeric_dtype(series):
                min_v, max_v = st.slider(
                    f"{col} range",
                    float(series.min()),
                    float(series.max()),
                    (float(series.min()), float(series.max())),
                    key=f"filter_num_{idx}"
                )
                return df_in[df_in[col].between(min_v, max_v)]

            # ---------- CATEGORICAL ----------
            else:
                vals = series.dropna().unique().tolist()

                if len(vals) == 0:
                    return df_in

                # Smart default
                if "model" in col.lower():
                    default = [vals[0]]
                else:
                    default = vals

                sel = st.multiselect(
                    f"{col} values",
                    options=vals,
                    default=default,
                    key=f"filter_cat_{idx}"
                )

                # 🔒 Never allow empty filter
                if not sel:
                    return df_in

                return df_in[df_in[col].isin(sel)]

        # ------------------------------------------------
        # FILTER 1 (required)
        # ------------------------------------------------
        col1 = st.selectbox(
            "Filter column 1",
            options=df.columns,
            key="filter_col_1"
        )
        df_filtered = apply_filter(df_filtered, col1, 1)

        # ------------------------------------------------
        # FILTER 2 (optional)
        # ------------------------------------------------
        if st.checkbox("➕ Add second filter", key="use_filter_2"):
            col2 = st.selectbox(
                "Filter column 2",
                options=[c for c in df.columns if c != col1],
                key="filter_col_2"
            )
            df_filtered = apply_filter(df_filtered, col2, 2)

        # ------------------------------------------------
        # FILTER 3 (optional)
        # ------------------------------------------------
        if st.checkbox("➕ Add third filter", key="use_filter_3"):
            used = {col1}
            if "filter_col_2" in st.session_state:
                used.add(st.session_state["filter_col_2"])

            col3 = st.selectbox(
                "Filter column 3",
                options=[c for c in df.columns if c not in used],
                key="filter_col_3"
            )
            df_filtered = apply_filter(df_filtered, col3, 3)

        # ------------------------------------------------
        # OUTPUT
        # ------------------------------------------------
        st.markdown(f"### Rows after filtering: **{len(df_filtered):,}**")
        st.dataframe(df_filtered)

        st.download_button(
            "⬇ Download filtered data",
            df_filtered.to_csv(index=False),
            file_name="filtered_data.csv",
            key="download_filtered"
        )
    # ===============================
    # TAB 2 — GROUPBY
    # ===============================
    with tab2:
        st.subheader("GroupBy Explorer")

        GROUPBY_COLS = ["LZ", "Models", "FCST_DATE_TIME"]

        group_cols = st.multiselect(
            "Group by columns",
            options=GROUPBY_COLS,
            default=GROUPBY_COLS,   # optional: preselect both
            key="groupby_cols"
        )

        num_cols = df.select_dtypes(include="number").columns.tolist()

        if num_cols:
            value_col = st.selectbox(
                "Value column",
                num_cols,
                key="value_col"
            )

            agg_func = st.selectbox(
                "Aggregation",
                ["mean", "sum", "median", "std", "min", "max", "count"],
                key="agg_func"
            )

            if group_cols:
                gb = (
                    df
                    .groupby(group_cols, dropna=False)[value_col]
                    .agg(agg_func)
                    .reset_index()
                )

                st.dataframe(gb, use_container_width=True)
        else:
            st.info("No numeric columns available.")

    # ===============================
    # TAB 3 — PIVOT TABLE
    # ===============================
    with tab3:
        st.subheader("Pivot Table Builder")

        rows = st.multiselect("Rows", df.columns)
        cols = st.multiselect("Columns", df.columns)
        num_cols = df.select_dtypes("number").columns

        if len(num_cols) > 0:
            values = st.selectbox("Values", num_cols)
            agg = st.selectbox("Aggregation", ["mean", "sum", "count", "std", "min", "max"], key="pivot_agg")

            if rows:
                pivot = pd.pivot_table(
                    df,
                    index=rows,
                    columns=cols if cols else None,
                    values=values,
                    aggfunc=agg
                )
                st.dataframe(pivot)
        else:
            st.info("No numeric columns available.")

    # ===============================
    # TAB 4 — CHARTS
    # ===============================
    with tab4:
        st.subheader("Charts")

        chart_type = st.selectbox(
            "Chart type",
            ["Line (Time Series)", "Bar", "Histogram"]
        )

        num_cols = df.select_dtypes("number").columns

        if chart_type == "Line (Time Series)":
            datatime_cols = ['FCST_DATE_TIME','INIT_DATE_TIME']
            date_col = st.selectbox("Datetime column", datatime_cols)
            value_col = st.selectbox("Value column", num_cols)

            agg_mode = st.selectbox(
                "Line aggregation",
                ["Average by LZ", "Average by models"]
            )

            df_ts = df.copy()

            # --- KEEP UTC (no conversion) ---
            df_ts[date_col] = pd.to_datetime(df_ts[date_col], utc=True, errors="coerce")
            df_ts = df_ts.dropna(subset=[date_col])

            # --- CREATE UTC STRING FOR SAFE HOVER ---
            df_ts["_dt_utc"] = df_ts[date_col].dt.strftime("%Y-%m-%d %H:%M UTC")
            
            # Sort by datetime to ensure proper line connection
            df_ts = df_ts.sort_values(date_col)

            if agg_mode == "Average by models":
                if "Models" not in df_ts.columns:
                    st.warning("Column 'Models' not found in dataframe")
                else:
                    plot_df = (
                        df_ts
                        .groupby([date_col, "_dt_utc", "Models"], as_index=False)[value_col]
                        .mean()
                        .sort_values(date_col)
                    )
                    chart = (
                        alt.Chart(plot_df)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X(
                                f"{date_col}:T",
                                title="Datetime (EST)",
                                axis=alt.Axis(
                                    format="%Y-%m-%d %H:%M",
                                    labelAngle=-45,
                                    labelOverlap=False
                                )
                            ),
                            y=alt.Y(value_col, title=value_col),
                            color=alt.Color("Models", legend=alt.Legend(title="Model")),
                            tooltip=[
                                alt.Tooltip("_dt_utc:N", title="Datetime (UTC)"),
                                alt.Tooltip("Models", title="Model"),
                                alt.Tooltip(value_col, title=value_col, format=".2f"),
                            ],
                        )
                    )

                    st.altair_chart(chart, use_container_width=True)

            elif agg_mode == "Average by LZ":
                if "LZ" not in df_ts.columns:
                    st.warning("Column 'LZ' not found in dataframe")
                else:
                    plot_df = (
                        df_ts
                        .groupby([date_col, "_dt_utc", "LZ"], as_index=False)[value_col]
                        .mean()
                        .sort_values(date_col)
                    )
                    chart = (
                        alt.Chart(plot_df)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X(
                                f"{date_col}:T",
                                title="Datetime (EST)",
                                axis=alt.Axis(
                                    format="%Y-%m-%d %H:%M",
                                    labelAngle=-45,
                                    labelOverlap=False
                                )
                            ),
                            y=alt.Y(value_col, title=value_col),
                            color=alt.Color("LZ", legend=alt.Legend(title="LZ")),
                            tooltip=[
                                alt.Tooltip("_dt_utc:N", title="Datetime (UTC)"),
                                alt.Tooltip("LZ", title="LZ"),
                                alt.Tooltip(value_col, title=value_col, format=".2f"),
                            ],
                        )
                    )

                    st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Bar":
            cat_col_val = ['LZ', 'Models']
            cat_col = st.selectbox("Category column", cat_col_val)
            value_col = st.selectbox("Value column", num_cols)

            agg_method = st.selectbox(
                "Bar aggregation",
                ["Mean", "Std", "Max", "Min"]
            )

            agg_map = {
                "Mean": "mean",
                "Std": "std",
                "Max": "max",
                "Min": "min"
            }
            agg_func = agg_map[agg_method]

            color_mode = st.selectbox(
                "Bar color mode",
                ["Color by category","Single color"]
            )

            bar_color = "#4C78A8"
            if color_mode == "Single color":
                bar_color = st.color_picker("Pick bar color", bar_color)

            bar_df = (
                df.groupby(cat_col)[value_col]
                .agg(agg_func)
                .reset_index()
                .sort_values(value_col, ascending=False)
            )

            tooltip_cols = [
                alt.Tooltip(cat_col, title=cat_col),
                alt.Tooltip(value_col, title=f"{agg_method} {value_col}")
            ]

            if color_mode == "Single color":
                chart = (
                    alt.Chart(bar_df)
                    .mark_bar(color=bar_color)
                    .encode(
                        x=alt.X(cat_col, sort='-y'),
                        y=value_col,
                        tooltip=tooltip_cols
                    )
                )
            else:
                chart = (
                    alt.Chart(bar_df)
                    .mark_bar()
                    .encode(
                        x=alt.X(cat_col, sort='-y'),
                        y=value_col,
                        color=alt.Color(cat_col, legend=None),
                        tooltip=tooltip_cols
                    )
                )

            st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Histogram":
            hist_col = st.selectbox("Column", num_cols)

            n_bins = st.slider("Number of bins", 5, 50, 20)

            # Create bins
            bins = pd.cut(df[hist_col], bins=n_bins)

            # Count
            hist_df = bins.value_counts().sort_index().reset_index()
            hist_df.columns = ["Bin", "Count"]

            # Convert Interval -> readable string
            hist_df["Bin_str"] = hist_df["Bin"].astype(str)
            
            # Extract midpoint for proper ordering
            hist_df["Bin_mid"] = hist_df["Bin"].apply(lambda x: x.mid)

            chart = (
                alt.Chart(hist_df)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Bin_str:N",
                        title=hist_col,
                        sort=alt.EncodingSortField(field="Bin_mid", order="ascending"),
                        axis=alt.Axis(labelAngle=45, labelOverlap=False)
                    ),
                    y=alt.Y("Count:Q", title="Count"),
                    tooltip=[
                        alt.Tooltip("Bin_str:N", title="Range"),
                        alt.Tooltip("Count:Q", title="Count")
                    ]
                )
                .properties(height=400)
            )

            st.altair_chart(chart, use_container_width=True)