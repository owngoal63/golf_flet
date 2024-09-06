import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Animated Container Reordering"
    page.padding = 50
    page.theme_mode = ft.ThemeMode.LIGHT

    container_width = 170
    container_height = 110
    animation_duration = 300
    default_color = ft.colors.BLUE
    highlight_color = ft.colors.RED

    # URL
    url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/102/?format=json'

    # Placeholder for the DataTable
    # data_table = ft.Column()
    data_table = ft.AnimatedSwitcher(
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=900,
        reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )


    global score_data
    global container_focus

    
    def get_api_data(url: str):

        # sending a GET request to the API
        response = requests.get(url)

        if response.status_code == 200: # checking if the request was successful (HTTP status code 200)
            # parsing the JSON response data
            score_data = response.json()
            date = score_data["date"]
        else:
            page.add(ft.SafeArea(ft.Text(f"Unable to retrieve URL:{url}")))

        return score_data 
    
    def create_container(index):
        return ft.Container(
            border_radius=20,
            width=container_width,
            height=container_height,
            bgcolor=default_color,
            padding=15,
            # border_radius=ft.border_radius.all(10),
            animate=ft.animation.Animation(animation_duration, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.animation.Animation(animation_duration, ft.AnimationCurve.EASE_IN_OUT),
            data=index,
            left=index * (container_width + 10),
            top=0,
            content=ft.Column(
                    controls=[
                        ft.Text(value=f"{score_data['player_details_list'][index]['firstname']} ({score_data['player_details_list'][index]['gross_score']} vs {score_data['player_details_list'][index]['target_score']})", color="YELLOW"),
                        ft.Text(value=str(score_data['player_details_list'][index]['course_hcp']), color="WHITE"),
                        ft.Container(
                            width=160,
                            height=5,
                            bgcolor='WHITE',
                            border_radius=20,
                            padding=ft.padding.only(right=140-int(140*((score_data['player_details_list'][index]['gross_score']/score_data['player_details_list'][index]['target_score']))) ),     # 140 is max width
                            content=ft.Container(
                                bgcolor="PINK",
                            ),                 
                        )
                    ]
                ),
            alignment=ft.alignment.center,
        )


    def container_click(e):
        clicked_container = e.control
        clicked_index = containers.index(clicked_container)

        # Reset all containers to default color
        for container in containers:
            container.bgcolor = default_color

        # Change color of clicked container
        clicked_container.bgcolor = highlight_color

        # Rearrange containers
        containers.insert(0, containers.pop(clicked_index))

        # Animate positions
        for i, container in enumerate(containers):
            container.left = i * (container_width + 10)

        global container_focus
        # container_focus = containers[0].key
        container_focus = clicked_container.data

        update_data_table(clicked_container.data)

        page.update()

    def update_data_table(player_index):
        global score_data
        columns=[
            ft.DataColumn(ft.Text("Hole", size=12, weight='bold', color='white'), numeric=True),
            ft.DataColumn(ft.Text("Par", size=12, weight='bold', color='white'), numeric=True),
            ft.DataColumn(ft.Text("SI", size=12, weight='bold', color='white'), numeric=True),
            ft.DataColumn(ft.Text("GRS", size=12, weight='bold', color='white'), numeric=True),
            ft.DataColumn(ft.Text("NET", size=12, weight='bold', color='white'), numeric=True),
        ]

        rows = []
        for i in range(0,18):
            rows.append(ft.DataRow(cells = [
                ft.DataCell(ft.Text(i+1, size=12, color='black')),
                ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["course_par_holes_list"][i], size=12, color='black')),
                ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["course_si_holes_list"][i], size=12, color='black')),
                ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["gross_score_holes_list"][i], size=12, color='black')),
                ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["net_score_holes_list"][i], size=12, color='black'))
            ]))

        data_table_content = ft.DataTable(
            width=600,
            bgcolor="blue",
            heading_row_color="black",
            border=ft.border.all(2, "black"),
            border_radius=10,
            heading_row_height=36,
            data_row_min_height = 20,
            data_row_max_height=28,
            column_spacing=30,
            divider_thickness=1,
            columns=columns,
            rows=rows
        )

        data_table.content = data_table_content

        # Wrap the DataTable in a Container with Scale animation
        # animated_table = ft.Container(
        #     content=data_table_content,
        #     scale=ft.transform.Scale(scale=0),
        #     animate_scale=ft.animation.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        # )

        # Clear previous content and add new animated DataTable
        # data_table.controls.clear()
        # data_table.controls.append(animated_table)
        
        # Trigger the animation
        # animated_table.scale = ft.transform.Scale(scale=1)
        page.update()


    def reload_data(e) -> None:
        print("Reload data")
        url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/99/?format=json'
        global score_data
        score_data = get_api_data(url)
        print(score_data)
        print("score data score id reload data", score_data["score_id"])
        update_data_table(0)
        print("reload container focus", container_focus)
        update_data_table(int(container_focus))
        page.update()
        return
   
    score_data = get_api_data(url)
    # print(score_data)
    containers = [create_container(i) for i in range(score_data["no_of_players"])]

    for container in containers:
        container.on_click = container_click

    stack = ft.Stack(
        controls=containers,
        width=(container_width * score_data["no_of_players"]) + 20,
        height=container_height
    )

    page.add(stack)

    # Create a Row to hold the containers
    row = ft.Row(spacing=5)

    # Create a Column to hold the row and the DataTable
    main_column = ft.Column(spacing=10)
    main_column.controls.append(row)

    main_column.controls.append(data_table)

    update_data_table(0)

    # Add the main column to the page
    page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))
    page.add(main_column)

ft.app(target=main)