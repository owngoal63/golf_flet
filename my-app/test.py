import flet as ft

class Item:
    def __init__(self, name, description, additional_info):
        self.name = name
        self.description = description
        self.additional_info = additional_info

items = [
    Item("Item 1", "This is the description for Item 1", "Additional info for Item 1"),
    Item("Item 2", "This is the description for Item 2", "Additional info for Item 2"),
    Item("Item 3", "This is the description for Item 3", "Additional info for Item 3"),
]

def main(page: ft.Page):
    page.title = "Three-Page Flet App"

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Item List"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ListView([create_list_item(item) for item in items])
                ]
            )
        )
        
        if page.route == "/item":
            page.views.append(
                ft.View(
                    "/item",
                    [
                        ft.AppBar(title=ft.Text("Item Details"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Text(page.client_storage.get("current_item_description")),
                        ft.ElevatedButton("More Info", on_click=lambda _: page.go("/more_info"))
                    ]
                )
            )
        elif page.route == "/more_info":
            page.views.append(
                ft.View(
                    "/more_info",
                    [
                        ft.AppBar(title=ft.Text("Additional Information"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Text(page.client_storage.get("current_item_additional_info"))
                    ]
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def create_list_item(item):
        return ft.ListTile(
            title=ft.Text(item.name),
            on_click=lambda _: show_item_details(item)
        )

    def show_item_details(item):
        page.client_storage.set("current_item_description", item.description)
        page.client_storage.set("current_item_additional_info", item.additional_info)
        page.go("/item")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)