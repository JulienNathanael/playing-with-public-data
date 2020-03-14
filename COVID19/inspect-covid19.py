# Written by: JL
# Data source: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series

import os
import pandas as pd
import plotly.graph_objects as go



# ONLY LINE THAT MUST BE MODIFIED: PATH TO THE COVID-19 FOLDER
path_dir_COVID19_repo = ''



def plot_states_situation_evolution(df, states, title='', show=True):
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

    if show is True:
        fig.show()


def prepare_df_states(df):
    return df.drop(columns=['Province/State', 'Lat', 'Long']).groupby('Country/Region').sum()


if __name__ == '__main__':
    path_dir_data = os.path.join(path_dir_COVID19_repo, 'csse_covid_19_data', 'csse_covid_19_time_series')
    path_confirmed = os.path.join(path_dir_data, 'time_series_19-covid-Confirmed.csv')
    path_deaths = os.path.join(path_dir_data, 'time_series_19-covid-Deaths.csv')
    path_recovered = os.path.join(path_dir_data, 'time_series_19-covid-Recovered.csv')

    # Evolution of cumulated cases per country
    df_confirmed = prepare_df_states(pd.read_csv(path_confirmed))
    df_deaths = prepare_df_states(pd.read_csv(path_deaths))
    df_recovered = prepare_df_states(pd.read_csv(path_recovered))

    # 10 states with highest confirmed cases
    states_with_most_confirmed = df_confirmed.iloc[:, -1].sort_values(ascending=False).head(10).index

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
    beta = 0.9
    df_confirmed_daily_increase_exp_av = pd.DataFrame(index=df_confirmed_daily_increase.index, columns=df_confirmed_daily_increase.columns)
    df_confirmed_daily_increase_exp_av_b_corr = pd.DataFrame(index=df_confirmed_daily_increase.index, columns=df_confirmed_daily_increase.columns)

    for nday, day in enumerate(df_confirmed_daily_increase_exp_av.columns):
        if nday == 0:
            df_confirmed_daily_increase_exp_av.iloc[:, nday] = 0
            df_confirmed_daily_increase_exp_av_b_corr.iloc[:, nday] = 0
        else:
            df_confirmed_daily_increase_exp_av.iloc[:, nday] = beta * df_confirmed_daily_increase_exp_av.iloc[:, nday - 1] + (1 - beta) * df_confirmed_daily_increase.iloc[:, nday]
            df_confirmed_daily_increase_exp_av_b_corr.iloc[:, nday] = (1 / (1 - beta ** nday)) * df_confirmed_daily_increase_exp_av.iloc[:, nday]

    # Plots
    plot_states_situation_evolution(df=df_confirmed, states=states_with_most_confirmed, title='Number of confirmed')
    plot_states_situation_evolution(df=df_deaths, states=states_with_most_confirmed, title='Number of deaths')
    plot_states_situation_evolution(df=df_recovered, states=states_with_most_confirmed, title='Number of recovered')
    plot_states_situation_evolution(df=df_deaths_over_confirmed, states=states_with_most_confirmed, title='Evolution of ratio (deaths / confirmed), only when more than 100 deaths')
    plot_states_situation_evolution(df=df_deaths_over_closed, states=states_with_most_confirmed, title='Evolution of ratio (deaths / (deaths + recovered)), only when more than 100 deaths')
    plot_states_situation_evolution(df=df_confirmed_daily_increase, states=states_with_most_confirmed, title='Confirmed per country, daily increase')
    plot_states_situation_evolution(df=df_deaths_daily_increase, states=states_with_most_confirmed, title='Deaths per country, daily increase')
    plot_states_situation_evolution(df=df_recovered_daily_increase, states=states_with_most_confirmed, title='Recovered per country, daily increase')
    plot_states_situation_evolution(df=df_confirmed_daily_increase_exp_av_b_corr, states=states_with_most_confirmed,
                                    title='Confirmed per country, daily increase, exponentially averaged with bias correction - WARNING: delay as a cost of smoothness')

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
