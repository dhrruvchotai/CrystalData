import pandas as pd
import streamlit as st
from cleaning.preprocess import getNumberOfDuplicateRows
from cleaning.preprocess import getTableOfNumericalAndCategoricalColumnsInDataOrMsg
import plotly.express as px

#SHOW FIRST N ROWS OF DATA
def preprocessGetFirstNRowsOfDataAndMsg(df, msgToShow, numberOfRowsToShow,):
    st.subheader(msgToShow)
    st.dataframe(df.head(numberOfRowsToShow))

#GET MISSING VALUE TABLE
def preprocessGetMissingValTableOrMsg(data_variable,instance_type):
    if isinstance(data_variable, instance_type):
        st.subheader("Missing Values found in this columns: ",)
        st.table(data_variable)
    else:
        st.error("No Missing Values Found!")

#GET MISSING VALUE BAR CHART
def preprocessGetMissingValuesBarGraphIfExists(data_variable, instance_type):
    if isinstance(data_variable, instance_type):
        st.bar_chart(data=data_variable, x='Column Name', y = 'Missing Count')

#SHOW NUMBER OF DUPLICATE ROWS 
def preprocessGetDuplicateRowsCountMessageIfAny(df):
    total_duplicate_rows = getNumberOfDuplicateRows(df=df)
    if(total_duplicate_rows > 0):
        st.error(f"Number of duplicate rows found : {total_duplicate_rows}")
        return total_duplicate_rows
    else : 
        st.error("No Duplicate Rows Found!")
        return 0

#TABLE FOR NUMERICAL AND CATEGORICAL COLS
def preprocessGetTableForNumericAndCategoricalColumnsInDataOrMsg(df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=5):
    numerical_categorical_variable_count_table_or_msg = getTableOfNumericalAndCategoricalColumnsInDataOrMsg(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=min_unique_values_threshold_to_convert_from_numerical_to_categorical)
    if isinstance(numerical_categorical_variable_count_table_or_msg, pd.DataFrame):
        st.table(numerical_categorical_variable_count_table_or_msg)
    else:
        st.error(numerical_categorical_variable_count_table_or_msg)

#GRAPHS SECTION

#UNIVARIATE
def preprocessGetHistogramPlottingSectionForUnivariateNumericalCols(df, numerical_cols):
    if not numerical_cols:
        st.error("No Numerical Columns found to Plot!")
    else:
        col1,col2 = st.columns([2.5,2.5])
        with col1:
            x_col = st.selectbox("Numerical Columns", options=numerical_cols)
        with col2:
            norm_options = {
                "Count" : None,
                "Percent" : "percent",
                "Probability" : "probability",
                "Probability Density" : "probability density"
            }
            normalization_type = st.selectbox("Normalization Options", options=["Count", "Percent", "Probability","Probability Density"])

        plot_options = st.expander("Plot Options")
        with plot_options:
            show_mean_line = st.checkbox("Show Mean Line", value=False)
            show_median_line = st.checkbox('Show Median Line', value=False)
            show_annotation = st.checkbox("Show Annotation (For Mean/Median Lines)", value = False)
            nbins = st.slider("Number Of Bins", min_value=5, max_value=100, value=40)
        fig = px.histogram(df,x=x_col, histnorm = norm_options[normalization_type], nbins=nbins, title=f"Histogram : {x_col}")
        if show_mean_line:
            fig.add_vline(x=df[x_col].mean(),line_color = "red")
            #here y shows the position of the text on y axis (> 0 means above the plot and < 0 means below the plot)
            if show_annotation:
                fig.add_annotation(x=df[x_col].mean(), y = 30, text=f"<b>Mean : {round(df[x_col].mean(),2)}</b>", font=dict(color = "red", size = 15), showarrow=False)
        if show_median_line:
            fig.add_vline(x=df[x_col].median(), line_color = "blue")
            if show_annotation:
                fig.add_annotation(x=df[x_col].median(), y = 15  , text=f"<b>Median : {round(df[x_col].median(),2)}</b>", font=dict(color = "blue", size = 15), showarrow=False)
        st.plotly_chart(fig,use_container_width=True, key=f"Histogram : {x_col} vs {normalization_type}")

def preprocessGetBarChartPlottingSectionForUnivariateCategoricalCols(df, categorical_cols):
    if not categorical_cols:
        st.error("No Categorical columns found to plot!")
    if len(categorical_cols) == 0:
        st.error("No Categorical columns found to plot!")
    else:
        st.info("To keep the Bar Chart easy to read, we've included only columns with up to 5 unique categories.")
        categorical_cols_filtered = [col for col in categorical_cols if df[col].nunique() <= 5]
        #IF THERE IS NO COLUMN HAVING NUMBER OF UNIQUE CATEGORIES <= 5
        if len(categorical_cols_filtered) == 0:
            st.error("No Categorical Columns found having number of unique categories less than or equal 5.")
        #IF THERE IS ONLY 1 COLUMN HAVING NUMBER OF UNIQUE CATEGORIES <= 5
        #Then directly plot graph for it
        elif len(categorical_cols_filtered) == 1:
            x_col = categorical_cols_filtered[0]
            st.warning(f"There is only one Categorical Column ({x_col}) having number of unique categories less than or equal 5.")
            #if it has numerical values like (0 & 1) or (1,2,3) then this 2 lines below is useful
            #get count of each unique categories and make a col for it 
            #value counts gives a series of counts in each categories but we want df so by using reset index will convert series into df 
            #and make the old column(x_col) the index of df.
            counts_of_unique_categories_in_col = df[x_col].value_counts().reset_index()
            #renaming the columns in the df
            counts_of_unique_categories_in_col.columns = [x_col,'Count']
            fig = px.bar(
                        # df, #now instead of passing df apde counts_of_unique_categories_in_col name ni df pass karsu here
                        counts_of_unique_categories_in_col,
                        x=x_col,
                        y = 'Count',
                        title=f"Bar Chart : {x_col}"
                    )
            st.plotly_chart(fig,use_container_width=True, key=f"Bar Chart : {x_col} vs Count")
        #IF THERE IS MORE THAN 1 COLUMN HAVING NUMBER OF UNIQUE CATEGORIES <= 5
        else:
            col1,col2= st.columns([2.5,2.5])
            with col1:
                x_col = st.selectbox("Categorical Columns", options=categorical_cols_filtered)
            with col2:
                default_idx = 1 if len(categorical_cols) > 1 else 0
                color_col =  st.selectbox("Color by (optional)", categorical_cols_filtered, index=default_idx)
            if x_col:
                if x_col == color_col:
                    st.warning("X Column and Color Column cannot be the same! Please select a different Column.")
                else:
                    counts_of_unique_categories_in_col = df.groupby([x_col,color_col]).size().reset_index(name='Count')
                    #why reset index ma Count pass karyu kemke groupby thi ek new col banse each selected col and color col ma ketli values chhe ano count but e unnamed hase so apde ene name api didhu count
                    #what is size() and groupby su kam?
                    #kemke color_col thi apde groupby kariye chhe cause group by nay kariye to individual rows plot thase 
                    #now apde color col thi groupby karyu to apde size chhe a kese ke each selected col and color col ma ketli rows or objects ave chhe eno count apse
                    #apde aa uper lakheli line ni su kaam jarur paidi ?
                    #suppose ke titanic ma survived col ma 2 category chhe 0 and 1 
                    #too jooo apde m nem bar chart plot karsu to it will plot each individually so bar chart ma ghana badha bars banse and why?
                    #kemke bar chart ma survived apsu to ema values numeric chhe(0 and 1 also Pclass ma pan same vandho avse cause numeric values(1,2,3)) atle it will plot individual rows kemke given col has numeric values(though it is categorical col)
                    #but Sex column mate bar chart perfect avse kemke ama value is string or object atle ae automatic grouping kari lese and jetli categories chhe atla j bar banse
                    #soo apde size() thi each selected col and color col na group bani ne ema ketli rows or object ave chhe ano count malse
                    #soo have bar chart proper banse (jetli unique categories atla unique bars)
                    fig = px.bar(
                        # df, #now instead of passing df apde counts_of_unique_categories_in_col name ni df pass karsu here
                        counts_of_unique_categories_in_col,
                        x=x_col,
                        y = 'Count',
                        color=color_col,
                        title=f"Bar Chart : {x_col}"
                    )
                    st.plotly_chart(fig,use_container_width=True, key=f"Bar Chart : {x_col}-{color_col} vs Count")
        
#BIVARIATE & MULTIVARIATE
def preprocessGetScatterPlotPlottingSectionForBivariateAndMultivariateNumericalVsNumerical(df,numerical_cols,categorical_cols):
    if not numerical_cols:
        st.error("No Numerical columns found to plot!")
    else:
        st.info("To keep the Scatter Plot easy to read, we've included only columns with up to 5 unique categories in Color by column options.")
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            x_col = st.selectbox("X (numerical)", options=numerical_cols, index=0)
        with col2:
            #TO CHOOSE DIFFERENT INITIAL INDEX
            default_idx = 1 if len(numerical_cols) > 1 else 0
            y_col = st.selectbox("Y (numerical)", options=numerical_cols, index=default_idx)
        with col3:
            categorical_cols_filtered = [col for col in categorical_cols if df[col].nunique() <= 5]
            color_col = st.selectbox("Color by (optional)", options=[None] + categorical_cols_filtered, index=0)

        plot_options = st.expander("Plot options")
        with plot_options:
            show_trend_line = st.checkbox("Show regression trend line", value=False)
            log_x = st.checkbox("Log scale X", value=False)
            log_y = st.checkbox("Log scale Y", value=False)
            point_size = st.slider("Marker size", min_value=5, max_value=30, value=9)
            color_scale_scatter = st.selectbox("Color Scale (If selected Color by column)", options=["Blues", "Viridis", "Plasma","Inferno", "Magma", "Cividis", "Portland"])

        #IF SELECTED SAME COLS THEN SHOW MESSAGE
        if x_col == y_col:
            st.warning("X Column and Y Column cannot be the same! Please select a different Column.")
        else:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col if color_col else None,
                title=f"Scatter Plot : {x_col} vs {y_col}",
                hover_data=df.columns,
                color_continuous_scale=color_scale_scatter,
                trendline="ols" if show_trend_line else None,
                height=600,
            )

            if log_x:
                fig.update_xaxes(type="log")
            if log_y:
                fig.update_yaxes(type="log")

            fig.update_traces(marker=dict(size=point_size))
            st.plotly_chart(fig, use_container_width=True)

def preprocessGetHeatmapPlottingSectionForBivariateAndMultivariateCategoricalVsCategorical(df, categorical_cols):
    
    if not categorical_cols:
        st.error("No Categorical columns found to plot!")
    elif len(categorical_cols) <= 1:
        st.error("There are not enough Categorical Columns to Plot Heatmap!")
    else:
        st.info("To keep the Heatmap easy to read, we've included only columns with up to 5 unique categories.")
        categorical_cols_filtered = [col for col in categorical_cols if df[col].nunique() <= 5]
        if len(categorical_cols_filtered) <= 1:
            st.error("No Categorical Columns found having number of unique categories less than or equal 5.")
        else: 
            col1, col2,col3 = st.columns([2,2,1])
            with col1:
                x_col = st.selectbox("X (categorical)", options=categorical_cols_filtered, index = 0)
            with col2:
                default_idx = 1 if len(categorical_cols) > 1 else 0
                y_col = st.selectbox("Y (categorical)", options=categorical_cols_filtered, index=default_idx)
            with col3:
                color_scale_heatmap = st.selectbox("Color Scale", options=["Blues", "Viridis", "Plasma","Inferno", "Magma", "Cividis", "Portland"], key="Heat Map - Color Scale")
            
            plot_options = st.expander('Plot Options')
            with plot_options:
                show_colorbar = st.checkbox("Show Colorbar", value=True)
            if x_col == y_col:
                    st.warning("X and Y are the same column please choose different columns to see relation!")
            else:
                fig = px.density_heatmap(
                    df,
                    x=x_col,
                    y=y_col,
                    hover_data=df.columns,
                    color_continuous_scale=color_scale_heatmap,
                    title=f"Heatmap : {x_col} vs {y_col}",
                )
                fig.update_layout(
                    coloraxis_showscale = show_colorbar
                )
                st.plotly_chart(fig, use_container_width=True)


#Check Normal Distribution
def preprocessGetKdePlotForCheckingNormalDistribution(df,numerical_cols):
    pass


#Outlier Detection & Removal
def preprocessGetBoxplotPlottingSectionForOutlierDetection(df, numerical_cols):

    if len(numerical_cols) < 1:
        st.error("No Numerical Columns found to Plot Boxplot!")
        return df

    # Initialize session state for persistent df and outlier info
    if "cleaned_df" not in st.session_state:
        st.session_state.cleaned_df = df.copy()

    if "outlier_bounds" not in st.session_state:
        st.session_state.outlier_bounds = {}

    # Work with the cleaned_df instead of original
    df = st.session_state.cleaned_df

    # Column selection UI
    col1, col2 = st.columns([2.5, 2.5])
    with col1:
        y_col = st.selectbox(
            "Y (Numerical Columns)",
            options=numerical_cols,
            key="Boxplot_SelectBox_Numerical_Cols"
        )

    with col2:
        points_options = {
            "False": False,
            "All": "all",
            "Outliers": "outliers",
            "Suspected Outliers": "suspectedoutliers"
        }
        show_points = st.selectbox("Points", options=list(points_options.keys()))

    # Plot options expander
    plot_options = st.expander("Plot Options")
    with plot_options:
        is_notched = st.checkbox(
            "Show Notched Boxplot — hover to explore quartiles (Q1, Median, Q3).",
            value=False
        )

    # Draw boxplot
    fig = px.box(
        df,
        y=y_col,
        points=points_options[show_points],
        title=f"Boxplot of {y_col}",
        hover_data=df.columns,
        notched=is_notched,
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- ACTION BUTTONS ---
    col1, col2, col3,col4 = st.columns([0.8, 2.6, 1.8, 1.8])
    with col2:
        find_outliers_btn = st.button(f"Find Outliers in {y_col} Column")
    with col3:
        remove_outliers_btn = st.button("Remove Outliers")
    with col4:
        smooth_outliers_btn = st.button("Smooth Outliers")

    # --- FIND OUTLIERS ---
    if find_outliers_btn:
        Q1 = df[y_col].quantile(0.25)
        Q3 = df[y_col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        number_of_outliers = len(df) - len(df[(df[y_col] >= lower_bound) & (df[y_col] <= upper_bound)])

        st.session_state.outlier_bounds[y_col] = {
            "Q1": Q1,
            "Q3": Q3,
            "IQR": IQR,
            "lower": lower_bound,
            "upper": upper_bound,
            "count": number_of_outliers
        }

        st.warning(f"Found **{number_of_outliers}** outliers in **{y_col}** column!")

    # --- REMOVE OUTLIERS ---
    if remove_outliers_btn:
        if y_col in st.session_state.outlier_bounds:
            bounds = st.session_state.outlier_bounds[y_col]
            lower, upper = bounds["lower"], bounds["upper"]
            st.session_state.cleaned_df = df[(df[y_col] >= lower) & (df[y_col] <= upper)]
            st.info(f"Removed **{bounds['count']}** outliers from **{y_col}** column.")
            st.info(f"After removing outliers, data shape: **{st.session_state.cleaned_df.shape}**")
        else:
            st.warning("Please click **'Find Outliers'** first!")

    # --- SMOOTH OUTLIERS ---
    if smooth_outliers_btn:
        if y_col in st.session_state.outlier_bounds:
            bounds = st.session_state.outlier_bounds[y_col]
            lower, upper = bounds["lower"], bounds["upper"]

            # Smooth (cap) values instead of removing
            df_smoothed = df.copy()
            df_smoothed[y_col] = df_smoothed[y_col].apply(
                lambda x: lower if x < lower else upper if x > upper else x
            )

            st.session_state.cleaned_df = df_smoothed
            st.success(
                f"Smoothed (capped) outliers in **{y_col}** column "
                f"between **{lower:.2f}** and **{upper:.2f}**."
            )
            st.info(f"Data shape remains unchanged: **{st.session_state.cleaned_df.shape}**")
        else:
            st.warning("Please click **'Find Outliers'** first!")

    return st.session_state.cleaned_df
