import flet as ft

def main(page):
    # Create a dictionary to store containers with unique keys
    containers = {}


     # Create multiple containers
    for i in range(5):
        container = ft.Container(
            width=100,
            height=200,
            bgcolor="black",
            alignment=ft.alignment.center,
            content=ft.Text(f"Container {i+1}"),
            margin=5  # Adding margin for better visibility
        )
        containers[f"Container {i+1}"] = container

    # Create a Row to hold the containers
    row = ft.Row(spacing=5)
    for container in containers:
        print(containers[container])
        row.controls = [containers[container]]

    # Add the row to the page
    page.add(row)

# Run the app
# ft.app(target=main)

#     # Create a container and store it with a unique key
#     container = ft.Container(content=ft.Text("Hello, Flet!"))
#     containers["unique_container"] = container
#     page.add(container)

#     # Function to retrieve and update the container using its key
#     def update_container():
#         container_by_key = containers.get("unique_container")
#         if container_by_key:
#             container_by_key.content.value = "Updated text"
#             container_by_key.update()

#     # Add a button to trigger the update
#     update_button = ft.ElevatedButton(text="Update Container", on_click=lambda e: update_container())
#     page.add(update_button)

ft.app(target=main)