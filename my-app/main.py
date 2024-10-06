import flet as ft
import requests
import datetime
import os
import asyncio

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
# default_bgcolor = ft.colors.GREEN_300
default_bgcolor = "#E9E9E9"
highlight_color = ft.colors.PURPLE
primary_text_color = ft.colors.TEAL_900
app_bar_color = ft.colors.GREEN_500
# url = f'{url_prefix}/api/getscorecardheaders/'

class MenuItem:
    def __init__(self, display, menuitem_id):
        self.display = display
        self.menuitem_id = menuitem_id

# menuitems = []

def quit_app(_):
    os._exit(0)

def extract_email_prefix(email: str) -> str:
    # Find the position of the '@' character
    at_index = email.find('@')
    
    if at_index != -1 and at_index + 1 < len(email):
        # Return everything up to and including '@' plus the first character after it
        return email[:at_index + 3] + "..."  # Slice the string up to @ and the first 2 chars after and add dots
    return email  # In case '@' is not found, return the original string


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

async def main(page: ft.Page):

    global score_data
    global player_select_containers

    page.title = "Handy Scorecard App"

    # Function to save to storage
    async def save_to_storage(key, value):
        await page.client_storage.set_async(key, str(value))

    # Function to retrieve from storage
    async def retrieve_from_storage(key, default=0):
        value_str = await page.client_storage.get_async(key)
        return int(value_str) if value_str is not None else default
    
    # await save_to_storage("my_number", 42)
    retrieved_value = await retrieve_from_storage("my_number")

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
                    ft.Text(self.course_name, size=16, weight='bold', color=primary_text_color, font_family="San Francisco"),
                    ft.Text(f"{self.group_name} ({self.date})", size=14, weight='bold', color=primary_text_color, font_family="San Francisco")
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

        def retrieve_from_storage(key, default=0):
            value_str = page.client_storage.get(key)
            return int(value_str) if value_str is not None else default
        
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

        my_id = retrieve_from_storage("my_id")
        # Divert to add_score only if Admin is in position 0 and has been clicked in this position
        if clicked_index == 0 and clicked_container.data == 0 and score_data["admin_id"] == my_id and score_data["current_hole_recorded"] <= 17:
            page.go("/add_score")
        else:
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
                weight=ft.FontWeight.BOLD,
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

        # Function to retrieve key value from local storage
        def retrieve_from_storage(key, default=0):
            value_str = page.client_storage.get(key)
            return int(value_str) if value_str is not None else default

        page.views.clear()
        my_id = retrieve_from_storage("my_id")      # Get the key value of the player_id if set (zero if not)
        # print(my_id)
        menuitems = []
        if my_id == 0:       # storage variable has not yet been set
            url = f'{url_prefix}/api/getscorecardheadersextended/'  # No filter on Scorecard list
        else:
            url = f'{url_prefix}/api/getscorecardheadersextended/?player_id={my_id}'    # Filter by player set in storage variable
        scorecards_data = get_api_data(url)
        for scorcard_header_data in scorecards_data:
            menuitems.append(MenuItem(f'{convert_date_format(scorcard_header_data["date"])}, {scorcard_header_data["course_name"]} {scorcard_header_data["name"]}', str(scorcard_header_data["id"])))
        page.views.append(
            ft.View(
                "/",
                [
                ft.AppBar(
                    leading=ft.IconButton(ft.icons.PERSON, on_click=lambda _: page.go("/get_users")),
                    title=ft.Text("Scorecards", style=ft.TextStyle(size=16, color=primary_text_color, font_family="San Francisco")),
                    bgcolor=app_bar_color,
                    toolbar_height=40,
                    center_title=True,
                    actions=[
                        ft.IconButton(ft.icons.ADD, on_click=lambda _: page.go("/add_scorecard"))
                    ]
                ),      
                ft.Container(
                    content = ft.ListView(
                        [
                            ft.Column([
                                create_list_item(menuitem, "Scorecard"),
                                ft.Divider(color=ft.colors.OUTLINE, thickness=1)
                            ])
                            for menuitem in menuitems[:-1]
                        ] + [create_list_item(menuitems[-1], "Scorecard")],  # Last item without divider
                        expand=True
                    ),
                    border=ft.border.all(2, ft.colors.PURPLE),
                        border_radius=10,
                        padding=10,
                        expand=True,
                        bgcolor=ft.colors.BLUE_GREY_50,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLUE_GREY_300,
                            offset=ft.Offset(0, 5),
                        )
                    )
                ],
                bgcolor=default_bgcolor,
            )
        )
        
        if page.route == "/scorecard":
            url = f'{url_prefix}/api/getscoredetails/{page.client_storage.get("current_scorecard_id")}/?format=json' # 4 ball
            global score_data
            score_data = get_api_data(url)
            header = header_text(score_data["course_name"], score_data["name"], convert_date_format(score_data["date"]))
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
                        ft.AppBar(title=ft.TextButton("Scorecard", style=ft.ButtonStyle(color=primary_text_color), scale = 1.1,  icon="refresh", icon_color=primary_text_color, on_click=reload_data), color="BLACK", bgcolor=app_bar_color, toolbar_height=40, center_title = True),
                        header,
                        player_select_stack_animation,
                        scorecard_column,
                    ],
                    bgcolor=default_bgcolor,
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
                bgcolor=ft.colors.BLUE_GREY_50,
                content=ft.Column(controls=[
                    ft.Text(f"Enter Scores for Hole No. {str(hole_no_to_update)}:", weight="bold", color=primary_text_color, font_family="San Francisco")
                ])
            )

            # Dynamically create number input fields based on the number of players
            for i in range(no_of_players):
                player_label = ft.Text(f"{score_data['player_details_list'][i]['firstname']}:", weight="bold", color=primary_text_color, font_family="San Francisco")
                
                number_input = ft.TextField(
                    label="Enter Gross Score",
                    keyboard_type=ft.KeyboardType.NUMBER,  # Set keyboard type to number
                    width=200,
                    color=primary_text_color,
                    input_filter=ft.NumbersOnlyInputFilter(), 
                    border_color=primary_text_color,
                    focused_border_color=ft.colors.PURPLE
                )
                number_fields.append(number_input)
                enter_score_container.content.controls.extend([player_label, number_input])

                # "Update Score" button 
                update_button = ft.ElevatedButton(text="Update Score", on_click=update_score_data)

            page.views.append(
                ft.View(
                    "/add_score",
                    [
                        ft.AppBar(
                            title=ft.Text("Player Scores", style=ft.TextStyle(size=16, color=primary_text_color, font_family="San Francisco")),
                            bgcolor=app_bar_color,
                            toolbar_height=40,
                            center_title=True
                        ),
                        ft.Container(
                            content=ft.Column([
                                enter_score_container,
                                update_button
                            ]),
                            border=ft.border.all(2, ft.colors.PURPLE),
                            border_radius=10,
                            padding=10,
                            expand=True,
                            bgcolor=ft.colors.BLUE_GREY_50,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=10,
                                color=ft.colors.BLUE_GREY_300,
                                offset=ft.Offset(0, 5),
                            )
                        )
                    ],
                    bgcolor=default_bgcolor,
                    padding=5,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        elif page.route == "/add_scorecard":

            def display_add_group_button(condition):
                if condition:
                    return [ft.IconButton(ft.icons.ADD, on_click=lambda _: page.go("/create_group"))]
                else:
                    return []
                
            group_menuitems = []
            url = f'{url_prefix}/api/getgroups/'
            groups = get_api_data(url)
            for group in groups:
                group_menuitems.append(MenuItem(f'{group["group_name"]}', str(group["id"])))

            # Sort the menu_items by their index
            group_menuitems.sort(key=lambda x: int(x.menuitem_id), reverse=True)

            page.views.append(
                ft.View(
                    "/add_scorecard",
                        [
                        ft.AppBar(
                            title=ft.Text("Select Group for Scorecard", style=ft.TextStyle(size=16,  color=primary_text_color, font_family="San Francisco")),
                            color=primary_text_color,
                            bgcolor=app_bar_color,
                            toolbar_height=40,
                            center_title = True,
                            actions = display_add_group_button(my_id != 0)
                        ),
                        ft.Container(
                            content = ft.ListView(
                                [
                                    ft.Column([
                                        create_list_item(group_menuitem, "GolfGroup"),
                                        ft.Divider(color=ft.colors.OUTLINE, thickness=1)
                                    ])
                                    for group_menuitem in group_menuitems[:-1]
                                ] + [create_list_item(group_menuitems[-1], "GolfGroup")],  # Last item without divider
                                expand=True
                            ),
                            border=ft.border.all(2, ft.colors.PURPLE),
                                border_radius=10,
                                padding=10,
                                expand=True,
                                bgcolor=ft.colors.BLUE_GREY_50,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=10,
                                    color=ft.colors.BLUE_GREY_300,
                                    offset=ft.Offset(0, 5),
                                )
                            )
                    ],
                    bgcolor=default_bgcolor,
                    padding = 5,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        elif page.route == "/initialise_scorecard":

            selected_id = 0

            def create_scorecard(e):
                # print("Create Scorecard")
                # http://127.0.0.1:8000/api/createscorecard/8/3/3/6/26/7/27/8/28/0/0/scorecardname/

                player_details_string = ""

                for i, field in enumerate(number_fields):
                    if field.value == "":  # If any field is blank exit function
                        return
                    # print(f"player {i} hcp", number_fields[i].value, buddys[i]['firstname'], buddys[i]['user_id'])
                    player_details_string = player_details_string + f"{str(buddys[i]['user_id'])}/{str(number_fields[i].value)}/"

                if no_of_players == 2: player_details_string = player_details_string + "0/0/0/0/"    # Add 2 blank player details
                if no_of_players == 3: player_details_string = player_details_string + "0/0/"       # Add 1 blank player details

                if not courses_dropdown.value:  # If dropdown field is blank exit function
                    return
                
                scorecardname = scorecard_name_input.value      # Get the Scoredard name
                
                # print("Course id", courses_dropdown.value)
                # print("Group id", page.client_storage.get("group_id"))
                url = f"{url_prefix}/api/createscorecard/{str(page.client_storage.get('group_id'))}/{str(courses_dropdown.value)}/{str(no_of_players)}/{player_details_string}{scorecardname}/"
                # print(url)
                response = requests.get(url)
                # if response.status_code == 200:
                response_confirmation = response.json()
                # print(response_confirmation)
                # print(response_confirmation["id"])
                # return
                show_scorecard_details(MenuItem("",int(response_confirmation["id"])))   # Goto Show Scorecard Page with newely created id


            group_menuitems = []
            # Get buddys for selected group
            url = f'{url_prefix}/api/getbuddys/{page.client_storage.get("group_id")}/'
            buddys = get_api_data(url)
            # for buddy in buddys:
            #     # group_menuitems.append(MenuItem(f'{group["group_name"]} ({group["id"]})', str(group["id"])))
            #     print(buddy)
            no_of_players =  len(buddys)

            # Create scorecard name input field
            scorecard_name_input = ft.TextField(
                label="Scorecard Name (optional)",
                value=f'{buddys[0]["group_name"]}',
                border_color=primary_text_color,
                focused_border_color=ft.colors.PURPLE,
                border_radius=10,
            )

            # Get Courses from API
            url = f'{url_prefix}/api/courses/'
            courses = get_api_data(url)
            options = []
            for course in courses:
                # print(course["name"])
                options.append(ft.dropdown.Option(text=course["name"], key=course["id"]))

            def dropdown_changed(e):
                selected_id = courses_dropdown.value
                return
            

            # Create a dropdown field using the options
            courses_dropdown = ft.Dropdown(
                label="Select Course",
                options=options,
                border_color=primary_text_color,
                padding=5,
                focused_border_color=ft.colors.PURPLE,
                border_radius=10,
                autofocus=True,
                on_change=dropdown_changed
            )

            # Create a list to store the number input fields
            number_fields = []

            # Create a list to store the players handicap from the API
            player_hcps = []
            for i in range(no_of_players):
                url = f'{url_prefix}/api/getcurrenthandicap/{buddys[i]["user_id"]}/'
                player_hcp = get_api_data(url)
                player_hcps.append(player_hcp["hcp_num"])
            # print(player_hcps)    


            # Create a container to hold the number input fields
            enter_handicap_container = ft.Container(
                bgcolor=ft.colors.BLUE_GREY_50,
                padding=10,
                content=ft.Column(controls=[
                    ft.Text(f"Course Handicaps for players:", weight="bold", color=primary_text_color, font_family="San Francisco")
                ])
            )

            for i in range(no_of_players):
                player_label = ft.Text(f"{buddys[i]['firstname']} (HCP {player_hcps[i]}):", weight="bold", color=primary_text_color, font_family="San Francisco")
                
                number_input = ft.TextField(
                    label="Enter Course Handicap",
                    keyboard_type=ft.KeyboardType.NUMBER,  # Set keyboard type to number
                    width=200,
                    color=primary_text_color,
                    input_filter=ft.NumbersOnlyInputFilter(), 
                    border_color=primary_text_color,
                    focused_border_color=ft.colors.PURPLE,
                )
                number_fields.append(number_input)
                enter_handicap_container.content.controls.extend([player_label, number_input])

                # "Create Scorecard" button 
                create_button = ft.ElevatedButton(text="Create Scorecard", on_click=create_scorecard)

            page.views.append(
                ft.View(
                    "/initialise_scorecard",
                    [
                        ft.AppBar(
                            title=ft.Text("Enter Course & Player Details", style=ft.TextStyle(size=16, color=primary_text_color, font_family="San Francisco")),
                            bgcolor=app_bar_color,
                            toolbar_height=40,
                            center_title=True
                        ),
                        ft.Container(
                            content=ft.Column([
                                scorecard_name_input,
                                courses_dropdown,
                                enter_handicap_container,
                                create_button
                            ]),
                            border=ft.border.all(2, ft.colors.PURPLE),
                            border_radius=10,
                            padding=10,
                            expand=True,
                            bgcolor=ft.colors.BLUE_GREY_50,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=10,
                                color=ft.colors.BLUE_GREY_300,
                                offset=ft.Offset(0, 5),
                            )
                        )
                    ],
                    bgcolor=default_bgcolor,
                    padding=5,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        elif page.route == "/get_users":
            user_menuitems = []
            user_menuitems.append(MenuItem("Show All Players", str(0)))    # First option is to show all players ( id = 0 )
            url = f'{url_prefix}/api/getusers/'
            users = get_api_data(url)
            for user in users:
                user_menuitems.append(MenuItem(f'{user["firstname"]}, {extract_email_prefix(user["email"])}' , str(user["id"])))
                # print(f'{user["firstname"]}, {user["email"]}')
            page.views.append(
            ft.View(
                "/get_users",
                [
                    ft.AppBar(
                        title=ft.Text("Select your profile from list", 
                                    style=ft.TextStyle(size=16, color=primary_text_color, font_family="San Francisco")),
                        color=primary_text_color,
                        bgcolor=app_bar_color,
                        toolbar_height=40,
                        center_title=True
                    ),
                    ft.Container(
                        content=ft.ListView(
                            [
                                ft.Column([
                                    create_list_item(user_menuitem, "User"),
                                    ft.Divider(color=ft.colors.OUTLINE, thickness=1)
                                ])
                                for user_menuitem in user_menuitems[:-1]
                            ] + [create_list_item(user_menuitems[-1], "User")],  # Last item without divider
                            expand=True,
                        ),
                        border=ft.border.all(2, ft.colors.PURPLE),
                        border_radius=10,
                        padding=10,
                        expand=True,
                        bgcolor=ft.colors.BLUE_GREY_50,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLUE_GREY_300,
                            offset=ft.Offset(0, 5),
                        )
                    )
                ],
                bgcolor=default_bgcolor,
            )
        )
            
        elif page.route == "/create_group":

            user_checkbox_items = []
            url = f'{url_prefix}/api/getusers/'
            users = get_api_data(url)
            for user in users:
                if user["id"] != my_id: user_checkbox_items.append(MenuItem(f'{user["firstname"]}, {user["email"]}' , str(user["id"])))
                if user["id"] == my_id: 
                    user_checkbox_items.insert(0, MenuItem(f'{user["firstname"]}, {user["email"]}' , str(user["id"])))
                    admin_firstname = user["firstname"]
                    admin_id = user["id"]

            print()
            for user in user_checkbox_items:
                print(user.display,user.menuitem_id)

            # List to store checkbox references
            checkboxes = []

            # TextField to display checked items
            checked_items_text = ft.TextField(label="Group Name", read_only=True)

            # Function to create a new checkbox
            def create_checkbox(label, value, disabled=False, checked=False):
                return ft.Checkbox(label=label, value=checked, data=value, disabled=disabled, on_change=on_checkbox_change)

            # Function to update the checked items TextField
            def update_checked_items_text():
                checked = [cb.label.split(",")[0] for cb in checkboxes[1:] if cb.value]  # Exclude Admin ( my_id ) from this list
                if len(checked) == 0:
                    checked_items_text.value = admin_firstname
                elif len(checked) == 1:
                    checked_items_text.value = f"{admin_firstname} & {checked[0]}"
                elif len(checked) == 2:
                    checked_items_text.value = f"{admin_firstname}, {checked[0]} & {checked[1]}"
                else:
                    checked_items_text.value = f"{admin_firstname}, {', '.join(checked[:-1])} & {checked[-1]}"
                page.update()

            # Function to handle checkbox changes
            def on_checkbox_change(e):
                if e.control != checkboxes[0]:  # Ignore changes to the Grape checkbox
                    checked_count = sum(1 for cb in checkboxes[1:] if cb.value)  # Count only editable checkboxes
                    if checked_count > 3:
                        e.control.value = False
                        result.value = f"You can only select up to 3 players (excluding {admin_firstname})."
                    else:
                        result.value = f"No. of players selected for group: {checked_count + 1}"
                    update_checked_items_text()
                    get_checked_button.disabled = checked_count == 0
                    page.update()

            # Function to initialize checkboxes
            def initialize_checkboxes():
                # Add Admin (my_id) as the first, pre-checked, non-editable checkbox
                admin_checkbox = create_checkbox(user_checkbox_items[0].display, user_checkbox_items[0].menuitem_id, disabled=True, checked=True)
                checkboxes.append(admin_checkbox)
                items_container.controls.append(admin_checkbox)

                # Add the rest of the users
                for checkbox_item in user_checkbox_items[1:]:
                    checkbox = create_checkbox(extract_email_prefix(checkbox_item.display), checkbox_item.menuitem_id )
                    checkboxes.append(checkbox)
                    items_container.controls.append(checkbox)
                
                update_checked_items_text()
                page.update()

            # Function to get checked items
            def get_checked_items(e):
                # checked = [(cb.label, cb.data) for cb in checkboxes if cb.value]
                # result.value = f"Checked items: {', '.join([f'{item[0]} ({item[1]})' for item in checked])}"
                # Create Group through API
                url = f"{url_prefix}/api/creategolfgroup/{str(checked_items_text.value)}/{str(admin_id)}/"
                print(url)
                # Temp disable
                response = requests.post(url)
                if response.status_code == 201:
                    response_confirmation = response.json()
                new_group_id = response_confirmation.get('id')
                # print("id of newly created group", new_group_id)
                buddy_ids = [cb.data for cb in checkboxes if cb.value]
                # print(buddy_ids)
                for buddy_id in buddy_ids:
                    url = f"{url_prefix}/api/createbuddy/{str(buddy_id)}/{str(new_group_id)}/"
                    # print("buddy url", url)
                    response = requests.post(url)
                    if response.status_code == 201:
                        response_confirmation = response.json()
                        # print(response_confirmation)
                display_popup_dialog(f"The group {str(checked_items_text.value)} has been created.")
                # page.update()

             # Container for checkboxes
            items_container = ft.Column()

            # Button to get checked items
            get_checked_button = ft.ElevatedButton("Create Buddy Group", on_click=get_checked_items, disabled=False)

            # Text area to display result
            result = ft.Text()

            # Initialize checkboxes
            initialize_checkboxes()


            page.views.append(
            ft.View(
                "/create_group",
                [
                    ft.AppBar(
                        title=ft.Text("Create Group from these Profiles", 
                                    style=ft.TextStyle(size=16, color=primary_text_color, font_family="San Francisco")),
                        color=primary_text_color,
                        bgcolor=app_bar_color,
                        toolbar_height=40,
                        center_title=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            items_container,
                            checked_items_text,
                            get_checked_button,
                            result
                        ]),
                         border=ft.border.all(2, ft.colors.PURPLE),
                        border_radius=10,
                        padding=10,
                        expand=True,
                        bgcolor=ft.colors.BLUE_GREY_50,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLUE_GREY_300,
                            offset=ft.Offset(0, 5),
                        )

                    )
                ]
            )
        )


        
        page.update()
        

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def display_popup_dialog(pre_text:str, parameter_str:str = "", post_text:str = ""):

        def save_to_storage(key, value):
            page.client_storage.set(key, str(value))

        def close_dlg(e):
            if parameter_str != "" and int(parameter_str) >= 0:  # Check if the parameter string is valid for save to storage
                save_to_storage("my_id", int(parameter_str))
            dlg.open = False
            page.update()

        def open_dlg():
            page.dialog = dlg
            dlg.open = True
            page.update()

        def navigate_to_root(e):
            close_dlg(e)
            page.go("/")

        dlg = ft.AlertDialog(
            title=ft.Text(pre_text),
            content=ft.ElevatedButton("OK", on_click=navigate_to_root),
            on_dismiss=close_dlg,
        )

        open_dlg()

        return

    def create_list_item(MenuItem, ItemType):
        if ItemType == "Scorecard":
            return ft.Container(
                content=ft.Column([
                    ft.Text(MenuItem.display, size=14, color=primary_text_color, font_family="San Francisco"), 
                ]),
                on_click=lambda _: show_scorecard_details(MenuItem),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_50,
                border_radius=5
            )
        elif ItemType == "GolfGroup":   # Item Type is Golfgroup
            return ft.Container(
                content=ft.Column([
                    ft.Text(MenuItem.display, size=14, color=primary_text_color, font_family="San Francisco"), 
                ]),
                on_click=lambda _: add_scorecard(MenuItem),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_50,
                border_radius=5
            )
        else:   # Item Type is User
            # print("user")
            return ft.Container(
                content=ft.Column([
                    ft.Text(MenuItem.display, size=14, color=primary_text_color, font_family="San Francisco"), 
                ]),
                on_click=lambda _: display_popup_dialog("Your profile is now set on this device", str(MenuItem.menuitem_id),""),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_50,
                border_radius=5
            )

    def show_scorecard_details(MenuItem):
        page.client_storage.set("current_scorecard_id", MenuItem.menuitem_id)
        page.go("/scorecard")

    def add_scorecard(MenuItem):
        page.client_storage.set("group_id", MenuItem.menuitem_id)
        page.go("/initialise_scorecard")


    splash_screen = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.GOLF_COURSE, color=ft.colors.GREEN_400, size=150),
                ft.Text(
                    "Handicappy Mobile",
                    size=20,
                    weight='bold',
                    color=ft.colors.GREEN_400,
                    font_family="San Francisco"
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True
    )

        # Add the splash screen to the page
    page.add(splash_screen)
    await page.update_async()

    # Wait for 2 seconds
    await asyncio.sleep(3)

    # Remove the splash screen 
    page.controls.clear()
    
    # Go to "/" root page
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)