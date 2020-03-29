# Written by: JL
# Data source: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series

import os
import pandas as pd
import plotly.graph_objects as go


with open('default.env', 'r') as file:
    var_name = 'path_dir_COVID19_repo'
    first_line = file.readline().strip()
    assert var_name + '=' == first_line[:len(var_name + '=')]
    path_dir_COVID19_repo = first_line[len(var_name + '='):]


def plot_states_situation_evolution(df, states, title='', html=False, log_y=False, show=True, filename=None):
    # df indexes are states
    # states must all be in df.index
    # df columns: dates
    print('Plotting graph: ' + title)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=df.columns,
                y=df.loc[state, :],
                name=state
            )
            for state in states
        ]
    )

    fig.update_layout(title=title)

    if log_y is True:
        fig.update_layout(yaxis_type='log')

    if show is True:
        fig.show()

    if html is True and filename is not None:
        fig.write_html(file=filename)


def prepare_df_states(df):
    return df.drop(columns=['Province/State', 'Lat', 'Long']).groupby('Country/Region').sum()


if __name__ == '__main__':
    path_dir_data = os.path.join(path_dir_COVID19_repo, 'csse_covid_19_data', 'csse_covid_19_time_series')
    path_confirmed = os.path.join(path_dir_data, 'time_series_covid19_confirmed_global.csv')
    path_deaths = os.path.join(path_dir_data, 'time_series_covid19_deaths_global.csv')
    path_recovered = os.path.join(path_dir_data, 'time_series_covid19_recovered_global.csv')

    # Evolution of cumulated cases per country
    df_confirmed = prepare_df_states(pd.read_csv(path_confirmed))
    df_deaths = prepare_df_states(pd.read_csv(path_deaths))
    df_recovered = prepare_df_states(pd.read_csv(path_recovered))

    # 10 states with highest number of deaths
    countries_with_most_deaths = df_deaths.iloc[:, -1].sort_values(ascending=False).head(10).index

    # Evolution of morbidity estimators (far from perfect...)
    df_deaths_over_confirmed = df_deaths / df_confirmed
    df_deaths_over_closed = df_deaths / (df_deaths + df_recovered)
    # Keeping only values if total deaths number is over 100
    df_deaths_over_confirmed = df_deaths_over_confirmed[df_deaths > 100]
    df_deaths_over_closed = df_deaths_over_closed[df_deaths > 100]

    # Evolution of daily increase per country
    df_confirmed_daily_increase = df_confirmed.diff(axis=1)
    df_deaths_daily_increase = df_deaths.diff(axis=1)
    df_recovered_daily_increase = df_recovered.diff(axis=1)

    # Smoothing daily increase per country - exponentially weighted averages: WARNING with delay
    beta = 0.8
    df_confirmed_daily_increase_exp_av = pd.DataFrame(index=df_confirmed_daily_increase.index, columns=df_confirmed_daily_increase.columns)
    df_confirmed_daily_increase_exp_av_b_corr = pd.DataFrame(index=df_confirmed_daily_increase.index, columns=df_confirmed_daily_increase.columns)

    for nday, day in enumerate(df_confirmed_daily_increase_exp_av.columns):
        if nday == 0:
            df_confirmed_daily_increase_exp_av.iloc[:, nday] = 0
            df_confirmed_daily_increase_exp_av_b_corr.iloc[:, nday] = 0
        else:
            df_confirmed_daily_increase_exp_av.iloc[:, nday] = beta * df_confirmed_daily_increase_exp_av.iloc[:, nday - 1] + (1 - beta) * df_confirmed_daily_increase.iloc[:, nday]
            df_confirmed_daily_increase_exp_av_b_corr.iloc[:, nday] = (1 / (1 - beta ** nday)) * df_confirmed_daily_increase_exp_av.iloc[:, nday]

    # Evolution of number of deaths; for each country, day 0 corresponds to the first day with more than 100 deaths
    df_deaths_filtered = df_deaths[df_deaths.max(axis=1) > 100]  # Keep only countries with more than 100 deaths
    df_building_day0_100deaths = pd.DataFrame(index=df_deaths_filtered.index)
    df_building_day0_100deaths['#days < 100 deaths'] = (df_deaths_filtered < 100).sum(axis=1)
    df_building_day0_100deaths['#days >= 100 deaths'] = (df_deaths_filtered >= 100).sum(axis=1)

    df_deaths_day0_100deaths = pd.DataFrame(index=df_deaths_filtered.index, columns=list(range(-df_building_day0_100deaths['#days < 100 deaths'].max(), df_building_day0_100deaths['#days >= 100 deaths'].max())))
    for ind_c, country in enumerate(df_deaths_filtered.index):
        for ind_d, day in enumerate(list(range(-df_building_day0_100deaths['#days < 100 deaths'][country], df_building_day0_100deaths['#days >= 100 deaths'][country]))):
            df_deaths_day0_100deaths[day][country] = df_deaths_filtered.iloc[ind_c, ind_d]

    # 10days before 100deaths, nothing to focus on
    df_deaths_day0_100deaths.drop(columns=list(range(-df_building_day0_100deaths['#days < 100 deaths'].max(), -10)), inplace=True)

    # Plots
    plot_states_situation_evolution(df=df_confirmed, states=countries_with_most_deaths, title='Number of confirmed')
    plot_states_situation_evolution(df=df_deaths, states=countries_with_most_deaths, title='Number of deaths')
    plot_states_situation_evolution(df=df_deaths, states=countries_with_most_deaths, log_y=True, title='Number of deaths (log)')
    plot_states_situation_evolution(df=df_recovered, states=countries_with_most_deaths, title='Number of recovered')
    plot_states_situation_evolution(df=df_deaths_over_confirmed, states=countries_with_most_deaths, title='Evolution of ratio (deaths / confirmed), only when more than 100 deaths')
    plot_states_situation_evolution(df=df_deaths_over_closed, states=countries_with_most_deaths, title='Evolution of ratio (deaths / (deaths + recovered)), only when more than 100 deaths')
    plot_states_situation_evolution(df=df_confirmed_daily_increase, states=countries_with_most_deaths, title='Confirmed per country, daily increase')
    plot_states_situation_evolution(df=df_deaths_daily_increase, states=countries_with_most_deaths, title='Deaths per country, daily increase')
    plot_states_situation_evolution(df=df_recovered_daily_increase, states=countries_with_most_deaths, title='Recovered per country, daily increase')
    plot_states_situation_evolution(df=df_confirmed_daily_increase_exp_av_b_corr, states=countries_with_most_deaths,
                                    title='Confirmed per country, daily increase, exponentially averaged with bias correction - WARNING: delay as a cost of smoothness')

    countries_with_more_than_100states = [country for country in countries_with_most_deaths if country in df_deaths_day0_100deaths.index]
    plot_states_situation_evolution(df=df_deaths_day0_100deaths, states=countries_with_more_than_100states, html=True,
                                    filename='covid19_ndeaths_evolution_day0_100deaths.html', title='Number of deaths, day0: about 100 deaths')
    plot_states_situation_evolution(df=df_deaths_day0_100deaths, states=countries_with_more_than_100states, log_y=True, title='Number of deaths, day0: about 100 deaths (log)')

    # Summary tables
    df_summary = pd.DataFrame(
        index=[],
        columns=[],
    )
    df_summary['confirmed'] = df_confirmed.iloc[:, -1]
    df_summary['deaths'] = df_deaths.iloc[:, -1]
    df_summary['recovered'] = df_recovered.iloc[:, -1]
    df_summary['deaths/confirmed'] = df_deaths_over_confirmed.iloc[:, -1]
    df_summary['deaths/(deaths+recovered)'] = df_deaths_over_closed.iloc[:, -1]
    df_summary = df_summary.loc[df_summary.iloc[:, 0].sort_values(ascending=False).index, :]

    df_summary.to_html('summary-table-covid19.html')
