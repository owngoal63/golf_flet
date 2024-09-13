import flet as ft
import requests

### Global Variables ###
# global score_data

### App Variables ###
container_width = 90
container_height = 70
animation_duration = 300
default_color = '#041955'
highlight_color = ft.colors.PURPLE
url = 'http://127.0.0.1:8000/api/getscorecardheaders/'
url = 'https://kenton.eu.pythonanywhere.com/api/getscorecardheaders/'


class MenuItem:
    def __init__(self, display, scorecard_id):
        self.display = display
        self.scorecard_id = scorecard_id

menuitems = []

### Get API Data function ###
def get_api_data(url: str):

    # sending a GET request to the API
    response = requests.get(url)

    if response.status_code == 200: # checking if the request was successful (HTTP status code 200)
        # parsing the JSON response data
        url_data = response.json()
        # date = scorecards_data["date"]
    # else:
    #     page.add(ft.SafeArea(ft.Text(f"Unable to retrieve URL:{url}")))

    return url_data
### End of Get API Data

scorecards_data = get_api_data(url)
# print(scorecards_data)
for scorcard_header_data in scorecards_data:
    # print(scorcard_header_data["date"])
    menuitems.append(MenuItem(f'{scorcard_header_data["date"]} {scorcard_header_data["course"]} {scorcard_header_data["group"]} ({scorcard_header_data["id"]})', str(scorcard_header_data["id"])))


def main(page: ft.Page):

    global score_data
    global player_select_containers

    page.title = "Handy Scorecard App"

    # Placeholder for the Score Container
    scorecard_outer_container = ft.AnimatedSwitcher(
        content = ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=900,
        reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )

    ### Header Text Class ### 
    class header_text(ft.UserControl):
        def __init__(self, course_name:str, group_name:str, date:str):
            super().__init__()
            self.course_name = course_name
            self.group_name = group_name
            self.date = date

        def build(self) -> ft.Container:
            return ft.Container(
                margin = ft.margin.only(top=10),
                # on_click = reload_data,
                content=ft.Column(
                    controls=[
                    ft.Text(self.course_name, size=18, weight='bold', color='WHITE'),
                    # ft.IconButton(ft.icons.REFRESH, on_click=reload_data),
                    ft.Text(f"{self.group_name} ({self.date})", size=14, weight='bold', color='WHITE')
                    ]
                )
            )
    ### End of Header Text ###


    ### Functions for Player Select Controls ####
    def player_select_container(index, score_data):
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
                        value=f"{score_data['player_details_list'][index]['firstname'][:5]} {str(score_data['player_details_list'][index]['stableford_total'])}",
                        color="YELLOW",
                        text_align=ft.TextAlign.CENTER,
                        size = 12,
                        weight='bold',
                        width=container_width - 15,  # Subtract padding
                    ),
                    ft.Icon(
                        ft.icons.PERSON,
                        size=30,
                        color=ft.colors.YELLOW
                    )
                ],
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )

    def player_select_stack(player_select_containers, score_data):
        return ft.Stack(
                controls=player_select_containers,
                width=(container_width * score_data["no_of_players"]) + 30,
                height=container_height
                )

    def container_click(e):
        clicked_container = e.control
        clicked_index = player_select_containers.index(clicked_container)
        # Reset all containers to default color
        for container in player_select_containers:
            container.bgcolor = default_color
        # Change color of clicked container
        clicked_container.bgcolor = highlight_color
        # Rearrange containers
        player_select_containers.insert(0, player_select_containers.pop(clicked_index))
        # Animate positions
        for i, container in enumerate(player_select_containers):
            container.left = i * (container_width + 10)
        global container_focus
        container_focus = clicked_container.data

        update_data_table(clicked_container.data)
        page.update()
    
    ### End of Functions for Player Select Controls ###


    ### Functions for Player Scorecard ####
    def update_data_table(player_index):

        holes_list = list(range(1, 19))
        course_par_holes_list = score_data['player_details_list'][player_index]['course_par_holes_list']
        course_si_holes_list = score_data['player_details_list'][player_index]['course_si_holes_list']
        player_gross_score_list = score_data['player_details_list'][player_index]['gross_score_holes_list']
        player_net_score_list = score_data['player_details_list'][player_index]['net_score_holes_list']
        player_stableford_score_list = score_data['player_details_list'][player_index]['stableford_score_holes_list']

        # Combine the 5 lists into a list of lists
        data = [[a, b, c, d, e] for a, b, c, d, e in zip(holes_list, course_par_holes_list, course_si_holes_list, player_gross_score_list,player_net_score_list)]
        # Add table headers to top
        data.insert(0, ["Hole", "Par", "SI", "GRS", "NET"])
        # Add out totals
        data.insert(10, ["Out", str(score_data['player_details_list'][player_index]['out_par_total']), "", str(score_data['player_details_list'][player_index]['out_gross_score']), str(score_data['player_details_list'][player_index]['out_net_score'])])
        # Add in totals
        data.insert(20, ["In", str(score_data['player_details_list'][player_index]['in_par_total']), "", str(score_data['player_details_list'][player_index]['in_gross_score']), str(score_data['player_details_list'][player_index]['in_net_score'])])
        # Add Overall Totals
        overall_par_total = score_data['player_details_list'][player_index]['out_par_total'] + score_data['player_details_list'][player_index]['in_par_total']
        if score_data["current_hole_recorded"] == 18:
            overall_gross_total = score_data['player_details_list'][player_index]['out_gross_score'] + score_data['player_details_list'][player_index]['in_gross_score']
            overall_net_total = score_data['player_details_list'][player_index]['out_net_score'] + score_data['player_details_list'][player_index]['in_net_score']
        else:
            overall_gross_total = '' 
            overall_net_total = ''
        data.insert(21, ["Total", str(overall_par_total), "", str(overall_gross_total), str(overall_net_total)]) 

        current_hole_row = score_data["current_hole_recorded"] if score_data["current_hole_recorded"] <= 9 else score_data["current_hole_recorded"] + 1
        try:
            if int(score_data['player_details_list'][player_index]['target_score']) > 0:
                shots_remaining_to_target = -1 * (score_data['player_details_list'][player_index]['gross_score'] - score_data['player_details_list'][player_index]['target_score'])
            else:
                shots_remaining_to_target = ""
        except:
            shots_remaining_to_target = ""


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
                    weight="normal",
                    color=(ft.colors.WHITE if is_header else ft.colors.BLACK)
                )

            return ft.Container(
                content=cell_content,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=3,
                width=45,
                height=22,
                bgcolor=(ft.colors.BLACK54 if is_header else 
                        ft.colors.YELLOW if row_index == current_hole_row else 
                        (ft.colors.GREY_100 if row_index % 2 == 0 else ft.colors.WHITE))
            )
        
        table = ft.Column(
            controls=[
                ft.Row(
                    controls=[create_cell(cell, is_header=(i == 0 or i == 10 or i == 20 or i == 21), row_index=i) for cell in row],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
                for i, row in enumerate(data)
            ],
            spacing=2,
        )

        # Define Enter Scores button (gesture Text workaround ??) only if round is not complete and player_type is "Admin"
        if score_data["current_hole_recorded"] <= 17 and score_data['player_details_list'][player_index]['player_type'] == "Admin":
            button_and_or_score = ft.GestureDetector(
                content=ft.Text(f"{score_data['player_details_list'][player_index]['firstname']} {str(score_data['player_details_list'][player_index]['gross_score'])}/{str(score_data['player_details_list'][player_index]['net_score'])}   ",
                size=12,
                color=ft.colors.WHITE,
                weight=ft.FontWeight.BOLD
                ),
            on_tap=lambda _: page.go("/add_score")
            ) 
        else:     # Just show Score Text
            button_and_or_score = ft.Text(f"{score_data['player_details_list'][player_index]['firstname']} {str(score_data['player_details_list'][player_index]['gross_score'])}/{str(score_data['player_details_list'][player_index]['net_score'])}   ",
                                         color=ft.colors.WHITE, weight='bold', size=12)

        # Wrap the table in an outer container
        scorecard_outer_container_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                            button_and_or_score,
                            ft.Icon(name=ft.icons.EMOJI_EVENTS, color=ft.colors.WHITE, size=14),
                            ft.Text(f"{str(score_data['player_details_list'][player_index]['target_score'])}/{str(shots_remaining_to_target)}", color=ft.colors.WHITE, size=12),
                            ],
                            spacing=5
                        ),
                        padding=10,
                        bgcolor=ft.colors.PURPLE,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10),
                        width=210,
                        height=38
                    ),
                    ft.Container(
                       content=table,
                        width=300,
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
            padding=2,
            alignment=ft.alignment.top_left,
        )
        scorecard_outer_container.content = scorecard_outer_container_content
        page.update()

        ### End of Functions for Player Scorecard ###

    def reload_data(e) -> None:
        # print("Reload data")
        url = 'http://127.0.0.1:8000/api/getscoredetails/13/?format=json'
        url = f'https://kenton.eu.pythonanywhere.com/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json'
        global score_data
        score_data = get_api_data(url)
        update_data_table(0)
        global container_focus
        update_data_table(int(container_focus))
        page.update()
        return

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(leading=ft.Icon(ft.icons.GOLF_COURSE), title=ft.Text("Scorecard List"), bgcolor=ft.colors.GREY_100, toolbar_height=40, center_title = True),
                    ft.ListView([create_list_item(menuitem) for menuitem in menuitems], expand=True)
                ],
                bgcolor=ft.colors.GREEN
            )
        )
        
        if page.route == "/scorecard":
            url = f'http://127.0.0.1:8000/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json' # 4 ball
            url = f'https://kenton.eu.pythonanywhere.com/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json'
            global score_data
            score_data = get_api_data(url)
            # print(score_data["course_name"], score_data["group_name"], score_data["date"], score_data["no_of_players"])
            header = header_text(score_data["course_name"], score_data["group_name"], score_data["date"])
            global player_select_containers
            player_select_containers = [player_select_container(i, score_data) for i in range(score_data["no_of_players"])]
            for container in player_select_containers:
                container.on_click = container_click
            # Set initial container to highlight colour
            player_select_containers[0].bgcolor = highlight_color
            player_select_stack_animation = player_select_stack(player_select_containers, score_data )
            
            # Create a Row to hold the containers
            row = ft.Row(spacing=5)

            # Create a Column to hold the row and the DataTable
            scorecard_column = ft.Column(spacing=10)
            scorecard_column.controls.append(row)

            scorecard_column.controls.append(scorecard_outer_container)

            update_data_table(0)
            
            page.views.append(
                ft.View(
                    "/scorecard",
                        [
                        ft.AppBar(title=ft.TextButton("Scorecard", style=ft.ButtonStyle(color=ft.colors.BLACK), scale = 1.2,  icon="refresh", icon_color="BLACK", on_click=reload_data), color="BLACK", bgcolor=ft.colors.GREY_100, toolbar_height=40, center_title = True),
                        header,
                        player_select_stack_animation,
                        scorecard_column,
                    ],
                    bgcolor=ft.colors.GREEN,
                    padding = 5,
                    scroll=ft.ScrollMode.AUTO
                    
                )
            )

        elif page.route == "/add_score":

            def update_score_data(e):
                    # This function will be called when the "Update" button is clicked
                    # You can implement your update logic here, such as processing the entered numbers
                    for field in number_fields:
                        if field.value == "":  # If any field is blank exit function
                            # print("Blank Field - Exit function")
                            return
                        # print(field.value)  # Example: Print the entered values

                    score_data_string = f"{str(number_fields[0].value)}/{str(number_fields[1].value)}/"      ## Player 1&2 scores
                    score_data_string = score_data_string + f"{str(number_fields[2].value)}/" if score_data["no_of_players"] > 2 else score_data_string + "0/"  # Player 3 score
                    score_data_string = score_data_string + f"{str(number_fields[3].value)}/" if score_data["no_of_players"] > 3 else score_data_string + "0/"  # Player 4 score
                    
                    url = f"http://127.0.0.1:8000/api/updatescore/{str(score_data['score_id'])}/{str(hole_no_to_update)}/{score_data_string}"
                    url = f"https://kenton.eu.pythonanywhere.com/api/updatescore/{str(score_data['score_id'])}/{str(hole_no_to_update)}/{score_data_string}"
                    # print(url)
                    response = requests.get(url)
                    if response.status_code == 200:
                        response_confirmation = response.json()
                        print(response_confirmation)
                        show_scorecard_details(MenuItem("",score_data['score_id']))

            
            no_of_players = score_data["no_of_players"]  # Adjust this value to set the desired number of players
            hole_no_to_update = score_data["current_hole_recorded"] + 1

            # Create a list to store the number input fields
            number_fields = []

            # Create a container to hold the number input fields
            enter_score_container = ft.Container(
                bgcolor="GREEN",
                content=ft.Column(controls=[
                    ft.Text(f"Enter Scores for Hole No. {str(hole_no_to_update)}:", color=ft.colors.WHITE, weight="bold")
                ])
            )

            # Dynamically create number input fields based on the number of players
            for i in range(no_of_players):
                player_label = ft.Text(f"{score_data['player_details_list'][i]['firstname']}:", color=ft.colors.WHITE, weight="bold")
                
                # number_input = ft.TextField(label="Number", type=ft.TextFieldType.number)
                number_input = ft.TextField(
                    label="Enter Gross Score",
                    keyboard_type=ft.KeyboardType.NUMBER,  # Set keyboard type to number
                    width=200,
                    color=ft.colors.WHITE,
                    input_filter=ft.NumbersOnlyInputFilter(), 
                    border_color=ft.colors.WHITE
                )
                number_fields.append(number_input)
                enter_score_container.content.controls.extend([player_label, number_input])

                # Create an "Update" button 
                update_button = ft.ElevatedButton(text="Update Score", on_click=update_score_data)

            #page.add(container)
            page.views.append(
                ft.View(
                    "/add_score",
                    [
                        ft.AppBar(title=ft.Text("Player Scores"), color="BLACK", bgcolor=ft.colors.GREY_100, toolbar_height=40, center_title = True),
                        
                        enter_score_container, 
                        update_button
                    ],
                    bgcolor=ft.colors.GREEN,
                    padding = 5,
                    scroll=ft.ScrollMode.AUTO
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def create_list_item(MenuItem):
        return ft.Container(
            content=ft.Column([
                ft.Text(MenuItem.display, size=14, weight="bold", color=ft.colors.WHITE), 
                # ft.Text(item.description, size=16)  # Set custom text size for item description
            ]),
            on_click=lambda _: show_scorecard_details(MenuItem),
            padding=15,
            bgcolor=ft.colors.GREEN,
            border_radius=5
        )

    def show_scorecard_details(MenuItem):
        page.client_storage.set("current_scorecard_id", MenuItem.scorecard_id)
        page.go("/scorecard")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)