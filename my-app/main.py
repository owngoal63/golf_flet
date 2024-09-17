import flet as ft
import requests
import datetime
import os

### URL Prefix Setting for Production vs Test
runmode = "TEST"
# runmode = "PROD"
if runmode == "TEST":
    url_prefix = "http://127.0.0.1:8000"
else:
    url_prefix = "https://kenton.eu.pythonanywhere.com"


### App Variables ###
container_width = 90
container_height = 70
animation_duration = 300
default_color = '#041955'
highlight_color = ft.colors.PURPLE
url = f'{url_prefix}/api/getscorecardheaders/'


class MenuItem:
    def __init__(self, display, scorecard_id):
        self.display = display
        self.scorecard_id = scorecard_id

menuitems = []

def quit_app(_):
    os._exit(0)

def convert_date_format(date_str):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d-%b-%y")

### Matchplay Conversion Function ###
def matchplay_convert(number):
    if number == 0: return "AS"
    elif number > 0: return f"{str(number)}up"
    elif number < 0: return f"{str(number*-1)}dn"
    else: return ""


### Get API Data function ###
def get_api_data(url: str):
    response = requests.get(url)    # sending a GET request to the API
    if response.status_code == 200: # checking if the request was successful (HTTP status code 200)
        url_data = response.json()  # parsing the JSON response data
    # else:
    #     page.add(ft.SafeArea(ft.Text(f"Unable to retrieve URL:{url}")))

    return url_data
### End of Get API Data

scorecards_data = get_api_data(url)
for scorcard_header_data in scorecards_data:
    menuitems.append(MenuItem(f'{convert_date_format(scorcard_header_data["date"])} {scorcard_header_data["course"]} {scorcard_header_data["group"]} ({scorcard_header_data["id"]})', str(scorcard_header_data["id"])))


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
                content=ft.Column(
                    controls=[
                    ft.Text(self.course_name, size=16, weight='bold', color='WHITE'),
                    ft.Text(f"{self.group_name} ({self.date})", size=12, weight='bold', color='WHITE')
                    ]
                )
            )
    ### End of Header Text ###


    ### Functions for Player Select Controls ####
    def player_select_container(index, score_data):

        # Determine whether to display Course Handicap, Matchplay total or Stableford total in player_select_containers
        if score_data['current_hole_recorded'] == 0:    # Show Course Handicap value
            value_to_show = str(score_data['player_details_list'][index]['course_hcp'])
        elif score_data["no_of_players"] == 2:          # Show Matchplay score
            value_to_show = matchplay_convert(score_data[f'matchplay_status_player{str(index+1)}'])
        else:                                           # Show Stableford points
            value_to_show = f"{str(score_data['player_details_list'][index]['stableford_total'])}s"

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
                        value=f"{score_data['player_details_list'][index]['firstname'][:5]} {value_to_show}",
                        color="YELLOW",
                        text_align=ft.TextAlign.CENTER,
                        size = 12,
                        weight='bold',
                        width=container_width - 15,  # Subtract padding
                        data={f"app_identifier": f"{index}"}
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
        clicked_container.bgcolor = highlight_color     # Change color of clicked container
        player_select_containers.insert(0, player_select_containers.pop(clicked_index))     # Rearrange containers
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
        # Add out score totals
        data.insert(10, ["Out", str(score_data['player_details_list'][player_index]['out_par_total']), "", str(score_data['player_details_list'][player_index]['out_gross_score']), str(score_data['player_details_list'][player_index]['out_net_score'])])
        # Add in score totals
        data.insert(20, ["In", str(score_data['player_details_list'][player_index]['in_par_total']), "", str(score_data['player_details_list'][player_index]['in_gross_score']), str(score_data['player_details_list'][player_index]['in_net_score'])])
        # Add Overall Totals
        overall_par_total = score_data['player_details_list'][player_index]['out_par_total'] + score_data['player_details_list'][player_index]['in_par_total']
        if score_data["current_hole_recorded"] == 18:
            overall_gross_total = score_data['player_details_list'][player_index]['out_gross_score'] + score_data['player_details_list'][player_index]['in_gross_score']
            overall_net_total = score_data['player_details_list'][player_index]['out_net_score'] + score_data['player_details_list'][player_index]['in_net_score']
        else:
            overall_gross_total = '' 
            overall_net_total = ''
        # Insert Grand Totals to Bottom row if 18th hole has been recorded
        data.insert(21, ["Total", str(overall_par_total), "", str(overall_gross_total), str(overall_net_total)]) 

        current_hole_row = score_data["current_hole_recorded"] if score_data["current_hole_recorded"] <= 9 else score_data["current_hole_recorded"] + 1
        try:
            if int(score_data['player_details_list'][player_index]['target_score']) > 0:
                shots_remaining_to_target = -1 * (score_data['player_details_list'][player_index]['gross_score'] - score_data['player_details_list'][player_index]['target_score'])
            else:
                shots_remaining_to_target = ""
        except:
            shots_remaining_to_target = ""

        ## Create Cells on Scorecard Table
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

        # Define an "Enter Scores" button (gesture Text workaround ??) only if round is not complete and player_type is "Admin"
        if score_data["current_hole_recorded"] <= 17 and score_data['player_details_list'][player_index]['player_type'] == "Admin":
            button_and_or_score = ft.GestureDetector(
                content=ft.Text(f"{score_data['player_details_list'][player_index]['firstname'][:5]} {str(score_data['player_details_list'][player_index]['gross_score'])}/{str(score_data['player_details_list'][player_index]['net_score'])} {str(score_data['player_details_list'][player_index]['stableford_total'])}s",
                size=12,
                color=ft.colors.WHITE,
                weight=ft.FontWeight.BOLD
                ),
            on_tap=lambda _: page.go("/add_score")
            ) 
        else:     # Just show Score Text
            button_and_or_score = ft.Text(f"{score_data['player_details_list'][player_index]['firstname'][:5]} {str(score_data['player_details_list'][player_index]['gross_score'])}/{str(score_data['player_details_list'][player_index]['net_score'])} {str(score_data['player_details_list'][player_index]['stableford_total'])}s",
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
                        width=250,
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

    ### Reload latest data from API 
    def reload_data(e) -> None:
        url = f'{url_prefix}/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json'
        global score_data
        score_data = get_api_data(url)

        # Get app id of player currently in focus to pass a parameter to update_data_table
        app_id_of_player_in_focus = player_select_containers[0].content.controls[0].data.get("app_identifier")

        ## Update values in player select containers with refreshed data
        for player_select_container in player_select_containers:
            for i in range(0,score_data["no_of_players"]):
                if isinstance(player_select_container.content.controls[0], ft.Text) and player_select_container.content.controls[0].data.get(f"app_identifier") == f"{i}":

                    # Determine whether to display Course Handicap, Matchplay total or Stableford total in player_select_containers
                    if score_data['current_hole_recorded'] == 0:            # Show Course Handicap value
                        value_to_show = str(score_data['player_details_list'][i]['course_hcp'])
                    elif score_data["no_of_players"] == 2:                  # Show Matchplay score
                        value_to_show = matchplay_convert(score_data[f'matchplay_status_player{str(i+1)}'])
                    else:                                                   # Show Stableford points
                        value_to_show = f"{str(score_data['player_details_list'][i]['stableford_total'])}s"
                    
                    player_select_container.content.controls[0].value = f"{score_data['player_details_list'][i]['firstname'][:5]} {value_to_show}"
        
        # refresh the scorecard data table
        update_data_table(int(app_id_of_player_in_focus))
        page.update()
        return

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                ft.AppBar(
                    leading=ft.Icon(ft.icons.GOLF_COURSE),
                    title=ft.Text("Scorecard List"),
                    bgcolor=ft.colors.GREY_100,
                    toolbar_height=40,
                    center_title=True,
                    actions=[
                        ft.IconButton(ft.icons.ADD, on_click=lambda _: page.go("/add_scorecard"))
                    ]
        ),
                    ft.ListView([create_list_item(menuitem) for menuitem in menuitems], expand=True)
                ],
                bgcolor=ft.colors.GREEN
            )
        )
        
        if page.route == "/scorecard":
            url = f'{url_prefix}/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json' # 4 ball
            global score_data
            score_data = get_api_data(url)
            header = header_text(score_data["course_name"], score_data["group_name"], convert_date_format(score_data["date"]))
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

            ### Function to Update the match score
            def update_score_data(e):
                for field in number_fields:
                    if field.value == "":  # If any field is blank exit function
                        return

                score_data_string = f"{str(number_fields[0].value)}/{str(number_fields[1].value)}/"      ## Player 1&2 scores
                score_data_string = score_data_string + f"{str(number_fields[2].value)}/" if score_data["no_of_players"] > 2 else score_data_string + "0/"  # Player 3 score
                score_data_string = score_data_string + f"{str(number_fields[3].value)}/" if score_data["no_of_players"] > 3 else score_data_string + "0/"  # Player 4 score
                
                url = f"{url_prefix}/api/updatescore/{str(score_data['score_id'])}/{str(hole_no_to_update)}/{score_data_string}"
                response = requests.get(url)
                if response.status_code == 200:
                    response_confirmation = response.json()
                    show_scorecard_details(MenuItem("",score_data['score_id']))

            
            no_of_players = score_data["no_of_players"]
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

                # "Update Score" button 
                update_button = ft.ElevatedButton(text="Update Score", on_click=update_score_data)

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

        elif page.route == "/add_scorecard":
            print("Add Scorecard")

            page.views.append(
                ft.View(
                    "/add_scorecard",
                    [
                        ft.AppBar(title=ft.Text("Add Scoercard"), color="BLACK", bgcolor=ft.colors.GREY_100, toolbar_height=40, center_title = True),
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