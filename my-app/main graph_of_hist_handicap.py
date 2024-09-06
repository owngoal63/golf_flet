import flet as ft
import requests
from datetime import datetime

class State:
    toggle = True

s = State()

def main(page: ft.Page):
    # page.add(ft.SafeArea(ft.Text("Hello, Flet!")))

    # building the complete API URL
    url = 'https://kenton.eu.pythonanywhere.com/api/getcurrenthandicap/1/?format=json'
    url = 'https://kenton.eu.pythonanywhere.com/api/gethistoricalhcp/1/?format=json'

    # sending a GET request to the API
    response = requests.get(url)

    # hcp_dict = {}

    # checking if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # parsing the JSON response data
        hcp_data = response.json()

        worst_hcp = hcp_data["worst_hcp"]
        best_hcp = hcp_data["best_hcp"]
        mid_point = best_hcp + (worst_hcp - best_hcp) / 2

        print(best_hcp, mid_point, worst_hcp)
        # hcp_first_m = hcp_data["hcp_monthly_averages"][0][1]
        hcp_monthly_averages = hcp_data["hcp_monthly_averages"]
        print(hcp_monthly_averages)
        x_points = len(hcp_monthly_averages)
        d_pts = []
        for i, hcp_monthly_average in enumerate(hcp_monthly_averages):
            d_pts.append(ft.LineChartDataPoint(i, hcp_monthly_average[1]))
        #     page.add(ft.SafeArea(ft.Text(f"{i} - {hcp_monthly_average[1]}")))
        print(d_pts)
        # page.add(ft.SafeArea(ft.Text(hcp_dict['worst_hcp'])))
        # page.add(ft.SafeArea(ft.Text(hcp_first_m)))



    # btn = ft.ElevatedButton("Click me!")
    # page.add(btn)
    data_1 = [
        ft.LineChartData(
            data_points=d_pts,
            stroke_width=5,
            color=ft.colors.CYAN,
            curved=True,
            stroke_cap_round=True,
        )
    ]

    # data_2 = [
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(0, 3.44),
    #             ft.LineChartDataPoint(2.6, 3.44),
    #             ft.LineChartDataPoint(4.9, 3.44),
    #             ft.LineChartDataPoint(6.8, 3.44),
    #             ft.LineChartDataPoint(8, 3.44),
    #             ft.LineChartDataPoint(9.5, 3.44),
    #             ft.LineChartDataPoint(11, 3.44),
    #         ],
    #         stroke_width=5,
    #         color=ft.colors.CYAN,
    #         curved=True,
    #         stroke_cap_round=True,
    #     )
    # ]

    chart = ft.LineChart(
        data_series=data_1,
        border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
        ),
        vertical_grid_lines=ft.ChartGridLines(
            interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
        ),
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=int(best_hcp) - 1,
                    label=ft.Text(str(int(best_hcp) - 1), size=14, weight=ft.FontWeight.BOLD),
                ),
                ft.ChartAxisLabel(
                    value=int(mid_point),
                    label=ft.Text(str(int(mid_point)), size=14, weight=ft.FontWeight.BOLD),
                ),
                ft.ChartAxisLabel(
                    value=int(worst_hcp) + 1,
                    label=ft.Text(str(int(worst_hcp) + 1), size=14, weight=ft.FontWeight.BOLD),
                ),
            ],
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=0,
                    label=ft.Container(
                        ft.Text(
                            datetime.strptime(hcp_monthly_averages[0][0], '%Y-%m-%d').strftime('%b %y'),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                        ),
                        margin=ft.margin.only(top=10, left=60),
                    ),
                ),
                ft.ChartAxisLabel(
                    value=int(x_points/2),
                    label=ft.Container(
                        ft.Text(
                            datetime.strptime(hcp_monthly_averages[int(x_points/2)][0], '%Y-%m-%d').strftime('%b %y'),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                        ),
                        margin=ft.margin.only(top=10),
                    ),
                ),
                ft.ChartAxisLabel(
                    value=x_points,
                    label=ft.Container(
                        ft.Text(
                            datetime.strptime(hcp_monthly_averages[x_points - 1][0], '%Y-%m-%d').strftime('%b %y'),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                        ),
                        margin=ft.margin.only(top=10, right=60),
                    ),
                ),
            ],
            labels_size=32,
        ),
        tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
        min_y=int(best_hcp) - 2,
        max_y=int(worst_hcp) + 2,
        min_x=0,
        max_x=x_points,
        # animate=5000,
        expand=True,
    )

    def toggle_data(e):
        if s.toggle:
            chart.data_series = data_1
            chart.interactive = False
        else:
            chart.data_series = data_1
            chart.interactive = True
        s.toggle = not s.toggle
        chart.update()

    # chart.data_series = data_1
    # chart.interactive = True
    # chart.update()

    page.add(ft.ElevatedButton("avg", on_click=toggle_data), chart)


ft.app(main)
