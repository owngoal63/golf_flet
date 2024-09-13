import flet as ft

def main(page: ft.Page):
    def text_clicked(e):
        print("Text clicked!")
        page.add(ft.Text("You clicked the text!"))
        page.update()

    clickable_text = ft.GestureDetector(
        content=ft.Text(
            "Click this text!",
            size=20,
            color=ft.colors.BLUE,
            weight=ft.FontWeight.BOLD
        ),
        on_tap=text_clicked
    )

    page.add(clickable_text)

ft.app(target=main)