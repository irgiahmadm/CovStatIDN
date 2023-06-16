import pandas as pd
import streamlit as st
import altair as alt
import calendar


class PageState:
    def __init__(self):
        self.current_page = 'Main'


def sidebar():
    page_state = PageState()
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .sidebar .sidebar-list {
            color: #333;
            font-weight: bold;
        }
        .sidebar .sidebar-list:hover {
            background-color: #e9ecef;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.header('Menu')
    selected_page = st.sidebar.radio(
        'Go To', ('CovStatIDN', 'Monthly Cases', 'About'))

    page_state.current_page = selected_page

    # Define the content for each page
    df = pd.read_csv('./data_indonesia/covid_19_indonesia_time_series_all.csv')
    if page_state.current_page == 'CovStatIDN':
        main_menu(df)
    elif page_state.current_page == 'Monthly Cases':
        monthly_cases_page(df)
    elif page_state.current_page == 'About':
        about()


def about():
    st.title('About this project')
    st.markdown('')
    st.markdown('''
        #### CovStatIDN
        Project ini dibuat untuk memenuhi **tugas besar** dari mata kuliah **Visualisasi Data (IF-43-PIL-DS02)** Universitas Telkom

        #### Dataset
        [COVID-19 Indonesia Dataset](https://www.kaggle.com/datasets/hendratno/covid19-indonesia)

        #### Author
        1. Irgi Ahmad Maulana (1301218548)
        2. Monica Dewi Seba Pasaribu (1301218691)
    ''')


def filter_main(df):
    # Preprocessed data
    cols_filter = ['New Cases',
                   'New Deaths', 'New Recovered']

    # data filter
    df_filter = df[['Date', 'New Cases',
                    'New Deaths', 'New Recovered', 'Location']]
    data_filter = st.selectbox('Pilih data', cols_filter)
    title = f"Akumulasi {data_filter} Tiap Kota"
    show_filter = st.checkbox('Tampilkan filter lain')

    df_filter['Date'] = pd.to_datetime(df_filter['Date'])

    if show_filter:
        # unique years and months from the DataFrame
        years = df_filter['Date'].dt.year.unique()
        months = df_filter['Date'].dt.month.unique()

        selected_year = st.selectbox('Select Year', years)

        # filter the DataFrame based on the selected year
        filtered_df_year = df_filter[df_filter['Date'].dt.year ==
                                     selected_year]

        selected_month = st.selectbox(
            'Select Month', months, format_func=lambda m: calendar.month_name[m])

        # filter the DataFrame based on the selected month
        filtered_df_month = filtered_df_year[filtered_df_year['Date'].dt.month == selected_month]

        # get the unique dates from the filtered DataFrame
        dates = filtered_df_month['Date'].dt.date.unique()

        # slider for selecting a specific date
        selected_date = st.slider('Select Date', min_value=min(
            dates), max_value=max(dates), value=min(dates))

        # filter the DataFrame based on the selected date
        filtered_df_date = filtered_df_month[filtered_df_month['Date'].dt.date == selected_date]
        filtered_df_cumulative = filtered_df_date[filtered_df_date['Location'] != 'Indonesia']
        filtered_df_cumulative = filtered_df_cumulative.groupby(
            'Location').sum().reset_index()
    else:
        filtered_df_cumulative = df_filter[df_filter['Location']
                                           != 'Indonesia']
        filtered_df_cumulative = filtered_df_cumulative.groupby(
            'Location').sum().reset_index()

    return filtered_df_cumulative, data_filter, title


def chart_main(df, data_filter, title):
    chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Location:O', sort=alt.EncodingSortField(
            field=data_filter, order='descending')),
        x=data_filter,
        tooltip=['Location', data_filter]
    ).properties(
        width=400,
        height=alt.Step(20),  # Adjust the height of each bar
        title=title
    )

    chart


def main_menu(df):

    st.header(f'Akumulasi Data Tiap Kota')

    col1, col2 = st.columns(2)
    with col1:
        filtered_df_cumulative, data_filter, title = filter_main(df)
    with col2:
        chart_main(filtered_df_cumulative, data_filter, title)


def monthly_cases_page(df):
    filter = st.selectbox('Urutkan',
                          ('Case tertinggi', 'Case terendah'))

    monthly_cases_visual(filter, df)


def monthly_cases_visual(filter, df):

    df['Date'] = pd.to_datetime(df['Date'])
    df['Bulan'] = df['Date'].dt.strftime('%B %Y')
    monthly_sum_cases = df.groupby('Bulan')['New Cases'].sum()

    # Create a new DataFrame with the desired format
    monthly_df = pd.DataFrame(
        {'Bulan': monthly_sum_cases.index, 'Total Cases': monthly_sum_cases.values})

    # Sort the DataFrame in descending order (from max to min)
    monthly_df_descending = monthly_df.sort_values(
        by='Total Cases', ascending=False)

    # Sort the DataFrame in ascending order (from min to max)
    monthly_df_ascending = monthly_df.sort_values(
        by='Total Cases', ascending=True)

    if (filter == "Case terendah"):
        monthly_plot(monthly_df_ascending, filter)
    else:
        monthly_plot(monthly_df_descending, filter)


def monthly_plot(dataframe, filter):

    title = ""
    if (filter == "Case terendah"):
        title = "Case Bulanan Terendah Ke Tertinggi"
        order = 'ascending'
    else:
        title = "Case Bulanan Tertinggi Ke Terendah"
        order = 'descending'

    monthly_df = dataframe.sort_values(
        by='Total Cases', ascending=True)
    # Create the bar plot using Altair
    chart = alt.Chart(monthly_df).mark_bar().encode(
        x=alt.X('Bulan:O', sort=alt.EncodingSortField(
            field='Total Cases', op='sum', order=order)),
        y='Total Cases',
        tooltip=['Bulan', 'Total Cases']
    ).properties(
        width=alt.Step(40),  # Adjust the width of each bar
        title=title
    )

    # Display the chart using st.altair_chart()
    st.altair_chart(chart, use_container_width=True)
    st.caption("Arahkan pointer ke bar untuk melihat detail")


def main():
    sidebar()


main()
