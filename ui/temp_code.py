from time import sleep
import flet as ft


def main(page: ft.Page):
    def button_click(e):
        page.splash = ft.ProgressBar()
        btn.disabled = True
        page.update()
        sleep(3)
        page.splash = None
        btn.disabled = False
        page.update()

    btn = ft.ElevatedButton("Do some lengthy task!", on_click=button_click)
    page.add(btn)


ft.app(target=main)
