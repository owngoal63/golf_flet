import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Handicappy Scorecard"
    page.padding = 5
    page.bgcolor = "GREEN"
    page.icon = "golfpin.png"
    page.icon =  ft.icons.PERSON

    container_width = 100
    container_height = 70
    animation_duration = 300
    default_color = '#041955'
    highlight_color = ft.colors.PURPLE

    # URL
    url = 'http://127.0.0.1:8000/api/getscoredetails/11/?format=json'

    # Placeholder for the Score Container
    outer_container = ft.AnimatedSwitcher(
        content = ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=900,
        reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )

    global score_data
    global container_focus

    class header_text(ft.UserControl):
        def __init__(self, course_name:str, group_name:str, date:str):
            super().__init__()
            self.course_name = course_name
            self.group_name = group_name
            self.date = date

        def build(self) -> ft.Container:
            return ft.Container(
                margin = ft.margin.only(top=40),
                on_click = reload_data,
                content=ft.Column(
                    controls=[
                    ft.Text(self.course_name, size=20, weight='bold'),
                    # ft.IconButton(ft.icons.REFRESH, on_click=reload_data),
                    ft.Text(f"{self.group_name} ({self.date})", size=16, weight='bold')
                    ]
                )
            )
    
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
            border_radius=10,
            width=container_width,
            height=container_height,
            bgcolor=default_color,
            padding=5,
            animate=ft.animation.Animation(animation_duration, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.animation.Animation(animation_duration, ft.AnimationCurve.EASE_IN_OUT),
            data=index,
            left=index * (container_width + 10),
            top=0,
            content=ft.Column(
                controls=[
                    ft.Text(
                        value=f"{score_data['player_details_list'][index]['firstname']} {str(score_data['player_details_list'][index]['course_hcp'])}",
                        color="YELLOW",
                        text_align=ft.TextAlign.CENTER,
                        width=container_width - 10,  # Subtract padding
                    ),
                    ft.Icon(
                        ft.icons.PERSON,
                        size=40,
                        color=ft.colors.YELLOW
                    )
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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

        # print(score_data['player_details_list'][player_index]['firstname'])

        holes_list = list(range(1, 19))
        course_par_holes_list = score_data['player_details_list'][player_index]['course_par_holes_list']
        course_si_holes_list = score_data['player_details_list'][player_index]['course_si_holes_list']
        player_gross_score_list = score_data['player_details_list'][player_index]['gross_score_holes_list']
        player_net_score_list = score_data['player_details_list'][player_index]['net_score_holes_list']

        # Combine the 5 lists into a list of lists
        data = [[a, b, c, d, e] for a, b, c, d, e in zip(holes_list, course_par_holes_list, course_si_holes_list, player_gross_score_list,player_net_score_list )]
        # Add table headers to top
        data.insert(0, ["Hole", "Par", "SI", "GRS", "NET"])


        def create_cell(text, is_header=False, row_index=0):
            if isinstance(text, str) and set(text) == {'*'}:  # Check if text consists only of asterisks
                num_icons = len(text)
                cell_content = ft.Row(
                    controls=[ft.Icon(ft.icons.SPORTS_GOLF, size=12, color=ft.colors.BLACK) for _ in range(num_icons)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2
                )
            else:
                cell_content = ft.Text(
                    str(text),
                    size=10,
                    weight="bold" if is_header else "normal",
                    color=ft.colors.BLACK
                )

            return ft.Container(
                content=cell_content,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=3,
                width=50,
                height=25,
                bgcolor=(ft.colors.BLUE_50 if is_header else 
                        ft.colors.YELLOW if row_index == score_data["current_hole_recorded"] else 
                        (ft.colors.GREY_100 if row_index % 2 == 0 else ft.colors.WHITE))
            )
        
        table = ft.Column(
            controls=[
                ft.Row(
                    controls=[create_cell(cell, is_header=(i == 0), row_index=i) for cell in row],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
                for i, row in enumerate(data)
            ],
            spacing=2,
        )

        # Wrap the table in an outer container
        outer_container_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(score_data['player_details_list'][player_index]['firstname'] + " " + str(score_data['player_details_list'][player_index]['gross_score']) + " (" + str(score_data['player_details_list'][player_index]['net_score']) + ")",
                                         color=ft.colors.WHITE),
                        padding=10,
                        bgcolor=ft.colors.PURPLE,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10),
                        width=150
                    ),
                    ft.Container(
                       content=table,
                        padding=5,
                        bgcolor=ft.colors.BLUE_GREY_50,
                        border=ft.border.all(2, ft.colors.PURPLE),
                        border_radius = ft.border_radius.only(
                            top_left=0,
                            top_right=10,
                            bottom_right=10,
                            bottom_left=10),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLUE_GREY_300,
                            offset=ft.Offset(0, 5),
                        )
                    ),
                ],
                spacing=0,
            ),
            padding=20,
        )


        outer_container.content = outer_container_content

        page.update()


    def reload_data(e) -> None:
        print("Reload data")
        url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/99/?format=json'
        global score_data
        score_data = get_api_data(url)
        # print(score_data)
        # print("score data score id reload data", score_data["score_id"])
        update_data_table(0)
        global container_focus
        # print("reload container focus", container_focus)
        update_data_table(int(container_focus))
        page.update()
        return
   
    score_data = get_api_data(url)

    header = header_text(score_data["course_name"], score_data["group_name"], score_data["date"])
    page.add(header)


    containers = [create_container(i) for i in range(score_data["no_of_players"])]

    for container in containers:
        container.on_click = container_click

    # Set initial container to highlight colour
    containers[0].bgcolor = highlight_color

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

    main_column.controls.append(outer_container)

    update_data_table(0)

    # Add the main column to the page
    # page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))
    page.add(main_column)
    page.add(ft.FilledButton("Reload Scores", icon="refresh", on_click=reload_data))

ft.app(target=main)