import flet as ft
import time

def main(page: ft.Page):
    page.title = "Animated DataTable Example"

    # Create a DataTable
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Age")),
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("1")),
                ft.DataCell(ft.Text("Alice")),
                ft.DataCell(ft.Text("30")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("2")),
                ft.DataCell(ft.Text("Bob")),
                ft.DataCell(ft.Text("25")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("3")),
                ft.DataCell(ft.Text("Charlie")),
                ft.DataCell(ft.Text("35")),
            ]),
        ],
    )

    # Wrap the DataTable in a Container with Scale animation
    animated_table = ft.Container(
        bgcolor="red",
        content=data_table,
        scale=ft.transform.Scale(scale=0),
        animate_scale=ft.animation.Animation(1000, ft.AnimationCurve.BOUNCE_OUT),
    )

    def animate_table(e):
        animated_table.scale = ft.transform.Scale(scale=1)
        page.update()

    # Button to trigger animation
    show_button = ft.ElevatedButton("Show Table", on_click=animate_table)

    # Add components to the page
    page.add(show_button, animated_table)

ft.app(target=main)