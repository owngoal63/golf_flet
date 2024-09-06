import flet as ft
from flet_core.control_event import ControlEvent
import requests
from datetime import datetime

class State:
    toggle = True

s = State()

def main(page: ft.Page):


    # Initialise variables
    # API URL
    url = 'https://kenton.eu.pythonanywhere.com/api/getcurrenthandicap/1/?format=json'
    url = 'https://kenton.eu.pythonanywhere.com/api/gethistoricalhcp/1/?format=json'
    url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/102/?format=json'

    # Main Page variables
    BG = '#041955'
    page.bgcolor = "GREEN"
    page.padding = 15
    player_score_selected = 0

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
                    ft.Text(self.course_name, size=26, weight='bold'),
                    # ft.IconButton(ft.icons.REFRESH, on_click=reload_data),
                    ft.Text(f"{self.group_name} ({self.date})", size=16, weight='bold')
                    ]
                )
            )
    

    class PlayerHeaderCard(ft.UserControl):
        def __init__(self, name: str, hcp: float, gross: int, target: int, player_index: int) -> None:
            super().__init__()
            self.name = name
            self.gross = gross
            self.target = target
            self.hcp = hcp
            self.player_index = player_index


        def setplayer(self, e: ControlEvent) -> None:    # Called on long click of player's card
            global player_score_selected
            player_score_selected = self.player_index
            # print("player score selected", player_score_selected)
            # Remove the controls on the page
            page.controls.pop()
            page.controls.pop()
            # page.controls.pop()
            header_text(score_data["course_name"], score_data["group_name"], score_data["date"])
            # players_card_row = add_players_header_cards()
            # page.add(players_card_row)
            player_score_table = PlayerScoreTable(score_data, player_score_selected)
            page.add(player_score_table)
            # player_score_table(score_data, player_score_selected)
            # print("hello")
            # print("self.phc", self.__dict__)
            # print(self._Stack__controls[0].__dict__)
            # print(self._Stack__controls[0]._Row__controls[0].bgcolor)
            self._Stack__controls[0]._Row__controls[0].bgcolor = "RED"
            self.update()
            # print(self._Stack__controls[0]._Row__controls[0])
            page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))
            page.update()


        def build(self) -> ft.Row:
            # global player_score_selected
            # global player_score_selected
            print("player score selected", player_score_selected)
            print("self player index", self.player_index)
            if player_score_selected == self.player_index:
                BG_colour = "BLACK"
            else:
                BG_colour = BG
            print(self.player_index)
            phc = ft.Row(controls=[ft.Container(
                border_radius=20,
                bgcolor=BG_colour,
                width=170,
                height=110,
                padding=15,
                on_long_press=self.setplayer,
                content=ft.Column(
                    controls=[
                        ft.Text(value=f"{self.name} ({self.gross} vs {self.target})", color="YELLOW"),
                        ft.Text(value=str(self.hcp), color="WHITE"),
                        ft.Container(
                            width=160,
                            height=5,
                            bgcolor='WHITE',
                            border_radius=20,
                            padding=ft.padding.only(right=140-int(140*((self.gross/self.target))) ),     # 140 is max width
                            content=ft.Container(
                                bgcolor="PINK",
                            ),                 
                        )
                    ]
                )
            )
            ]
            )
            print("phc", phc.controls[0].bgcolor)   #
            return phc

    def add_players_header_cards(player_score_selected: int):        

        players_card_row = ft.Row(
            scroll='auto'
        )
        print("add players header card - player_score_selected", player_score_selected)

        for p in range(score_data["no_of_players"]):
            players_card_row.controls.append(
                PlayerHeaderCard(score_data["player_details_list"][p]["firstname"], 
                                score_data["player_details_list"][p]["course_hcp"],
                                score_data["player_details_list"][p]["gross_score"],
                                score_data["player_details_list"][p]["target_score"],
                                p
                                )

            )
        # print("players_card_row.controls[0]",players_card_row.controls[0])
        page.add(players_card_row)
        # print("players_card_row.__dict__",players_card_row.__dict__)
        # print("-------------------")
        # print("players_card_row.__dict__._Row__controls[0]",players_card_row._Row__controls[0].__dict__)
        # print("This is the one",players_card_row._Row__controls[0]._Stack__controls[0]._Row__controls[0].bgcolor)

        return players_card_row

    class PlayerScoreTable(ft.UserControl):
        def __init__(self, score_data, p:int) -> None:
            super().__init__()
            self.score_data = score_data
            self.p = p

    
        def score_table_rows(self) -> list:
            rows = []
            # print("p again is ",self.p)
            for i in range(0,18):
                rows.append(ft.DataRow(cells = [
                    ft.DataCell(ft.Text(i+1, size=12, color='white')),
                    ft.DataCell(ft.Text(self.score_data["player_details_list"][self.p]["course_par_holes_list"][i], size=12, color='white')),
                    ft.DataCell(ft.Text(self.score_data["player_details_list"][self.p]["course_si_holes_list"][i], size=12, color='white')),
                    ft.DataCell(ft.Text(self.score_data["player_details_list"][self.p]["gross_score_holes_list"][i], size=12, color='white')),
                    ft.DataCell(ft.Text(self.score_data["player_details_list"][self.p]["net_score_holes_list"][i], size=12, color='white'))
                ]))

            return rows


        def build(self) -> ft.DataTable:

            # print("p is ",self.p)
            # print("score data", self.score_data)
            
            return ft.DataTable(
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
                    columns=[
                        ft.DataColumn(ft.Text("Hole", size=12, weight='bold', color='white'), numeric=True),
                        ft.DataColumn(ft.Text("Par", size=12, weight='bold', color='white'), numeric=True),
                        ft.DataColumn(ft.Text("SI", size=12, weight='bold', color='white'), numeric=True),
                        ft.DataColumn(ft.Text("GRS", size=12, weight='bold', color='white'), numeric=True),
                        ft.DataColumn(ft.Text("NET", size=12, weight='bold', color='white'), numeric=True),
                    ],

                    rows = self.score_table_rows()
            )
            # page.add(score_table)
            # return
    
    def reload_data(e: ControlEvent) -> None:
        global player_score_selected
        print("clicked", player_score_selected)
        url = 'https://kenton.eu.pythonanywhere.com/api/getscoredetails/99/?format=json'
        score_data = get_api_data(url)
        page.controls.pop()
        page.controls.pop()
        page.controls.pop()
        # page.controls.pop()
        header_text(score_data["course_name"], score_data["group_name"], score_data["date"])
        players_card_row = add_players_header_cards()
        # player_score_table(score_data, player_score_selected)
        player_score_table = PlayerScoreTable(score_data, player_score_selected)
        page.add(player_score_table)
        page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))
        page.update()
        return

    
    score_data = get_api_data(url)
    header = header_text(score_data["course_name"], score_data["group_name"], score_data["date"])
    page.add(header)
    players_card_row = add_players_header_cards()
    # print(page)
    #player_score_table(score_data, player_score_selected)
    player_score_table = PlayerScoreTable(score_data, player_score_selected)
    page.add(player_score_table)
    page.add(ft.IconButton(ft.icons.REFRESH, on_click=reload_data))

ft.app(main)
