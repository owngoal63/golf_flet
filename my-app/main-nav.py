import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Dynamic Hyperlink Navigation Example"

    # Sample data - in a real app, this might come from a database
    items = [
        {"id": 1, "name": "Item One"},
        {"id": 2, "name": "Item Two"},
        {"id": 3, "name": "Item Three"},
        {"id": 4, "name": "Item Four"},
        {"id": 5, "name": "Item Five"},
    ]

    # URL
    url = 'https://kenton.eu.pythonanywhere.com/api/getscores/?format=json'

    # Function to get the API data
    def get_api_data(url: str):

        # sending a GET request to the API
        response = requests.get(url)

        if response.status_code == 200: # checking if the request was successful (HTTP status code 200)
            # parsing the JSON response data
            scores_data = response.json()
            # date = scores_data["date"]
            # course_name = scores_data[0]["course"]
            # # group_name = scores_data["group"]
            # print(course_name)
            # date = score_data["date"].datetime.strftime('%-d %b')
        else:
            page.add(ft.SafeArea(ft.Text(f"Unable to retrieve URL:{url}")))

        return scores_data 

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Item List"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Column([
                        ft.TextButton(
                            f"{score['date']} | {score['course']} | {score['group']}",
                            on_click=lambda _, id=score["id"]: page.go(f"/item/{id}")
                        ) for score in scores_data
                    ])
                ]
            )
        )

        if page.route.startswith("/item/"):
            item_id = int(page.route.split("/")[-1])
            item = next((item for item in items if item["id"] == item_id), None)
            
            if item:
                page.views.append(
                    ft.View(
                        page.route,
                        [
                            ft.AppBar(title=ft.Text(f"Item {item_id}"), bgcolor=ft.colors.SURFACE_VARIANT),
                            ft.Text(f"This is the details page for {item['name']} (ID: {item_id})"),
                            ft.ElevatedButton("Go back", on_click=lambda _: page.go("/")),
                        ]
                    )
                )
            else:
                page.views.append(
                    ft.View(
                        page.route,
                        [
                            ft.AppBar(title=ft.Text("Error"), bgcolor=ft.colors.SURFACE_VARIANT),
                            ft.Text(f"Item with ID {item_id} not found"),
                            ft.ElevatedButton("Go back", on_click=lambda _: page.go("/")),
                        ]
                    )
                )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    scores_data = get_api_data(url)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.WEB_BROWSER)