import flet as ft
import requests

# CReate a custom container as a subclass of container
# class CustomContainer(ft.Container):
#     def __init__(self, player_index, **kwargs):
#         super().__init__(**kwargs)
#         self.player_index = player_index

def main(page: ft.Page):
    # Default color for containers
    default_color = ft.colors.BLUE
    page.bgcolor = "GREEN"
    page.padding = 15

    # A list to hold the container objects
    containers = []

    global score_data
    global container_focus

    # URL
    url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/102/?format=json'

    # Placeholder for the DataTable
    data_table = ft.Column()

    # Placeholder for the player_id that has the current focus
    current_player_id = 0

    # Function to get the Golf API data
    def get_api_data(url: str):

        # sending a GET request to the API
        response = requests.get(url)

        if response.status_code == 200: # checking if the request was successful (HTTP status code 200)
            # parsing the JSON response data
            score_data = response.json()
            no_of_players = score_data["no_of_players"]
            course_name = score_data["course_name"]
            group_name = score_data["group_name"]
            # date = score_data["date"].datetime.strftime('%-d %b')
            date = score_data["date"]
        else:
            page.add(ft.SafeArea(ft.Text(f"Unable to retrieve URL:{url}")))

        return score_data  

    # Function to handle container clicks
    def on_container_click(e):
        # Reset all containers to the default color
        for container in containers:
            container.bgcolor = default_color

        # Change the clicked container's color
        clicked_container = e.control
        clicked_container.bgcolor = ft.colors.RED

        # Move the clicked container to the first position
        containers.remove(clicked_container)
        containers.insert(0, clicked_container)

        print("Container keys")
        for container in containers:
            print(container.key)
        global container_focus
        container_focus = containers[0].key
        print("container_focus", container_focus)

        # Rebuild the row with the updated order
        row.controls = containers

        # Update the DataTable with the clicked container's unique key
        update_data_table(int(e.control.key))
        print("container key", e.control.key)
        # print(containers)

        # Update the page to reflect changes
        page.update()

    def update_data_table(player_index):
        global score_data
        # Define the DataTable columns
        # columns = [
        #     ft.DataColumn(ft.Text(header_title)),
        #     ft.DataColumn(ft.Text("Title")),
        #     ft.DataColumn(ft.Text("Score")),
        # ]
        # print("scoredata update_data_table", score_data)
        # print("Player Index", player_index)
        print("score data score id update data table", score_data["score_id"])
        # print("player id of data table", score_data["player_details_list"][player_index]["firstname"], score_data["player_details_list"][player_index]["id"])
        columns=[
                ft.DataColumn(ft.Text("Hole", size=12, weight='bold', color='white'), numeric=True),
                ft.DataColumn(ft.Text("Par", size=12, weight='bold', color='white'), numeric=True),
                ft.DataColumn(ft.Text("SI", size=12, weight='bold', color='white'), numeric=True),
                ft.DataColumn(ft.Text("GRS", size=12, weight='bold', color='white'), numeric=True),
                ft.DataColumn(ft.Text("NET", size=12, weight='bold', color='white'), numeric=True),
                ]

        # Define the DataTable rows
        rows = []
        for i in range(0,18):
            rows.append(ft.DataRow(cells = [
                    ft.DataCell(ft.Text(i+1, size=12, color='black')),
                    ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["course_par_holes_list"][i], size=12, color='black')),
                    ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["course_si_holes_list"][i], size=12, color='black')),
                    ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["gross_score_holes_list"][i], size=12, color='black')),
                    ft.DataCell(ft.Text(score_data["player_details_list"][player_index]["net_score_holes_list"][i], size=12, color='black'))
                ]))

        # Create the DataTable
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

        # Clear previous content and add new DataTable
        data_table.controls.clear()
        data_table.controls.append(data_table_content)
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

    # Create multiple containers
    # print("here")
    score_data = get_api_data(url)
    # print(score_data)
    for i in range(score_data["no_of_players"]):
        container = ft.Container(
            border_radius=20,
            width=170,
            height=110,
            padding=15,
            bgcolor=default_color,
            alignment=ft.alignment.center,
            # content=ft.Text(f"Container {i+1}"),
            # content = ft.Text(score_data["player_details_list"][i]["firstname"]),
            content=ft.Column(
                    controls=[
                        ft.Text(value=f"{score_data['player_details_list'][i]['firstname']} ({score_data['player_details_list'][i]['gross_score']} vs {score_data['player_details_list'][i]['target_score']})", color="YELLOW"),
                        ft.Text(value=str(score_data['player_details_list'][i]['course_hcp']), color="WHITE"),
                        ft.Container(
                            width=160,
                            height=5,
                            bgcolor='WHITE',
                            border_radius=20,
                            padding=ft.padding.only(right=140-int(140*((score_data['player_details_list'][i]['gross_score']/score_data['player_details_list'][i]['target_score']))) ),     # 140 is max width
                            content=ft.Container(
                                bgcolor="PINK",
                            ),                 
                        )
                    ]
                ),


            key = str(i),
            on_click=on_container_click,
            #margin=5  # Adding margin for better visibility
        )
        containers.append(container)

    # Create a Row to hold the containers
    row = ft.Row(spacing=5)
    row.controls = containers

    # Create a Column to hold the row and the DataTable
    main_column = ft.Column(spacing=10)
    main_column.controls.append(row)
    main_column.controls.append(data_table)

    # Add the main column to the page
    page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))
    page.add(main_column)

# Run the app
ft.app(target=main)