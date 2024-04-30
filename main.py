import flet as ft
import flet_material as fm
from database.db import (
    DatabaseManager,
    User,
    Group,
    Sending,
    Test,
    Task,
    Theme,
    UserGroup,
)
from database.config import uri
from ui.execute_code import execute_code


# from task import TaskPage
from datetime import datetime
import random
import asyncio
from re import match
from functools import partial
import time
import pyperclip

fm.Theme.set_theme("teal")
db_manager = DatabaseManager(uri)
username = ""
email = ""
role = ""
GROUPS_DATA = {}
TASKS_DATA = {}
THEMES_DATA = {}
SENDINGS_DATA = {}
tasks = {}
icon_btns = []
CURRENT_THEME_ID = None
CURRENT_GROUP_ID = None
CURRENT_USER_ID = None
TESTS_DATA = {}
func = None


def get_time():
    now = datetime.now()
    formatted_date = now.strftime("%H:%M %d.%m.%Y")
    return formatted_date


def copy_to_clipboard(text):
    pyperclip.copy(text)


def get_data():
    global password, TASKS_DATA, GROUPS_DATA, THEMES_DATA, CURRENT_GROUP_ID, CURRENT_THEME_ID, CURRENT_USER_ID, db_manager, TESTS_DATA
    db_manager = DatabaseManager(uri)
    THEMES_DATA = {}
    Users = (
        db_manager.session.query(User)
        .filter(User.email == email and User.password == password)
        .all()
    )
    user = Users[0]
    ID = user.ID

    GROUPS_ID = []

    for grp in db_manager.session.query(UserGroup):
        if grp.user_id == ID:
            GROUPS_ID.append(grp.group_id)

    for group in db_manager.session.query(Group).all():
        if group.ID in GROUPS_ID:
            GROUPS_DATA[group.ID] = {
                "leader_id": group.leader,
                "name": group.description.split("|")[0],
                "description": group.description.split("|")[1],
                "icon": group.description.split("|")[2],
            }

    themes = db_manager.session.query(Theme).all()

    for theme in themes:
        if str(theme.group_id) == str(CURRENT_GROUP_ID) or 0:
            THEMES_DATA[theme.ID] = {
                "description": theme.description + "| ",
                "color": theme.color,
            }

    tests = db_manager.session.query(Test).all()
    for test in tests:
        TESTS_DATA[test.ID] = {
            "task_id": test.task_id,
            "num": test.num,
            "input": test.input,
            "output": test.output,
        }

    tasks = db_manager.session.query(Task).all()

    TASKS_DATA = {}
    for task in tasks:
        if task.theme_id in THEMES_DATA:
            TASKS_DATA[task.ID] = {
                "description": task.description + "| ",
                "ID": task.ID,
                "theme_id": task.theme_id,
                "cost": task.cost,
                "accepted_tests": 0,
                "total_tests": 0,
            }
            sendings = db_manager.session.query(Sending).all()
            for send in sendings:
                if task.ID == send.task_id:

                    if send.author == CURRENT_USER_ID:
                        TASKS_DATA[task.ID]["total_tests"] = send.total_tests
                        TASKS_DATA[task.ID]["accepted_tests"] = max(
                            TASKS_DATA[task.ID]["accepted_tests"], send.accepted_tests
                        )

                        # if send.verdict == 'accepted':

    sendings = db_manager.session.query(Sending).all()
    for send in sendings:
        SENDINGS_DATA[send.ID] = send


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if match(pattern, email):
        return True

    return False


def random_cord() -> int:
    return random.randint(-100, 2000)


def random_color() -> str:
    colors: list = ["blue", "white"]
    return random.choice(colors)


def random_offset() -> int:
    return random.randint(1, 5)


def random_wait() -> int:
    return random.randrange(1500, 1700, 100)


def show_message(page, text, type="message", width=3):
    color = {
        "message": ft.colors.with_opacity(0.7, ft.colors.WHITE),
        "success": ft.colors.GREEN_400,
        "error": ft.colors.RED_400,
    }[type]
    page.snack_bar = ft.SnackBar(
        content=ft.Row(
            controls=[
                ft.Container(
                    expand=4,
                ),
                ft.Container(
                    alignment=ft.alignment.center,
                    expand=width,
                    height=50,
                    border_radius=10,
                    content=ft.Text(
                        text_align="center",
                        value=text,
                        font_family="Consolas",
                        size=18,
                        color=color,
                    ),
                    bgcolor="#2a3139",
                ),
                ft.Container(
                    expand=1,
                ),
                ft.Container(
                    expand=3,
                ),
            ]
        ),
        bgcolor="transparent",
        elevation=0,
    )

    page.snack_bar.open = True
    page.update()


class Thing(ft.Container):
    def __init__(self) -> None:
        color: str = random_color()
        super(Thing, self).__init__(
            left=random_cord(),
            top=random_cord(),
            width=2.5,
            height=2.5,
            shape=ft.BoxShape("circle"),
            bgcolor=color,
            opacity=0,
            offset=ft.transform.Offset(0, 0),
            shadow=ft.BoxShadow(
                spread_radius=20,
                blur_radius=100,
                color=color,
            ),
        )

        self.wait: int = random_wait()

        self.animate_opacity = ft.Animation(self.wait, "ease")
        self.animate_offset = ft.Animation(self.wait, "ease")

    async def animate_thing(self, event=None) -> None:
        self.opacity = 1
        self.offset = ft.transform.Offset(random_offset() ** 2, random_offset() ** 2)
        self.update()
        await asyncio.sleep(self.wait / 1000)
        self.opacity = 0
        self.offset = ft.transform.Offset(random_offset() ** 2, random_offset() ** 2)
        self.update()
        await asyncio.sleep(self.wait / 1000)

        await self.animate_thing()


input_style: dict = {
    "height": 38,
    "focused_border_color": "blue",
    "border_radius": 5,
    "cursor_height": 30,
    "cursor_color": "white",
    "content_padding": 10,
    "border_width": 1.5,
    "text_size": 18,
}


class Input(ft.TextField):
    def __init__(self, password: bool = False, label: str = "", email=False) -> None:
        super().__init__(
            **input_style,
            password=password,
            label=label,
            on_focus=self.to,
            on_blur=self.back,
            animate_size=ft.animation.Animation(
                400, ft.AnimationCurve.EASE_IN_OUT_BACK
            ),
        )
        self.email = email

    def to(self, e: ft.ControlEvent) -> None:
        self.height = 52
        if self.email:
            if not is_valid_email(self.value):
                self.border_color = "red"
            else:
                self.border_color = "blue"
        self.page.update()

    def back(self, e: ft.ControlEvent) -> None:
        self.height = 38
        # self.border_color = 'gray'
        if self.email:
            if not is_valid_email(self.value):
                self.border_color = "red"
            else:
                self.border_color = "gray"
        self.border_color = "gray"
        self.page.update()


button_style: dict = {
    "expand": True,
    "height": 38,
    "bgcolor": "blue",
    "style": ft.ButtonStyle(shape={"": ft.RoundedRectangleBorder(radius=5)}),
    "color": "white",
}


class Button(ft.ElevatedButton):
    def __init__(self, textto, **kwargs) -> None:
        super().__init__(**button_style, text=textto, **kwargs)
        # self.text.font_family="Consolas"
        # self.
        # self.text.font_family = 'Consolas'


button_back_style: dict = {
    "bgcolor": "transparent",
    "top": 8,
}


class BackButton(ft.IconButton):
    def __init__(self, size) -> None:
        super().__init__(
            **button_back_style,
            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
            tooltip="Back",
            icon_size=size,
        )


body_style: dict = {
    "width": 400,
    "padding": 15,
    "bgcolor": ft.colors.with_opacity(0.045, "white"),
    "border_radius": 10,
    "shadow": ft.BoxShadow(
        spread_radius=20, blur_radius=45, color=ft.colors.with_opacity(0.45, "black")
    ),
    # "font-family": "Consolas",
}


class BodyLogin(ft.Container):
    def __init__(self) -> None:
        super().__init__(**body_style)
        self.email = Input(password=False, email=True)
        self.password = Input(
            password=True,
        )
        self.email.on_change = self.disactive_login
        self.password.on_change = self.disactive_login
        self.signin = Button("Login")
        self.back = BackButton(size=13)
        self.back.on_click = self.back_page
        self.signin.on_click = self.login

        self.status1: ft.Control = fm.CheckBox(
            shape="circle",
            value=False,
            disabled=True,
            offset=ft.Offset(1, 0),
            bottom=0,
            right=1,
            top=1,
            animate_opacity=ft.Animation(200, "linear"),
            animate_offset=ft.Animation(350, "ease"),
            opacity=0,
        )

        self.status2: ft.Control = fm.CheckBox(
            shape="circle",
            value=False,
            disabled=True,
            offset=ft.Offset(1, 0),
            bottom=0,
            right=1,
            top=1,
            animate_opacity=ft.Animation(200, "linear"),
            animate_offset=ft.Animation(350, "ease"),
            opacity=0,
        )

        style: dict = {
            "padding": 20,
            "bgcolor": ft.colors.with_opacity(0.045, "black"),
            "height": 0,
            # "width" : ,
            "border_radius": 10,
            # "border" : "1px solid red
            "height": 0,
            # "alignment": 'center',
        }
        self.message = ft.Text(
            value="some_message", size=15, font_family="Consolas", opacity=1
        )

        # self.message.offset=ft.transform.Offset(0, -100),

        self.cont_message = ft.Container(content=self.message, **style)
        # self.cont_message.offset = ft.transform.Offset(0, -20)
        # self.cont_message.animate_offset=ft.animation.Animation(1000, ft.AnimationCurve.EASE_IN_OUT_BACK)
        self.cont_message.animate_size = ft.animation.Animation(
            1000, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.cont_message.animate_opacity = ft.animation.Animation(
            1000, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.cont_message.on_animation_end = self.message_clear

        self.signin.disabled = True

        self.content = ft.Stack(
            controls=[
                self.back,
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[self.cont_message],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Welcome back",
                                    size=25,
                                    font_family="Consolas",
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Text("e-mail", size=15, font_family="Consolas"),
                        ft.Stack(
                            controls=[
                                self.email,
                                self.status1,
                            ]
                        ),
                        ft.Text("password", size=15, font_family="Consolas"),
                        ft.Stack(
                            controls=[
                                self.password,
                                self.status2,
                            ]
                        ),
                        ft.Divider(height=15, color="transparent"),
                        ft.Row(controls=[self.signin]),
                    ]
                ),
            ]
        )

    def back_page(self, e):
        new = "/".join(list((self.page.route.split("/")))[:-1])
        self.page.route = new if new else "/"
        self.page.update()

    def login(self, e):
        global email, role, username, CURRENT_USER_ID
        email = self.email.value
        password = self.password.value
        users: list = db_manager.session.query(User).filter(User.email == email).all()

        if users:
            user: User = users[0]
            if user.password == password:
                username = user.username
                role = user.TYPE
                CURRENT_USER_ID = user.ID
                self.cont_message.content.clean()
                self.cont_message.height = 0
                self.password.border_color = "gray"
                self.email.border_color = "gray"
                # asyncio.run(self.validate_enti)
                asyncio.run(self.set_check(e))
                self.page.update()

            else:
                self.show_message("wrong data")
                self.password.border_color = "red"
                self.email.border_color = "red"

        else:
            self.show_message("wrong data")
            self.email.border_color = ft.colors.RED
            self.password.border_color = ft.colors.RED

        self.page.update()

    def show_message(self, text):
        self.cont_message.height = 60
        # self.cont_message.border_color = 'red'
        self.message.value = text
        self.message.color = "red"
        self.page.update()

    def message_clear(self, e):
        self.message.size = 0
        self.message.opacity = 0
        self.cont_message.opacity = 0
        self.cont_message.value = ""
        self.page.update()

    async def set_check(self, e):
        await asyncio.sleep(0.3)
        await self.set_ok_1()
        await self.set_ok_2()

    async def set_ok_1(self):
        self.status1.offset = ft.Offset(-0.5, 0)
        self.status1.opacity = 1
        self.page.update()

        await asyncio.sleep(0.4)

        self.status1.content.value = True
        self.status1.animate_checkbox(e=None)
        self.status1.update()

    async def set_ok_2(self):
        self.status2.offset = ft.Offset(-0.5, 0)
        self.status2.opacity = 1
        self.page.update()

        await asyncio.sleep(0.4)

        self.status2.content.value = True
        self.status2.animate_checkbox(e=None)
        self.status2.update()
        await asyncio.sleep(0.5)

        self.page.route = f"/app~{role}"

    def disactive_login(self, e):
        if self.password.value and self.email.value:
            self.signin.disabled = False
        else:
            self.signin.disabled = True
        self.page.update()


class BodyRegistration(ft.Container):
    def __init__(self) -> None:
        super().__init__(**body_style)
        self.login = Input(password=False)
        self.email = Input(
            password=False,
        )
        self.password = Input(
            password=True,
        )
        self.signup = Button("Sign Up", on_click=self.registr)
        self.back = BackButton(size=15)
        self.back.on_click = self.back_page
        self.message = ft.Text(
            value="some_message", size=15, font_family="Consolas", opacity=1
        )

        # self.message.offset=ft.transform.Offset(0, -100),
        style: dict = {
            "padding": 20,
            "bgcolor": ft.colors.with_opacity(0.045, "black"),
            "height": 0,
            "border_radius": 10,
            "height": 0,
        }

        self.cont_message = ft.Container(content=self.message, **style)
        self.cont_message.animate_size = ft.animation.Animation(
            1000, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.cont_message.animate_opacity = ft.animation.Animation(
            1000, ft.AnimationCurve.EASE_IN_OUT_BACK
        )

        self.signup.disabled = True

        self.status_1: ft.Control = fm.CheckBox(
            shape="circle",
            value=False,
            disabled=True,
            offset=ft.Offset(1, 0),
            bottom=0,
            right=1,
            top=1,
            animate_opacity=ft.Animation(200, "linear"),
            animate_offset=ft.Animation(350, "ease"),
            opacity=0,
        )
        self.status_2: ft.Control = fm.CheckBox(
            shape="circle",
            value=False,
            disabled=True,
            offset=ft.Offset(1, 0),
            bottom=0,
            right=1,
            top=1,
            animate_opacity=ft.Animation(200, "linear"),
            animate_offset=ft.Animation(350, "ease"),
            opacity=0,
        )
        self.status_3: ft.Control = fm.CheckBox(
            shape="circle",
            value=False,
            disabled=True,
            offset=ft.Offset(1, 0),
            bottom=0,
            right=1,
            top=1,
            animate_opacity=ft.Animation(200, "linear"),
            animate_offset=ft.Animation(350, "ease"),
            opacity=0,
        )

        self.imteacher_btn = Button("I'm a teacher")
        self.imteacher_btn.height = 50
        self.imteacher_btn.icon = ft.icons.ADB
        self.imteacher_btn.on_click = self.imteacher_btn_animation
        self.imteacher_btn.animate_scale = ft.animation.Animation(
            500, ft.AnimationCurve.EASE_IN_OUT_BACK
        )

        # self.imteacher_btn.on_activ
        self.option = None

        self.imstudent_btn = Button("I'm a student")
        self.imstudent_btn.animate_scale = ft.animation.Animation(
            500, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.imstudent_btn.on_click = self.imstudent_btn_animation
        self.imstudent_btn.height = 50
        self.imstudent_btn.icon = ft.icons.ACCESSIBILITY_NEW_OUTLINED

        for inp in [self.password, self.email, self.login]:
            inp.on_change = self.unable_signup_btn

        # self.imstudent_btn.disabled = True
        # self.imteacher_btn.disabled = True

        self.content = ft.Stack(
            controls=[
                self.back,
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[self.cont_message],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text("Someone New?", size=25, font_family="Consolas")
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=15, color="transparent"),
                        ft.Text("login", size=15, font_family="Consolas"),
                        ft.Stack(controls=[self.login, self.status_1]),
                        ft.Text("email", size=15, font_family="Consolas"),
                        ft.Stack(controls=[self.email, self.status_2]),
                        ft.Text("password", size=15, font_family="Consolas"),
                        ft.Stack(controls=[self.password, self.status_3]),
                        ft.Divider(height=10, color="transparent"),
                        ft.Row(controls=[self.imteacher_btn, self.imstudent_btn]),
                        ft.Divider(height=10, color="transparent"),
                        ft.Row(controls=[self.signup]),
                    ]
                ),
            ]
        )

    def back_page(self, e):
        new = "/".join(list((self.page.route.split("/")))[:-1])
        self.page.route = new if new else "/"
        self.page.update()

    def unable_signup_btn(self, e):
        if (
            self.option
            and self.email.value
            and self.password.value
            and self.login.value
        ):
            self.signup.disabled = False
            self.page.update()
        else:
            self.signup.disabled = True
            self.page.update()

    def registr(self, e):
        global username, email, role, CURRENT_USER_ID
        role = self.option
        username = self.login.value
        email = self.email.value
        password = self.password.value
        users: list = db_manager.session.query(User).filter(User.email == email).all()

        if users:
            self.show_message("this email is already in use")
            self.email.border_color = "red"

        else:
            if is_valid_email(self.email.value):
                self.cont_message.height = 0
                db_manager.add_user(
                    user_type=self.option,
                    email=email,
                    username=username,
                    password=password,
                )
                user = (
                    db_manager.session.query(User).filter(User.email == email).first()
                )
                CURRENT_USER_ID = user.ID
                asyncio.run(self.set_check(e))
            else:
                self.show_message("wrong email validation")
                self.email.border_color = "red"

        self.page.update()

    def show_message(self, text):
        self.cont_message.height = 60
        # self.cont_message.border_color = 'red'
        self.message.value = text
        self.message.color = "red"
        self.page.update()

    def imteacher_btn_animation(self, e):
        self.option = "teacher"
        self.unable_signup_btn(e)
        self.imteacher_btn.opacity = 1
        self.imteacher_btn.scale = 1.05
        self.imstudent_btn.opacity = 0.45
        self.imstudent_btn.scale = 0.9
        self.page.update()

    def imstudent_btn_animation(self, e):
        self.option = "student"
        self.unable_signup_btn(e)
        self.imteacher_btn.opacity = 0.45
        self.imteacher_btn.scale = 0.9
        self.imstudent_btn.opacity = 1
        self.imstudent_btn.scale = 1.05
        self.page.update()

    async def set_check(self, e):
        await asyncio.sleep(0.3)
        await self.set_ok_1()
        await self.set_ok_2()
        await self.set_ok_3()

    async def set_ok_1(self):
        self.status_1.offset = ft.Offset(-0.5, 0)
        self.status_1.opacity = 1
        self.page.update()

        await asyncio.sleep(0.4)

        self.status_1.content.value = True
        self.status_1.animate_checkbox(e=None)
        self.status_1.update()

    async def set_ok_2(self):
        self.status_2.offset = ft.Offset(-0.5, 0)
        self.status_2.opacity = 1
        self.page.update()

        await asyncio.sleep(0.4)

        self.status_2.content.value = True
        self.status_2.animate_checkbox(e=None)
        self.status_2.update()

    async def set_ok_3(self):
        self.status_3.offset = ft.Offset(-0.5, 0)
        self.status_3.opacity = 1
        self.page.update()

        await asyncio.sleep(0.4)

        self.status_3.content.value = True
        self.status_3.animate_checkbox(e=None)
        self.status_3.update()
        await asyncio.sleep(0.5)
        self.page.route = "/app~student"


class BodyHello(ft.Container):
    def __init__(self) -> None:
        super().__init__(**body_style)
        self.to_signin = Button("Login")
        self.to_register = Button("Sign Up")

        self.to_signin.height = 100
        self.to_signin.animate_scale = ft.animation.Animation(
            400, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.to_signin.on_hover = self.to_signin_anim
        self.to_signin.icon = ft.icons.LOGIN

        self.on_hover = self.to_signin_anim_back

        self.to_register.height = 100
        self.to_register.icon = ft.icons.ADD_CIRCLE
        self.to_register.animate_scale = ft.animation.Animation(
            400, ft.AnimationCurve.EASE_IN_OUT_BACK
        )
        self.to_register.on_hover = self.to_register_anim

        self.to_signin.on_click = self.go_login
        self.to_register.on_click = self.go_registrations

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("Hello There!", font_family="Consolas", size=25)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        ft.Text("This is pytosh!", font_family="Consolas", size=25)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(controls=[self.to_signin, self.to_register]),
            ],
        )

    def to_signin_anim(self, e):
        self.to_register.scale = 0.8
        self.to_register.opacity = 0.6
        self.to_signin.scale = 1.1
        self.to_signin.opacity = 1

        self.text_size = 6
        self.page.update()

    def to_register_anim(self, e):
        self.to_register.scale = 1.1
        self.to_register.opacity = 1
        self.to_signin.opacity = 0.6
        self.to_signin.scale = 0.8
        self.page.update()

    def to_signin_anim_back(self, e):
        self.to_signin.opacity = 1
        self.to_register.opacity = 1
        self.to_register.scale = 1
        self.to_signin.scale = 1
        self.page.update()

    def go_login(self, e):
        self.page.route = "/login"
        self.page.update()

    def go_registrations(self, e):
        self.page.route = "/registration"
        self.page.update()


app_style: dict = {}


class NavBar(ft.UserControl):
    def __init__(self, func) -> None:
        self.func = func
        super().__init__()

    def HighLight(self, e):
        if e.data == "true":
            e.control.bgcolor = "white10"
            e.control.update()

            e.control.content.controls[0].controls[0].icon_color = "white"
            e.control.content.controls[0].controls[1].color = "white"
            e.control.content.update()
        else:
            e.control.bgcolor = None
            e.control.update()
            e.control.content.controls[0].controls[0].icon_color = "white54"
            e.control.content.controls[0].controls[1].color = "white54"
            e.control.content.update()

    def UserData(self, initals, name, description):
        return ft.Container(
            content=ft.Row(
                alignment="top",
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        bgcolor="bluegrey900",
                        alignment=ft.alignment.center,
                        border_radius=8,
                        content=ft.Text(
                            value=initals,
                            size=20,
                            weight="bold",
                        ),
                    ),
                    ft.Column(
                        alignment="center",
                        spacing=1,
                        controls=[
                            ft.Text(
                                value=name,
                                size=11,
                                weight="bold",
                                opacity=1,
                                animate_opacity=200,
                            ),
                            ft.Text(
                                value=description,
                                size=9,
                                weight="w400",
                                color="white54",
                                opacity=1,
                                animate_opacity=200,
                            ),
                        ],
                    ),
                ],
            )
        )

    def ContainedIcons(self, icon_name, text, onclick=None):
        return ft.Container(
            width=180,
            height=45,
            border_radius=10,
            on_hover=lambda e: self.HighLight(e),
            content=ft.Row(
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            ft.Text(
                                value=text,
                                color="white54",
                                size=11,
                                opacity=1,
                                animate_opacity=200,
                                left=40,
                                top=14,
                            ),
                            ft.IconButton(
                                top=1,
                                left=-68 - 35,
                                icon=icon_name,
                                icon_size=18,
                                width=180 + 70,
                                icon_color="white54",
                                style=ft.ButtonStyle(
                                    shape={
                                        "": ft.RoundedRectangleBorder(radius=7),
                                    },
                                    overlay_color={
                                        "": "transparent",
                                    },
                                ),
                                on_click=onclick,
                            ),
                        ],
                    ),
                ]
            ),
        )

    def build(self) -> ft.Container:
        global username, email, role, icon_btns
        if role == "student":
            icon_btns = [
                # self.ContainedIcons(
                #     ft.icons.MANAGE_ACCOUNTS,
                #     "Account",
                #     onclick=lambda _: self.page.go("/app~student/account"),
                # ),
                self.ContainedIcons(
                    ft.icons.TASK_OUTLINED,
                    "Tasks",
                    onclick=lambda _: self.page.go("/app~student/groups"),
                ),
                # self.ContainedIcons(ft.icons.SPACE_DASHBOARD_ROUNDED, "dashboard"),
                self.ContainedIcons(
                    ft.icons.GROUP,
                    "Groups",
                    onclick=lambda _: self.page.go("/app~student/groups-manager"),
                ),
                # self.ContainedIcons(ft.icons.PIE_CHART_ROUNDED, "Analytics"),
                self.ContainedIcons(
                    ft.icons.LOGOUT_ROUNDED,
                    "Logout",
                    onclick=self.logout,
                ),
            ]
        else:
            icon_btns = [
                # self.ContainedIcons(
                #     ft.icons.MANAGE_ACCOUNTS,
                #     "Account",
                #     onclick=lambda _: self.page.go("/app~teacher/account"),
                # ),
                # self.ContainedIcons(
                #     ft.icons.TASK_OUTLINED,
                #     "Tasks",
                #     onclick=lambda _: self.page.go("/app~teacher/tasks-edit"),
                # ),
                # self.ContainedIcons(ft.icons.SPACE_DASHBOARD_ROUNDED, "dashboard"),
                self.ContainedIcons(
                    ft.icons.WORKSPACES_OUTLINED,
                    "Edit workspace",
                    onclick=lambda _: self.page.go("/app~teacher/groups-manager"),
                ),
                # self.ContainedIcons(ft.icons.PIE_CHART_ROUNDED, "Analytics"),
                self.ContainedIcons(
                    ft.icons.LOGOUT_ROUNDED,
                    "Logout",
                    onclick=self.logout,
                ),
            ]
        return ft.Container(
            expand=True,
            # width=200,
            # height=580,
            padding=ft.padding.only(top=10),
            alignment=ft.alignment.center,
            content=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment="center",
                controls=[
                    self.UserData(
                        username[0].upper(),
                        username if len(username) <= 13 else username[:10] + "...",
                        role,
                    ),
                    ft.Container(
                        width=24,
                        height=24,
                        bgcolor="bluegrey800",
                        border_radius=12,
                        on_click=partial(self.func),
                    ),
                    ft.Divider(height=5, color="transparent"),
                    *icon_btns[:-1],
                    ft.Divider(
                        height=200,
                        color="transparent",
                    ),
                    ft.Divider(
                        height=5,
                        color="white24",
                    ),
                    icon_btns[-1],
                ],
            ),
        )

    def logout(self, e):
        global username, email, role, GROUPS_DATA, TASKS_DATA, THEMES_DATA, icon_btns, CURRENT_THEME_ID, CURRENT_USER_ID
        username = ""
        email = ""
        role = ""
        GROUPS_DATA = {}
        TASKS_DATA = {}
        THEMES_DATA = {}
        icon_btns = []
        CURRENT_THEME_ID = None
        CURRENT_GROUP_ID = None
        CURRENT_USER_ID = None
        self.page.go("/")


class AccountPage(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self) -> ft.Container:
        return ft.Container(bgcolor="green", width=300)


class ThemeContainer(ft.UserControl):
    def __init__(self, name, description, color="bluegrey900", id=0):
        super().__init__()
        self.id = id
        self.name = name
        self.description = description
        self.color = color

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.name, font_family="Consolas", size=16, text_align="center"
                    ),
                    ft.Divider(
                        height=2 if self.description else 0,
                        color="white40" if self.description else "transparent",
                    ),
                    ft.Text(
                        self.description,
                        font_family="Consolas",
                        size=12,
                        text_align="center",
                    ),
                ],
                # spacing=10,
                horizontal_alignment="center",
                # alignment='center'
            ),
            margin=10,
            padding=10,
            alignment=ft.alignment.top_center,
            # horizontal_alignment='left',
            bgcolor=self.color,
            # width=150,
            # height=50,
            border_radius=10,
            ink=True,
            on_click=(
                self.go_to_tasks
                if self.name != "You don't have any tasks yet"
                else None
            ),
            animate_scale=ft.animation.Animation(500, "decelerate"),
            on_long_press=None,
            shadow=ft.BoxShadow(
                spread_radius=3,
                color=ft.colors.with_opacity(0.1, "black"),
                offset=ft.Offset(3, 3),
            ),
        )

    def go_to_tasks(self, e):
        global CURRENT_THEME_ID
        CURRENT_THEME_ID = self.id
        self.page.go("/app~student/tasks")


class TaskCard(ft.UserControl):
    def __init__(
        self, name, description, color="bluegrey900", id=0, status=0, par=None
    ):
        super().__init__()
        self.id = id
        self.status = status
        self.par = par
        self.name = name
        self.description = description
        if status == 0:
            self.icon = ft.Icon(ft.icons.CIRCLE_ROUNDED)
            self.icon.color = "#37474f"

        elif status == 1:
            self.icon = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED)
            self.icon.color = ft.colors.GREEN_700
        else:
            self.icon = ft.Icon(ft.icons.CIRCLE_ROUNDED)
            self.icon.color = ft.colors.RED_600

        self.icon.animate_scale = ft.animation.Animation(200, "decelerate")
        self.icon.tooltip = "не было попыток сдать задачу"
        self.color = color
        self.status_row = ft.Row()

        self.card = ft.Card(
            elevation=0.9,
            animate_scale=ft.animation.Animation(200, "decelerate"),
            margin=ft.margin.only(left=10, right=30, top=10),
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                height=60,
                # alignment='topleft'
                on_click=self.go_to_task,
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(0.1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.Row(
                    expand=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ListTile(
                            leading=self.icon,
                            expand=1,
                            title=ft.Text(
                                name,
                                font_family="Consolas",
                                text_align="topleft",
                                size=17,
                            ),
                        ),
                        ft.Container(
                            expand=0,
                            padding=ft.padding.only(right=20),
                            content=self.status_row,
                        ),
                    ],
                ),
            ),
        )

    def go_to_task(self, e):
        self.page.route = "/app~student/tasks/" + str(self.id)
        self.page.update()

    def set_status(self, it, vs):
        if it != vs:
            self.status = -1
            self.status_row.controls.clear()
            if it == 0:
                self.status_row.controls = [
                    ft.Text(
                        "to refine",
                        color="red",
                        animate_scale=ft.animation.Animation(200, "decelerate"),
                    )
                ]
                self.icon.tooltip = "задача решена не правильно"

            else:
                self.status_row.controls = [
                    ft.Text(
                        "to refine",
                        color="red",
                        animate_scale=ft.animation.Animation(200, "decelerate"),
                    ),
                    ft.Container(
                        border_radius=5,
                        width=1,
                        height=40,
                        bgcolor=ft.colors.WHITE12,
                        margin=ft.margin.only(left=10),
                    ),
                    ft.Text(str(it), color="white", weight=ft.FontWeight.W_400),
                    ft.Text("/" + str(vs), color=ft.colors.WHITE12),
                ]
                self.icon.tooltip = "нужно доработать задачу"

        else:
            self.status = 1
            self.status_row.controls.clear()
            self.status_row.controls = [
                ft.Text(
                    "accepted",
                    color="green",
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                ),
                ft.Container(
                    border_radius=5,
                    width=1,
                    height=40,
                    bgcolor=ft.colors.WHITE12,
                    margin=ft.margin.only(left=10),
                ),
                ft.Text(str(it), color="white", weight=ft.FontWeight.W_400),
                ft.Text("/" + str(vs), color=ft.colors.WHITE12),
            ]
            self.icon.tooltip = "задача зачтена!"

    def set_icon(self, status):
        if status == 0:
            self.icon = ft.Icon(ft.icons.CIRCLE_ROUNDED)
            self.icon.color = ft.colors.with_opacity(0.5, "white")

        elif status == 1:
            self.icon = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED)
            self.icon.color = ft.colors.GREEN_700
        else:
            self.icon = ft.Icon(ft.icons.CIRCLE_ROUNDED)
            self.icon.color = ft.colors.RED_600
        # self.icon.update()
        # self.card.update()
        # self.par.update()

    def anim(self, e):
        if e.data == "true":
            self.card.elevation = 8
            self.card.scale = 1.009
            self.icon.scale = 1.2
            if self.status_row.controls:
                self.status_row.controls[0].scale = 1.25
            # self.icon.update()
            self.card.update()
            self.page.update()
        else:

            self.card.elevation = 0.9
            self.card.scale = 1

            self.icon.scale = 1
            if self.status_row.controls:
                self.status_row.controls[0].scale = 1

            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.card
    # for i in data:
    #     n.controls.append(ThemeCard)

class ThemeCard(ft.UserControl):
    def __init__(self, name, description, color="bluegrey900", id=0, progress=0):
        super().__init__()
        self.id = id
        self.name = name
        self.description = description
        self.color = color
        self.progress_ring = ft.ProgressRing(
            expand=0,
            width=40,
            height=40,
            stroke_width=4,
            value=progress,
            color=ft.colors.GREEN_600,
            bgcolor="#5a5c60",
        )

        self.progress_ring.rotate = ft.transform.Rotate(
            0, alignment=ft.alignment.center
        )
        self.progress_ring.animate_scale = ft.animation.Animation(150)
        self.progress_ring.animate_rotation = ft.animation.Animation(300)
        self.progress_ring.offset = (0, 1)

        self.card = ft.Card(
            elevation=0.9,
            animate_scale=ft.animation.Animation(200, "decelerate"),
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                height=120,
                on_click=self.go,
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(0.1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.Row(
                    expand=0,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.ListTile(
                            expand=1,
                            title=ft.Text(
                                name,
                                font_family="Consolas",
                                text_align="topleft",
                                height=30,
                            ),
                            subtitle=ft.Text(
                                description, font_family="Consolas", text_align="left"
                            ),
                        ),
                        ft.Container(
                            expand=0,
                            padding=ft.padding.only(right=20),
                            content=self.progress_ring,
                        ),
                    ],
                ),
            ),
        )

    def set_procent(self, n):
        self.progress_ring.value = n

    def go(self, e):
        global CURRENT_THEME_ID
        CURRENT_THEME_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.controls[0].controls[1].content.on_animation_end = (
            lambda _: self.page.go("/app~student/tasks")
        )
        self.page.update()

        # self.page.go('')

    def anim(self, e):
        if e.data == "true":
            self.card.elevation = 8
            self.card.scale = 1.009
            self.progress_ring.scale = 1.3
            self.progress_ring.rotate.angle += 0.4
            self.progress_ring.update()
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.scale = 1
            self.progress_ring.scale = 1
            self.progress_ring.rotate.angle -= 0.4

            self.progress_ring.update()
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.card


class ThemeTasksPage(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()

    def get_tasks(self):
        global tasks, CURRENT_THEME_ID
        self.tasks_list = []
        for task in TASKS_DATA.values():

            if task["theme_id"] == CURRENT_THEME_ID:
                self.tasks_list.append(task)

    def build(self) -> ft.Text:
        self.get_tasks()
        themes = ft.Column(
            expand=1,
            spacing=4,
            # paddi
            run_spacing=10,
            # scroll=ft.ScrollMode.HIDDEN,
        )
        for task in self.tasks_list:
            name = task["description"].split("|")[0]
            short_description = task["description"].split("|")[1]
            tot, acc = task["total_tests"], task["accepted_tests"]
            if tot == 0:
                crd = TaskCard(name, short_description, id=task["ID"], status=0)
            elif acc == tot:
                crd = TaskCard(name, short_description, id=task["ID"], status=1)
                crd.set_status(acc, tot)
            else:
                crd = TaskCard(name, short_description, id=task["ID"], status=-1)
                crd.set_status(acc, tot)

            themes.controls.append(crd)
        return themes


class ThemesPage(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        self.back = BackButton(size=13)

    def build(self):
        global get_data
        get_data()
        themes = ft.Column(
            expand=1,
            scroll=ft.ScrollMode.HIDDEN,
        )

        if THEMES_DATA:
            for theme_id, theme in THEMES_DATA.items():
                total, acc = 0, 0
                for task_id, task in TASKS_DATA.items():
                    if task["theme_id"] != theme_id:
                        continue
                    if (
                        task["accepted_tests"] == task["total_tests"]
                        and task["total_tests"] != 0
                    ):
                        acc += 1
                    total += 1

                progress = acc / total if total > 0 else 0
                cnt = ThemeCard(
                    name=theme["description"].split("|")[0],
                    description=theme["description"].split("|")[1],
                    id=theme_id,
                    progress=progress,
                )
                # cnt.set_procent(0.2)
                themes.controls.append(cnt)
        else:
            themes.controls.append(
                ThemeContainer("You don't have any tasks yet", "", "red", 0)
            )

        return themes


class GroupCard(ft.UserControl):
    def __init__(self, leading, title, subtitle, id):
        super().__init__()
        self.id = id

        self.card = ft.Card(
            elevation=0.9,
            height=200,
            width=400,
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                on_click=(
                    self.go
                    if self.id != "wtf?"
                    else lambda _: self.page.go("/app~student/groups-manager")
                ),
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.ListTile(
                    leading=ft.Icon(leading),
                    title=ft.Text(title, font_family="Consolas", text_align="left"),
                    subtitle=ft.Text(
                        subtitle, font_family="Consolas", text_align="left"
                    ),
                ),
            ),
        )

    def go(self, e):
        global CURRENT_GROUP_ID
        CURRENT_GROUP_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.controls[0].controls[1].content.on_animation_end = (
            lambda _: self.page.go("/app~student/themes")
        )
        self.page.update()

    def anim(self, e):

        if e.data == "true":

            self.card.elevation = 8
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return ft.Container(
            alignment=ft.alignment.center,
            content=self.card,
        )


class TaskPage(ft.UserControl):
    def __init__(self, info, id):
        super().__init__()
        get_data()

        self.id = id
        self.info = info
        description = info["description"]
        self.task_name = description.split("|")[0]
        limits = (
            description.split("|")[5]
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .split(",")
        )

        self.time_limit = limits[0]
        self.memory_limit = limits[1]
        self.hard_procent = (
            limits[2]
            if len(limits[2].split("-")) > 1
            and limits[2].split("-")[0] != limits[2].split("-")[1]
            else limits[2].split("-")[0]
        )
        self.description = description.split("|")[2]
        self.input_data = description.split("|")[3]
        self.output_data = description.split("|")[4]
        self.tests_input = (
            description.split("|")[6]
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .replace("\\n", "\n")
            .split(",")
        )
        self.tests_output = (
            description.split("|")[7]
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .replace("\\n", "\n")
            .split(",")
        )
        self.back_btn = BackButton(size=13)
        self.back_btn.top = None

        self.status = 0
        if TASKS_DATA[self.id]["total_tests"] > 0:
            if (
                TASKS_DATA[self.id]["accepted_tests"]
                == TASKS_DATA[self.id]["total_tests"]
            ):
                self.status = 1
            else:
                self.status = -1

        def go_back(e):
            self.page.controls[0].controls[1].content.offset = ft.transform.Offset(1, 0)
            self.page.controls[0].controls[1].content.update()
            self.page.update()

        self.indicator = ft.Container(
            width=22,
            height=22,
            bgcolor="#37474f",
            border_radius=11,
            animate_scale=ft.animation.Animation(400, "decelerate"),
            on_animation_end=self.back_scale_indicator,
        )

        if self.status == 0:
            self.indicator.bgcolor = "#37474f"

        elif self.status == 1:
            self.indicator.bgcolor = ft.colors.GREEN_700

        else:
            self.indicator.bgcolor = ft.colors.RED_600

        # self.indicator.update()
        # self.page.update()

        self.back_btn.on_click = go_back
        self.NAME_ROW = ft.Row(
            # expand=True,
            controls=[
                self.back_btn,
                ft.Container(
                    on_hover=self.namehover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    expand=True,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            # self.back_btn,
                            ft.Row(
                                alignment="center",
                                controls=[
                                    ft.Text(
                                        self.task_name.upper(),
                                        font_family="Consolas",
                                        size=20,
                                        text_align="center",
                                        weight=110,
                                    ),
                                    self.indicator,
                                ],
                            ),
                            ft.Row(
                                alignment="center",
                                controls=[
                                    ft.Container(
                                        border=ft.border.all(1.5, ft.colors.RED_300),
                                        border_radius=10,
                                        padding=ft.padding.only(
                                            left=8, top=2, bottom=2, right=1
                                        ),
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(
                                                    "Time limit:",
                                                    font_family="Consolas",
                                                    size=11,
                                                    color=ft.colors.with_opacity(
                                                        0.5, "white"
                                                    ),
                                                ),
                                                ft.Text(
                                                    self.time_limit + "C",
                                                    font_family="Consolas",
                                                    size=12,
                                                    color=ft.colors.with_opacity(
                                                        0.75, "white"
                                                    ),
                                                    offset=(-0.45, 0),
                                                ),
                                            ]
                                        ),
                                    ),
                                    ft.Container(
                                        border=ft.border.all(1.5, ft.colors.RED_200),
                                        border_radius=10,
                                        padding=ft.padding.only(
                                            left=8, top=2, bottom=2, right=1
                                        ),
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(
                                                    "Memory limit:",
                                                    font_family="Consolas",
                                                    size=11,
                                                    color=ft.colors.with_opacity(
                                                        0.5, "white"
                                                    ),
                                                ),
                                                ft.Text(
                                                    self.memory_limit + "MB",
                                                    font_family="Consolas",
                                                    size=12,
                                                    color=ft.colors.with_opacity(
                                                        0.75, "white"
                                                    ),
                                                    offset=(-0.3, 0),
                                                ),
                                            ]
                                        ),
                                    ),
                                    ft.Container(
                                        border=ft.border.all(1.5, ft.colors.RED_100),
                                        border_radius=10,
                                        padding=ft.padding.only(
                                            left=8, top=2, bottom=2, right=1
                                        ),
                                        content=ft.Row(
                                            controls=[
                                                ft.Text(
                                                    "Hard:",
                                                    font_family="Consolas",
                                                    size=11,
                                                    color=ft.colors.with_opacity(
                                                        0.5, "white"
                                                    ),
                                                ),
                                                ft.Text(
                                                    self.hard_procent + "%",
                                                    font_family="Consolas",
                                                    size=12,
                                                    color=ft.colors.with_opacity(
                                                        0.75, "white"
                                                    ),
                                                    # offset=(-0.45, 0),
                                                ),
                                            ]
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    border_radius=10,
                    padding=10,
                    bgcolor="#2a3139",
                ),
            ]
        )
        self.tests_table = ft.Column(
            controls=[
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Column(
                            horizontal_alignment="center",
                            controls=[
                                ft.Text(
                                    "ПРИМЕРЫ:",
                                    font_family="Consolas",
                                    size=14,
                                    text_align="center",
                                    weight=110,
                                ),
                                ft.Divider(color="white40", height=1),
                            ],
                        )
                    ],
                ),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.DataTable(
                            bgcolor="#2a3139",
                            border_radius=10,
                            columns=[
                                ft.DataColumn(
                                    ft.Text("Input"),
                                ),
                                ft.DataColumn(ft.Text("Output")),
                            ],
                        )
                    ],
                ),
            ]
        )

        self.inpout_content = ft.Column(
            expand=True,
            # height=600,
            alignment="top",
            scroll=ft.ScrollMode.HIDDEN,
            # padding = 0,
            controls=[
                ft.Container(
                    # height = 400,
                    bgcolor="#2a3139",
                    border_radius=10,
                    margin=ft.margin.only(top=10),
                    on_hover=self.inphover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    padding=10,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "ВХОДНЫЕ ДАННЫЕ:",
                                font_family="Consolas",
                                size=14,
                                text_align="center",
                                weight=110,
                            ),
                            ft.Divider(color="white40", height=1),
                            ft.Text(
                                self.input_data.replace("\\n", "\n"),
                                font_family="Consolas",
                                size=14,
                                text_align="center",
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    # height = 400,
                    bgcolor="#2a3139",
                    border_radius=10,
                    padding=10,
                    on_hover=self.outhover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "ВЫХОДНЫЕ ДАННЫЕ:",
                                font_family="Consolas",
                                size=14,
                                text_align="center",
                                weight=110,
                            ),
                            ft.Divider(color="white40", height=1),
                            ft.Text(
                                self.output_data.replace("\\n", "\n"),
                                font_family="Consolas",
                                size=14,
                                text_align="center",
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    # height = 400,
                    bgcolor="#2a3139",
                    border_radius=10,
                    padding=10,
                    on_hover=self.tablehover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            self.tests_table,
                        ],
                    ),
                ),
            ],
        )

        self.description_content = ft.Column(
            expand=True,
            height=600,
            # alignment='top',
            animate_scale=ft.animation.Animation(200, "decelerate"),
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Container(
                    alignment=ft.alignment.top_left,
                    on_hover=self.deschover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    bgcolor="#2a3139",
                    border_radius=10,
                    padding=10,
                    offset=(0, 0),
                    height=600,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "УСЛОВИЕ:",
                                    font_family="Consolas",
                                    size=14,
                                    text_align="center",
                                    weight=110,
                                ),
                            ),
                            ft.Divider(color="white40", height=1),
                            ft.Text(
                                self.description,
                                font_family="Consolas",
                                size=14,
                                text_align="center",
                            ),
                        ],
                    ),
                )
            ],
        )

        file_picker = ft.FilePicker(on_result=self.on_dialog_result)
        button_style: dict = {
            # "expand": True,
            # "margin": 5,
            "height": 48,
            # "width": 120,
            "bgcolor": ft.colors.BLUE_500,
            "style": ft.ButtonStyle(shape={"": ft.RoundedRectangleBorder(radius=5)}),
            "color": "white",
        }
        button_style2: dict = {
            # "expand": True,
            # "margin": 5,
            "height": 48,
            "width": 160,
            "bgcolor": ft.colors.GREEN_400,
            "style": ft.ButtonStyle(shape={"": ft.RoundedRectangleBorder(radius=5)}),
            "color": "white",
        }
        self.filepick_btn = ft.ElevatedButton(
            **button_style,
            text="выбор файла",
            icon=ft.icons.UPLOAD_ROUNDED,
            disabled=True,
            animate_scale=ft.animation.Animation(200, "decelerate"),
        )
        self.filepick_btn.on_click = lambda _: file_picker.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["py", "cpp"]
        )
        self.send_btn = ft.ElevatedButton(
            **button_style2,
            text="отправить",
            disabled=True,
            icon=ft.icons.SEND_ROUNDED,
            animate_scale=ft.animation.Animation(200, "decelerate"),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(150, ft.AnimationCurve.BOUNCE_OUT),
        )

        self.filepick_btn.on_hover = self.filepick_btn_anim
        self.send_btn.on_hover = self.send_btn_anim

        self.send_btn.on_click = self.send_code

        self.change_send = ft.SegmentedButton(
            show_selected_icon=False,
            on_change=self.change_send_btn,
            selected={"1"},
            segments=[
                ft.Segment(
                    value="1",
                    label=ft.Text("code"),
                    # icon=ft.Icon(ft.icons.DESCRIPTION_ROUNDED),
                ),
                ft.Segment(
                    value="2",
                    label=ft.Text("file"),
                    # icon=ft.Icon(ft.icons.INPUT),
                ),
            ],
        )

        self.send_type = "code"
        self.patch_to_file = ""
        self.filename = ""

        self.editor = ft.TextField(
            on_change=self.change_send_btn,
            label="write your code here...",
            multiline=True,
            min_lines=16,
            max_lines=16,
            border_color=ft.colors.WHITE38,
            text_size=16,
            text_style=ft.TextStyle(font_family="Roboto Mono"),
        )
        # self.page.overlay.append(file_picker)
        self.code_editor = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
            height=600,
            controls=[
                ft.Container(
                    alignment=ft.alignment.top_left,
                    # on_hover=self.deschover,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    bgcolor="#2a3139",
                    border_radius=10,
                    padding=10,
                    offset=(0, 0),
                    height=600,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Container(
                                # alignment='center',
                                content=ft.Text(
                                    "КОД:",
                                    font_family="Consolas",
                                    size=14,
                                    text_align="center",
                                    weight=110,
                                ),
                            ),
                            ft.Divider(color="white40", height=1),
                            self.editor,
                            ft.Divider(color="white40", height=1),
                            file_picker,
                            self.change_send,
                            ft.Row(
                                controls=[self.filepick_btn, self.send_btn],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                        ],
                    ),
                )
            ],
        )

        self.sendings_panel = ft.ExpansionPanelList(
            expand_icon_color="white40",
            elevation=8,
            divider_color="black",
            # divider_height=10,
            controls=[],
        )

        self.tests_content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
            on_scroll_interval=1,
            height=600,
            controls=[
                ft.Container(
                    alignment=ft.alignment.top_left,
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    bgcolor="#2a3139",
                    border_radius=10,
                    padding=10,
                    offset=(0, 0),
                    # expand=2,
                    # height=600,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Container(
                                # alignment='center',
                                content=ft.Text(
                                    "ОТПРАВКИ:",
                                    font_family="Consolas",
                                    size=14,
                                    text_align="center",
                                    weight=110,
                                ),
                            ),
                            ft.Divider(color="white40", height=1),
                            self.sendings_panel,
                        ],
                    ),
                )
            ],
        )

        self.left_column = ft.Container(
            expand=True,
            content=self.description_content,
            animate_scale=ft.animation.Animation(200, "decelerate"),
        )
        self.right_column = ft.Container(
            # scro
            height=600,
            expand=True,
            content=self.code_editor,
            animate_scale=ft.animation.Animation(200, "decelerate"),
        )

        self.controls_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.SegmentedButton(
                    show_selected_icon=False,
                    on_change=self.change_left_content,
                    selected={"1"},
                    segments=[
                        ft.Segment(
                            value="1",
                            label=ft.Text("description"),
                            icon=ft.Icon(ft.icons.DESCRIPTION_ROUNDED),
                        ),
                        ft.Segment(
                            value="2",
                            label=ft.Text("input-output"),
                            icon=ft.Icon(ft.icons.INPUT),
                        ),
                    ],
                ),
                ft.SegmentedButton(
                    show_selected_icon=False,
                    selected={"1"},
                    on_change=self.change_right_content,
                    segments=[
                        ft.Segment(
                            value="1",
                            label=ft.Text("code editor"),
                            icon=ft.Icon(ft.icons.CODE),
                        ),
                        ft.Segment(
                            value="2",
                            label=ft.Text("tests data"),
                            icon=ft.Icon(ft.icons.NOTES),
                        ),
                    ],
                ),
            ],
        )

        self.description_row = ft.Row(
            controls=[
                self.left_column,
                self.right_column,
            ]
        )

        x = 0

        for inp, out in zip(self.tests_input, self.tests_output):
            if x >= 2:
                break
            exec(f"self.inp{x} = inp")
            exec(f"self.out{x} = out")
            self.tests_table.controls[1].controls[0].rows.append(
                ft.DataRow(
                    # on_select_changed = lambda e : pyperclip.copy(inp) if e.data=='true' else None,
                    cells=[
                        ft.DataCell(
                            ft.Text(inp),
                            on_tap=lambda e, text=inp: copy_to_clipboard(text),
                        ),
                        ft.DataCell(
                            ft.Text(out),
                            on_tap=lambda e, text=out: copy_to_clipboard(text),
                        ),
                    ]
                )
            )
            x += 1

    def change_send_btn(self, e):
        if self.change_send.selected == {"1"}:
            self.send_type = "code"
            self.filepick_btn.disabled = True
            self.send_btn.disabled = False if self.editor.value else True
            self.send_btn.text = "отправить"

            if self.editor.value:
                self.send_btn.disabled = False
            else:
                self.send_btn.disabled = True

        else:
            self.send_type = "file"
            self.filepick_btn.disabled = False
            if not self.filename:
                self.send_btn.disabled = True
            else:
                self.send_btn.text = f"отправить {self.filename}"
                self.send_btn.disabled = False

        self.send_btn.update()
        self.filepick_btn.update()
        self.page.update()

    def filepick_btn_anim(self, e):
        if e.data == "true":
            self.filepick_btn.scale = 1.03
            self.filepick_btn.elevation = 6
        else:
            self.filepick_btn.elevation = 1
            self.filepick_btn.scale = 1

        self.filepick_btn.update()
        self.page.update()

    def send_btn_anim(self, e):
        if e.data == "true":
            self.send_btn.scale = 1.03
            self.send_btn.elevation = 6

        else:
            self.send_btn.elevation = 1
            self.send_btn.scale = 1

        self.send_btn.update()
        self.page.update()

    def back_scale_indicator(self, e):
        self.indicator.scale = 1

        self.indicator.update()
        self.page.update()

    def animate_status(self, status):
        if status == 0:
            self.indicator.bgcolor = "#37474f"

        elif status == 1:
            self.indicator.bgcolor = ft.colors.GREEN_700

        else:
            self.indicator.bgcolor = ft.colors.RED_600

        self.indicator.scale = 1.4

        self.indicator.update()
        self.page.update()

    def send_code(self, e):
        self.send_btn.rotate.angle += 0.06
        self.send_btn.update()
        self.page.update()

        time.sleep(0.1)
        self.send_btn.rotate.angle -= 0.12
        self.send_btn.update()
        self.page.update()

        time.sleep(0.1)
        self.send_btn.rotate.angle = 0
        self.send_btn.update()
        self.page.update()

        get_data()
        if self.send_type == "code":
            code = self.editor.value.strip()
            self.editor.value = ""

        else:

            def read_file(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                return file_content

            code = read_file(self.patch_to_file).strip()

        sending_data = {
            "code": code,
            "total_tests": 0,
            "accepted_tests": 0,
            "verdict": None,
            "info_test": None,
            "author_id": CURRENT_USER_ID,
            "task_id": self.id,
            "time": get_time(),
            "num": 0,
        }

        for test_id, test in TESTS_DATA.items():
            if test["task_id"] == self.id:
                print(test["input"], test["output"])
                data = execute_code(
                    code=code,
                    inp=test["input"],
                    expected_output=test["output"],
                    memory_limit_mb=int(self.memory_limit),
                    timeout=int(self.time_limit),
                )
                sending_data["total_tests"] += 1
                if data["status"] == "Accepted":
                    sending_data["accepted_tests"] += 1

                else:
                    if sending_data["verdict"] is None:
                        sending_data["verdict"] = data["status"]
                        sending_data["info_test"] = data["output"]
                        sending_data["num"] = test["num"]

        if sending_data["verdict"] is None:
            sending_data["verdict"] = "accepted"

        if sending_data["verdict"] == "accepted":
            show_message(self.page, "Ваш код принят!", "success")
            self.status = 1
            self.animate_status(1)

        elif sending_data["verdict"] != "accepted":
            show_message(self.page, "Ваш код не принят!", "error")

        elif self.status != 1:
            self.status = -1
            self.animate_status(-1)

        db_manager.save_solution(**sending_data)

        get_data()
        self.controls_row.controls[1].selected = {"2"}
        self.controls_row.controls[1].update()
        self.page.update()
        self.change_right_content(None)

        # current_tests_data[test['num']] = {''}

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        # filename = e.files[0].split('//')[-1]
        self.patch_to_file = e.files[0].path
        self.filename = e.files[0].name

        self.send_btn.text = f"отправить - {self.filename}"
        self.send_btn.disabled = False

        self.filepick_btn.update()
        self.send_btn.update()
        self.page.update()

    def update_tests_data(self):
        get_data()
        self.sendings_panel.controls.clear()
        # status_row = ft.Row()
        for send_id, send in SENDINGS_DATA.items():
            header_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            content_container = ft.Container(margin=0, padding=5)

            if send.task_id != self.id:
                continue
            if send.author != CURRENT_USER_ID:
                continue

            if send.verdict == "accepted":
                header_row.controls = [
                    ft.Container(
                        width=200,
                        # alignment = 'center',
                        border=ft.border.all(1.5, ft.colors.GREEN_400),
                        border_radius=10,
                        padding=6,
                        margin=ft.margin.only(left=20, top=5, right=5, bottom=5),
                        content=ft.Text(
                            "Accepted",
                            color=ft.colors.GREEN_700,
                            font_family="Consolas",
                            weight=110,
                            text_align="center",
                        ),
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    str(send.accepted_tests),
                                    color=ft.colors.WHITE54,
                                    weight=ft.FontWeight.W_400,
                                ),
                                ft.Text(
                                    "/" + str(send.total_tests), color=ft.colors.WHITE12
                                ),
                            ]
                        )
                    ),
                    ft.Text(
                        send.time,
                        font_family="Consolas",
                        color=ft.colors.WHITE24,
                    ),
                ]

            else:
                header_row.controls = [
                    ft.Container(
                        width=200,
                        # alignment = 'center',
                        border=ft.border.all(1.5, ft.colors.RED_600),
                        border_radius=10,
                        padding=6,
                        margin=ft.margin.only(left=20, top=5, right=5, bottom=5),
                        content=ft.Text(
                            send.verdict,
                            color=ft.colors.RED_700,
                            font_family="Consolas",
                            weight=110,
                            text_align="center",
                        ),
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    str(send.accepted_tests),
                                    color=ft.colors.WHITE54,
                                    weight=ft.FontWeight.W_400,
                                ),
                                ft.Text(
                                    "/" + str(send.total_tests), color=ft.colors.WHITE12
                                ),
                            ]
                        )
                    ),
                    ft.Text(
                        send.time,
                        font_family="Consolas",
                        color=ft.colors.WHITE24,
                    ),
                ]

            content_container.content = ft.Column(
                controls=[
                    # ft.Row(
                    #     alignment = ft.MainAxisAlignment.END,
                    #     controls=[
                    #     ],
                    # ),
                    ft.Stack(
                        controls=[
                            ft.Markdown(
                                "\n\n```dart\n" + send.code + "\n```",
                                selectable=True,
                                extension_set="gitHubWeb",
                                code_theme="atom-one-dark",
                                code_style=ft.TextStyle(font_family="Roboto Mono"),
                            ),
                            ft.IconButton(
                                # offset = (0, 0.5),
                                top=0,
                                right=0.9,
                                icon=ft.icons.COPY_ROUNDED,
                                icon_size=14,
                                icon_color="white40",
                                tooltip="copy",
                                on_click=lambda e, text=send.code: copy_to_clipboard(
                                    text
                                ),
                            ),
                        ]
                    )
                ]
            )

            if send.verdict != "Wrong Answer":
                message_text = str(send.info_test)
            else:
                dt = send.info_test.split("~")
                message_text = (
                    "Expected output:"
                    + "\n\n"
                    + dt[1]
                    + "\n\n"
                    + "Actual output:"
                    + "\n\n"
                    + dt[3]
                )

            info_container = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        border=ft.border.all(1.5, ft.colors.RED_400),
                        border_radius=10,
                        padding=5,
                        margin=ft.margin.only(left=20),
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    value="Ошибка на тесте №",
                                    font_family="Consolas",
                                    color=ft.colors.WHITE60,
                                    text_align="center",
                                    weight=80,
                                ),
                                ft.Text(
                                    value=str(send.num),
                                    font_family="Consolas",
                                    text_align="center",
                                    color=ft.colors.WHITE60,
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        border=ft.border.all(1.5, ft.colors.RED_400),
                        border_radius=10,
                        padding=5,
                        margin=ft.margin.only(left=20, right=20),
                        content=ft.Row(
                            wrap=True,
                            controls=[
                                ft.Text(
                                    value="Сообщение:",
                                    font_family="Consolas",
                                    color=ft.colors.WHITE60,
                                    text_align="center",
                                    weight=80,
                                ),
                                ft.Container(
                                    bgcolor=ft.colors.WHITE70,
                                    width=1,
                                    margin=0,
                                    padding=0,
                                    height=60 if send.verdict == "Wrong Answer" else 10,
                                ),
                                ft.Text(
                                    value=message_text,
                                    font_family="Consolas",
                                    text_align="center",
                                    color=ft.colors.WHITE60,
                                ),
                            ],
                        ),
                    ),
                ],
            )

            if send.verdict != "accepted":
                content_container.content.controls.insert(0, info_container)

            send_card = ft.ExpansionPanel(
                header=header_row,
                bgcolor="#37474f",
                content=content_container,
            )

            self.sendings_panel.controls.append(send_card)

        # self.sendings_panel.update()

        self.sendings_panel.controls = self.sendings_panel.controls[::-1]
        self.page.update()

    def change_left_content(self, e):
        if self.controls_row.controls[0].selected == {"1"}:
            self.left_column.content = self.description_content
        else:
            self.left_column.content = self.inpout_content

        self.left_column.update()
        self.page.update()

    def change_right_content(self, e):
        if self.controls_row.controls[1].selected == {"1"}:
            self.right_column.content = self.code_editor
        else:
            self.right_column.content = self.tests_content
            self.update_tests_data()

        self.right_column.update()
        self.page.update()

    def namehover(self, e):
        if e.data == "true":
            self.NAME_ROW.controls[0].scale = 1.014

            self.NAME_ROW.update()
            self.page.update()
        else:
            self.NAME_ROW.controls[0].scale = 1

            self.NAME_ROW.update()
            self.page.update()

    def deschover(self, e):
        if e.data == "true":
            self.left_column.content.scale = 1.014
            self.left_column.update()
            self.page.update()
        else:
            self.left_column.content.scale = 1
            self.left_column.update()
            self.page.update()

    def tablehover(self, e):
        if e.data == "true":
            self.inpout_content.controls[2].scale = 1.014
            self.inpout_content.controls[2].update()
            self.page.update()
        else:
            self.inpout_content.controls[2].scale = 1
            self.inpout_content.controls[2].update()
            self.page.update()

    def inphover(self, e):
        if e.data == "true":
            self.inpout_content.controls[0].scale = 1.014
            self.inpout_content.controls[0].update()
            self.page.update()
        else:
            self.inpout_content.controls[0].scale = 1
            self.inpout_content.controls[0].update()
            self.page.update()

    def outhover(self, e):
        if e.data == "true":
            self.inpout_content.controls[1].scale = 1.014
            self.inpout_content.controls[1].update()
            self.page.update()
        else:
            self.inpout_content.controls[1].scale = 1
            self.inpout_content.controls[1].update()
            self.page.update()

    def build(self) -> ft.Column:
        return ft.Column(
            alignment=ft.alignment.top_center,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            animate_offset=ft.animation.Animation(350, "decelerate"),
            offset=ft.transform.Offset(0, 0),
            horizontal_alignment="center",
            controls=[
                self.NAME_ROW,
                self.description_row,
                self.controls_row,
            ],
        )


class GroupsManager(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self) -> ft.GridView:
        global get_data
        get_data()
        global GROUPS_DATA

        themes = ft.GridView(
            expand=1,
            runs_count=4,
            max_extent=400,
            child_aspect_ratio=2,
            spacing=4,
            run_spacing=50,
            # alig
        )

        if GROUPS_DATA:
            for ind, group in GROUPS_DATA.items():
                crt = GroupCard(
                    title=group["name"],
                    leading=group["icon"],
                    subtitle=group["description"],
                    id=ind,
                )

                themes.controls.append(crt)
        else:
            crt = GroupCard(
                title="you are not yet a member of any group",
                leading=ft.icons.CENTER_FOCUS_STRONG_ROUNDED,
                subtitle="you can join a group on the groups tab",
                id="wtf?",
            )
            # crt
            crt.width = 600
            themes.controls.append(crt)

        return themes


class ManagerGroupCard(ft.UserControl):
    def __init__(self, leading, title, subtitle, id):
        super().__init__()
        self.id = id

        self.card = ft.Card(
            elevation=0.9,
            height=200,
            width=400,
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                # on_click=(
                #     self.go
                #     if self.id != "wtf?"
                #     else lambda _: self.page.go("/app~student/groups-manager")
                # ),
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.ListTile(
                    leading=ft.Icon(leading),
                    title=ft.Text(title, font_family="Consolas", text_align="left"),
                    subtitle=ft.Text(
                        subtitle, font_family="Consolas", text_align="left"
                    ),
                ),
            ),
        )

        self.func = None
        self.on_delete_selected = False

        self.dlg_modal = ft.AlertDialog(
            # bgcolor = ft.colors.with_opacity(0.045, 'white'),
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Уверенны?",
                        text_align="center",
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            # content=ft.Text(
            #     "Вы уверены что хотите выйти из группы?", text_align="center"
            # ),
            actions=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.ElevatedButton(
                            text="Выйти из группы",
                            color=ft.colors.RED_600,
                            icon=ft.icons.LOGOUT_ROUNDED,
                            on_click=lambda _: self.close_dlg(1),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="Отмена",
                            color=ft.colors.WHITE30,
                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                            on_click=lambda _: self.close_dlg(0),
                            expand=True,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.content = ft.Stack(
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=self.card,
                ),
                ft.IconButton(
                    icon=ft.icons.HIGHLIGHT_REMOVE_ROUNDED,
                    icon_color=ft.colors.RED_600,
                    on_click=self.anim_on_delete,
                    right=0.9,
                    bottom=0.9,
                ),
            ],
        )

    def go(self, e):
        global CURRENT_GROUP_ID
        CURRENT_GROUP_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.controls[0].controls[1].content.on_animation_end = (
            lambda _: self.page.go("/app~student/themes")
        )
        self.page.update()

    def anim_on_delete(self, e):
        self.open_dlg_modal()

        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected:
            self.content.rotate.angle += 0.05
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle -= 0.10
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle = 0
            self.content.update()
            self.page.update()

        self.content.rotate.angle = 0

        self.content.update()
        self.page.update()

    def close_dlg(self, type):
        if type == 1:

            groups = db_manager.session.query(UserGroup).all()
            for grp in groups:
                if grp.user_id == CURRENT_USER_ID and grp.group_id == self.id:
                    show_message(self.page, "вы вышли из группы")
                    self.close_dlg(0)
                    db_manager.session.delete(grp)
                    db_manager.session.commit()

                    self.on_delete_selected = False
                    self.func()

                    self.page.update()

        else:
            self.on_delete_selected = False
        self.dlg_modal.open = False
        # self.page.update()

    def open_dlg_modal(self):
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()

    def anim(self, e):
        if e.data == "true":

            self.card.elevation = 8
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.content


class ManagerNewGroupCard(ft.UserControl):
    def __init__(self, leading, title, subtitle, id):
        super().__init__()
        self.id = id

        self.card = ft.Card(
            elevation=0.9,
            height=200,
            width=400,
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.ListTile(
                    leading=ft.Icon(leading),
                    title=ft.Text(title, font_family="Consolas", text_align="left"),
                    subtitle=ft.Text(
                        subtitle, font_family="Consolas", text_align="left"
                    ),
                ),
            ),
        )

        self.func = None
        self.on_delete_selected = False

        self.dlg_modal = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Вступить?",
                        text_align="center",
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.ElevatedButton(
                            text="Вступить в группу",
                            color=ft.colors.GREEN_600,
                            icon=ft.icons.ADD_ROUNDED,
                            on_click=lambda _: self.close_dlg(1),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="Отмена",
                            color=ft.colors.WHITE30,
                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                            on_click=lambda _: self.close_dlg(0),
                            expand=True,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.content = ft.Stack(
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=self.card,
                ),
                ft.IconButton(
                    icon=ft.icons.ADD_ROUNDED,
                    icon_color=ft.colors.GREEN_600,
                    on_click=self.anim_on_delete,
                    right=0.9,
                    bottom=0.9,
                ),
            ],
        )

    def go(self, e):
        global CURRENT_GROUP_ID
        CURRENT_GROUP_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.controls[0].controls[1].content.on_animation_end = (
            lambda _: self.page.go("/app~student/themes")
        )
        self.page.update()

    def anim_on_delete(self, e):
        self.open_dlg_modal()

        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected:
            self.content.rotate.angle += 0.05
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle -= 0.10
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle = 0
            self.content.update()
            self.page.update()

        self.content.rotate.angle = 0

        self.content.update()
        self.page.update()

    def close_dlg(self, type):
        if type == 1:
            db_manager.add_user_to_group(user_id=CURRENT_USER_ID, group_id=self.id)
            show_message(self.page, "вы вступили в группу", "success")
            self.on_delete_selected = False
            self.dlg_modal.open = False

            self.close_dlg(0)
            self.func()
            self.page.update()

        else:
            self.on_delete_selected = False

        self.dlg_modal.open = False
        self.page.update()

    def open_dlg_modal(self):
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()

    def anim(self, e):
        if e.data == "true":

            self.card.elevation = 8
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.content


class GroupsEditPage(ft.UserControl):
    def __init__(self):
        super().__init__()
        groups_data = db_manager.session.query(Group).all()
        users_data = [
            grp.group_id
            for grp in db_manager.session.query(UserGroup)
            .filter(UserGroup.user_id == CURRENT_USER_ID)
            .all()
        ]
        my_groups = {}
        off_groups = {}

        for group in groups_data:
            if group.ID in users_data:
                my_groups[group.ID] = group
            else:
                off_groups[group.ID] = group

        self.my_groups_container = ft.GridView(
            # height=340,
            runs_count=4,
            max_extent=400,
            child_aspect_ratio=2,
            spacing=4,
            run_spacing=50,
            controls=[],
        )

        self.off_groups_container = ft.GridView(
            # height=340,
            runs_count=4,
            max_extent=400,
            child_aspect_ratio=2,
            spacing=4,
            run_spacing=50,
            controls=[],
        )

        def delete_func():
            self.my_groups_container.controls.clear()
            self.off_groups_container.controls.clear()

            db_manager = DatabaseManager(uri)

            groups_data = db_manager.session.query(Group).all()
            users_data = [
                grp.group_id
                for grp in db_manager.session.query(UserGroup)
                .filter(UserGroup.user_id == CURRENT_USER_ID)
                .all()
            ]
            my_groups = {}
            off_groups = {}

            for group in groups_data:
                if group.ID in users_data:
                    my_groups[group.ID] = group
                else:
                    off_groups[group.ID] = group

            for grp_id, grp in my_groups.items():
                crd = ManagerGroupCard(
                    leading=grp.description.split("|")[2],
                    title=grp.description.split("|")[0],
                    subtitle=grp.description.split("|")[1],
                    id=grp_id,
                )

                crd.func = delete_func
                self.my_groups_container.controls.append(crd)

            for grp_id, grp in off_groups.items():
                crd = ManagerNewGroupCard(
                    leading=grp.description.split("|")[2],
                    title=grp.description.split("|")[0],
                    subtitle=grp.description.split("|")[1],
                    id=grp_id,
                )

                crd.func = delete_func
                self.off_groups_container.controls.append(crd)

            self.off_groups_container.update()
            self.my_groups_container.update()
            self.page.update()

        # def update_new_func():

        for grp_id, grp in my_groups.items():
            crd = ManagerGroupCard(
                leading=grp.description.split("|")[2],
                title=grp.description.split("|")[0],
                subtitle=grp.description.split("|")[1],
                id=grp_id,
            )

            crd.func = delete_func
            self.my_groups_container.controls.append(crd)

        for grp_id, grp in off_groups.items():
            crd = ManagerNewGroupCard(
                leading=grp.description.split("|")[2],
                title=grp.description.split("|")[0],
                subtitle=grp.description.split("|")[1],
                id=grp_id,
            )

            crd.func = delete_func
            self.off_groups_container.controls.append(crd)

    def build(self) -> ft.Column:

        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            animate_offset=ft.animation.Animation(350, "decelerate"),
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Text(
                                "Редактор групп".upper(),
                                font_family="Consolas",
                                size=18,
                                text_align="center",
                                weight=110,
                            ),
                            border_radius=10,
                            padding=10,
                            bgcolor="#2a3139",
                        )
                    ]
                ),
                ft.Divider(height=25, color="transparent"),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Text(
                            size=20,
                            font_family="Consolas",
                            value="Мои Группы:",
                        ),
                    ],
                ),
                self.my_groups_container,
                ft.Divider(height=1, color="white40"),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Text(
                            size=20,
                            font_family="Consolas",
                            value="Доступные Группы:",
                        ),
                    ],
                ),
                self.off_groups_container,
            ],
        )


class ManagerGroupCardTeacher(ft.UserControl):
    def __init__(self, leading, title, subtitle, id):
        super().__init__()
        self.id = id

        self.card = ft.Card(
            elevation=0.9,
            height=200,
            width=400,
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                on_click=(
                    self.go
                    # if self.id != "wtf?"
                    # else lambda _: self.page.go("/app~student/groups-manager")
                ),
                # on_animation_end=lambda _: self.page.go("/app~teacher/themes"),
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.ListTile(
                    leading=ft.Icon(leading),
                    title=ft.Text(title, font_family="Consolas", text_align="left"),
                    subtitle=ft.Text(
                        subtitle, font_family="Consolas", text_align="left"
                    ),
                ),
            ),
        )

        self.func = func
        self.on_delete_selected = False

        self.dlg_modal_edit = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Редактировать описание",
                        text_align="center",
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.END,
                    height=380,
                    controls=[
                        ft.TextField(
                            label="Название\n",
                            value=self.card.content.content.title.value,
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=20,
                            text_size=18,
                            hint_text="Название вашей группы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.TextField(
                            label="Описание\n",
                            value=self.card.content.content.subtitle.value,
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=150,
                            text_size=18,
                            border=ft.InputBorder.UNDERLINE,
                            multiline=True,
                            min_lines=1,
                            max_lines=3,
                            # filled=True,
                            hint_text="Описание вашей группы",
                        ),
                        ft.TextField(
                            prefix_text="ft.icons.",
                            label="Иконка\n",
                            value=self.card.content.content.leading.name,
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            text_size=18,
                            hint_text="Иконка вашей группы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            expand=True,
                            controls=[
                                ft.ElevatedButton(
                                    text="Сохранить",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.SAVE_ALT_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1, 1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0, 1),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.dlg_modal_delete = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Уверенны?",
                        text_align="center",
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.ElevatedButton(
                            text="Удалить группу",
                            color=ft.colors.RED_600,
                            icon=ft.icons.LOGOUT_ROUNDED,
                            on_click=lambda _: self.close_dlg(1),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="Отмена",
                            color=ft.colors.WHITE30,
                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                            on_click=lambda _: self.close_dlg(0),
                            expand=True,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.content = ft.Stack(
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=self.card,
                ),
                ft.IconButton(
                    icon=ft.icons.EDIT_ROUNDED,
                    icon_color=ft.colors.GREEN_300,
                    on_click=self.anim_on_edit,
                    right=0.9,
                    bottom=0.9,
                ),
                ft.IconButton(
                    icon=ft.icons.HIGHLIGHT_REMOVE_ROUNDED,
                    icon_color=ft.colors.RED_600,
                    on_click=self.anim_on_delete,
                    right=0.9,
                    offset=(-0.9, 0),
                    bottom=0.9,
                ),
            ],
        )

    def go(self, e):
        global CURRENT_GROUP_ID
        CURRENT_GROUP_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.update()
        self.page.go("/app~teacher/themes")

    def anim_on_delete(self, e):
        self.open_dlg_modal()

        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected:
            self.content.rotate.angle += 0.05
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle -= 0.10
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle = 0
            self.content.update()
            self.page.update()

        self.content.rotate.angle = 0

        self.content.update()
        self.page.update()

    def anim_on_edit(self, e):
        self.open_dlg_modal(type=1)

        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected:
            self.content.rotate.angle += 0.05
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle -= 0.10
            self.content.update()
            self.page.update()

            time.sleep(0.1)
            self.content.rotate.angle = 0
            self.content.update()
            self.page.update()

        self.content.rotate.angle = 0

        self.content.update()
        self.page.update()

    def close_dlg(self, type, dlg_type=0):
        if dlg_type == 0:
            if type == 1:
                groups = db_manager.session.query(Group).all()
                for grp in groups:
                    if grp.leader == CURRENT_USER_ID and grp.ID == self.id:
                        show_message(self.page, "группа удалена")
                        self.close_dlg(0)
                        db_manager.session.delete(grp)
                        db_manager.session.commit()

                        self.on_delete_selected = False
                        self.func()

            else:
                self.on_delete_selected = False
            self.dlg_modal_delete.open = False

        else:
            if type == 1:
                groups = db_manager.session.query(Group).all()
                for grp in groups:
                    if grp.leader == CURRENT_USER_ID and grp.ID == self.id:
                        description = (
                            self.dlg_modal_edit.actions[0].controls[0].value
                            + "|"
                            + self.dlg_modal_edit.actions[0].controls[1].value
                            + "|"
                            + self.dlg_modal_edit.actions[0].controls[2].value
                        )
                        show_message(self.page, "группа", "success")
                        self.close_dlg(0, 1)

                        grp.description = description
                        db_manager.session.commit()

                        self.on_delete_selected = False
                        self.func()

            else:
                self.on_delete_selected = False

            self.dlg_modal_edit.open = False

    def open_dlg_modal(self, type=0):

        if type == 0:
            self.page.dialog = self.dlg_modal_delete
            self.dlg_modal_delete.open = True
        else:
            self.page.dialog = self.dlg_modal_edit
            self.dlg_modal_edit.open = True

        self.page.update()

    def anim(self, e):
        if e.data == "true":

            self.card.elevation = 8
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.content


class GroupsEditTeacherPage(ft.UserControl):
    def __init__(self):
        super().__init__()
        groups_data = db_manager.session.query(Group).all()
        users_data = [
            grp.group_id
            for grp in db_manager.session.query(UserGroup).filter(
                UserGroup.user_id == CURRENT_USER_ID
            )
        ]
        my_groups = {}

        for group in groups_data:
            if group.leader == CURRENT_USER_ID:
                my_groups[group.ID] = group

        self.my_groups_container = ft.GridView(
            # height=340,
            runs_count=4,
            max_extent=400,
            child_aspect_ratio=2,
            spacing=4,
            run_spacing=50,
            controls=[],
        )

        def delete_func():
            self.my_groups_container.controls.clear()

            db_manager = DatabaseManager(uri)

            groups_data = db_manager.session.query(Group).all()
            users_data = [
                grp.group_id
                for grp in db_manager.session.query(UserGroup)
                .filter(UserGroup.user_id == CURRENT_USER_ID)
                .all()
            ]
            my_groups = {}

            for group in groups_data:
                if group.leader == CURRENT_USER_ID:
                    my_groups[group.ID] = group

            for grp_id, grp in my_groups.items():
                crd = ManagerGroupCardTeacher(
                    leading=grp.description.split("|")[2],
                    title=grp.description.split("|")[0],
                    subtitle=grp.description.split("|")[1],
                    id=grp_id,
                )

                crd.func = delete_func
                self.my_groups_container.controls.append(crd)

            self.my_groups_container.update()
            self.page.update()

        global func
        func = delete_func

        for grp_id, grp in my_groups.items():
            crd = ManagerGroupCardTeacher(
                leading=grp.description.split("|")[2],
                title=grp.description.split("|")[0],
                subtitle=grp.description.split("|")[1],
                id=grp_id,
            )

            crd.func = delete_func
            self.my_groups_container.controls.append(crd)

        self.dlg_modal_new = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Создать группу",
                        text_align="center",
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.END,
                    height=380,
                    controls=[
                        ft.TextField(
                            label="Название\n",
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=20,
                            text_size=18,
                            hint_text="Название вашей группы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.TextField(
                            label="Описание\n",
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=150,
                            text_size=18,
                            border=ft.InputBorder.UNDERLINE,
                            multiline=True,
                            min_lines=1,
                            max_lines=3,
                            # filled=True,
                            hint_text="Описание вашей группы",
                        ),
                        ft.TextField(
                            prefix_text="ft.icons.",
                            label="Иконка\n",
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            text_size=18,
                            hint_text="Иконка вашей группы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            expand=True,
                            controls=[
                                ft.ElevatedButton(
                                    text="Cоздать",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.ADD_TASK_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.add_new_group_btn = ft.ElevatedButton(
            on_click=lambda _: self.add_new_group(),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(150, ft.AnimationCurve.BOUNCE_OUT),
            height=45,
            width=185,
            content=ft.Row(
                alignment="center",
                controls=(
                    ft.Icon(
                        ft.icons.ADD_ROUNDED, color="green", size=26, offset=(-0.6, 0)
                    ),
                    ft.Text(
                        "Создать группу",
                        font_family="Consolas",
                        size=15,
                        color="green",
                        text_align="center",
                        offset=(-0.15, 0),
                    ),
                ),
            ),
            #    border_radius = 10,
        )

    def close_dlg(self, type):
        # global delete_func
        if type == 1:
            description = (
                self.dlg_modal_new.actions[0].controls[0].value
                + "|"
                + self.dlg_modal_new.actions[0].controls[1].value
                + "|"
                + self.dlg_modal_new.actions[0].controls[2].value
            )
            show_message(self.page, "Группа создана", "success")
            db_manager.create_group(leader_id=CURRENT_USER_ID, description=description)
            groups = db_manager.session.query(Group).all()
            id = groups[-1].ID

            crd = ManagerGroupCardTeacher(
                leading=description.split("|")[2],
                title=description.split("|")[0],
                subtitle=description.split("|")[1],
                id=id,
            )

            crd.func = func
            self.my_groups_container.controls.append(crd)
            self.my_groups_container.update()
            self.page.update()

        self.dlg_modal_new.open = False
        self.page.update()

    def hover_group_btn(self, e):
        if e.data == "true":
            self.add_new_group_btn.elevation = 10
        else:
            self.add_new_group_btn.elevation = 4
        self.add_new_group_btn.update()
        self.page.update()

    def add_new_group(self):
        self.page.dialog = self.dlg_modal_new
        self.dlg_modal_new.open = True

        self.add_new_group_btn.rotate.angle += 0.06
        self.add_new_group_btn.update()
        self.page.update()

        time.sleep(0.1)
        self.add_new_group_btn.rotate.angle -= 0.12
        self.add_new_group_btn.update()
        self.page.update()

        time.sleep(0.1)
        self.add_new_group_btn.rotate.angle = 0
        self.add_new_group_btn.update()
        self.page.update()

    def build(self) -> ft.Column:

        return ft.Column(
            animate_offset=(ft.animation.Animation(350, "decelerate")),
            offset=(0, 0),
            on_animation_end=lambda _: self.page.go("/app~teacher/themes"),
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Text(
                                "Редактор групп".upper(),
                                font_family="Consolas",
                                size=18,
                                text_align="center",
                                weight=110,
                            ),
                            border_radius=10,
                            padding=10,
                            bgcolor="#2a3139",
                        )
                    ]
                ),
                ft.Divider(height=25, color="transparent"),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.Text(
                            size=20,
                            font_family="Consolas",
                            value="Мои Группы:",
                        ),
                    ],
                ),
                self.my_groups_container,
                ft.Divider(height=1, color="white40"),
                ft.Row(
                    alignment="center",
                    controls=[
                        self.add_new_group_btn,
                    ],
                ),
            ],
        )


class ThemeTeacherCard(ft.UserControl):
    def __init__(self, name, description, color="bluegrey900", id=0, parent=None):
        super().__init__()
        self.id = id
        self.name = name
        self.description = description
        self.color = color
        self.parent = parent

        self.dlg_delete = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Вы хотите удалить эту тему?",
                        size=18,
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.ElevatedButton(
                            text="Удалить тему",
                            color=ft.colors.RED_600,
                            icon=ft.icons.DELETE_ROUNDED,
                            on_click=lambda _: self.close_dlg(1, 0),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="Отмена",
                            color=ft.colors.WHITE30,
                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                            on_click=lambda _: self.close_dlg(0, 0),
                            expand=True,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.on_delete_selected = False

        self.edit_btn = ft.IconButton(
            icon=ft.icons.EDIT_ROUNDED,
            icon_size=30,
            icon_color=ft.colors.GREEN_600,
            on_click=lambda _: self.edit(),
        )
        self.delete_btn = ft.IconButton(
            icon=ft.icons.DELETE_ROUNDED,
            icon_size=30,
            icon_color=ft.colors.RED_600,
            on_click=lambda _: self.delete(),
        )

        self.card = ft.Card(
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            elevation=0.9,
            animate_scale=ft.animation.Animation(200, "decelerate"),
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                height=120,
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(0.1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.Row(
                    expand=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            on_click=self.go,
                            alignment=ft.alignment.top_left,
                            expand=16,
                            height=120,
                            content=ft.Row(
                                controls=[
                                    ft.ListTile(
                                        expand=1,
                                        title=ft.Text(
                                            name,
                                            font_family="Consolas",
                                            text_align="topleft",
                                            height=30,
                                        ),
                                        subtitle=ft.Text(
                                            description,
                                            font_family="Consolas",
                                            text_align="left",
                                        ),
                                    ),
                                ]
                            ),
                        ),
                        ft.Container(
                            # alignment=ft.alignment.bottom_left,
                            height=100,
                            width=2,
                            margin=ft.margin.only(top=10),
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                        ),
                        ft.Container(
                            expand=1,
                            padding=ft.padding.only(top=10),
                            content=ft.Column(
                                controls=[
                                    self.edit_btn,
                                    self.delete_btn,
                                ]
                            ),
                        ),
                    ],
                ),
            ),
        )

        self.dlg_edit = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Редактировать описание",
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                        size=18,
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.END,
                    height=300,
                    controls=[
                        ft.TextField(
                            label="Название\n",
                            value=name,
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=20,
                            text_size=18,
                            hint_text="Название вашей группы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.TextField(
                            label="Описание\n",
                            value=description,
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=150,
                            text_size=18,
                            border=ft.InputBorder.UNDERLINE,
                            multiline=True,
                            min_lines=1,
                            max_lines=3,
                            # filled=True,
                            hint_text="Описание вашей группы",
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            expand=True,
                            controls=[
                                ft.ElevatedButton(
                                    text="Сохранить",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.SAVE_ALT_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1, 1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0, 1),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def edit(self):
        self.dlg_edit.open = True
        self.page.dialog = self.dlg_edit

    def delete(self):
        self.dlg_delete.open = True
        self.page.dialog = self.dlg_delete
        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected:
            self.card.rotate.angle += 0.005
            self.card.update()
            self.page.update()

            time.sleep(0.1)
            self.card.rotate.angle -= 0.010
            self.card.update()
            self.page.update()

            time.sleep(0.1)
            self.card.rotate.angle = 0
            self.card.update()
            self.page.update()

        self.card.rotate.angle = 0

        self.card.update()
        self.page.update()

    def go(self, e):
        if self.dlg_delete.open:
            return

        global CURRENT_THEME_ID
        CURRENT_THEME_ID = self.id
        self.page.controls[0].controls[1].content.offset = ft.transform.Offset(-1, 0)
        self.page.controls[0].controls[1].content.update()
        self.page.controls[0].controls[1].content.on_animation_end = (
            lambda _: self.page.go("/app~teacher/tasks")
        )
        self.page.update()

    def close_dlg(self, type, par):
        if par == 0:
            self.on_delete_selected = False
            self.dlg_delete.open = False
            self.page.update()

            if type == 1:
                db_manager.remove_theme(theme_id=self.id)
                self.page.controls[0].controls[1].content.controls[
                    2
                ] = ThemesTeacherPage()
                self.page.controls[0].controls[1].content.update()

        if par == 1:
            self.dlg_edit.open = False
            self.page.update()

            if type == 1:
                db_manager.update_theme(
                    theme_id=self.id,
                    new_description=self.dlg_edit.actions[0].controls[0].value
                    + "|"
                    + self.dlg_edit.actions[0].controls[1].value,
                )
                self.page.controls[0].controls[1].content.controls[
                    2
                ] = ThemesTeacherPage()
                self.page.controls[0].controls[1].content.update()

                # self.page.update()

    def anim(self, e):
        if e.data == "true":
            self.card.elevation = 8
            self.card.scale = 1.009
            self.card.update()
            self.page.update()
        else:
            self.card.elevation = 0.9
            self.card.scale = 1
            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.card


# button_back_style: dict = {
#     "bgcolor": "transparent",
#     "top": 8,
# }


# class BackButton(ft.IconButton):
#     def __init__(self, size) -> None:
#         super().__init__(
#             **button_back_style,
#             icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
#             tooltip="Back",
#             icon_size=size,
#         )


class ThemesTeacherPage(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        # self.back = BackButton(size=13)
        self.add_theme_dlg = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Создать тему",
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.END,
                    height=300,
                    controls=[
                        ft.TextField(
                            label="Название\n",
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=20,
                            text_size=18,
                            hint_text="Название новой темы",
                            border=ft.InputBorder.UNDERLINE,
                        ),
                        ft.TextField(
                            label="Описание\n",
                            label_style=ft.TextStyle(
                                font_family="Consolas",
                                size=16,
                                shadow=ft.BoxShadow(
                                    color=ft.colors.BLACK87,
                                    blur_radius=1,
                                ),
                            ),
                            max_length=150,
                            text_size=18,
                            border=ft.InputBorder.UNDERLINE,
                            multiline=True,
                            min_lines=1,
                            max_lines=3,
                            # filled=True,
                            hint_text="Описание новой темы",
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            expand=True,
                            controls=[
                                ft.ElevatedButton(
                                    text="Cоздать",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.ADD_TASK_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.add_new_theme_btn = ft.ElevatedButton(
            on_click=lambda _: self.add_new_theme(),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(150, ft.AnimationCurve.BOUNCE_OUT),
            height=45,
            width=185,
            content=ft.Row(
                alignment="center",
                controls=(
                    ft.Icon(
                        ft.icons.ADD_ROUNDED, color="green", size=26, offset=(-0.6, 0)
                    ),
                    ft.Text(
                        "Добавить тему",
                        font_family="Consolas",
                        size=15,
                        color="green",
                        text_align="center",
                        offset=(-0.15, 0),
                    ),
                ),
            ),
        )

        # self.page.update()

    def build(self):
        get_data()
        themes = ft.Column(
            expand=1,
            scroll=ft.ScrollMode.HIDDEN,
            horizontal_alignment="center",
        )

        if THEMES_DATA:
            for theme_id, theme in THEMES_DATA.items():
                total, acc = 0, 0
                for task_id, task in TASKS_DATA.items():
                    if task["theme_id"] != theme_id:
                        continue
                    if (
                        task["accepted_tests"] == task["total_tests"]
                        and task["total_tests"] != 0
                    ):
                        acc += 1
                    total += 1

                progress = acc / total if total > 0 else 0
                cnt = ThemeTeacherCard(
                    name=theme["description"].split("|")[0],
                    description=theme["description"].split("|")[1],
                    id=theme_id,
                    parent=self,
                )
                themes.controls.append(cnt)

        themes.controls.append(self.add_new_theme_btn)
        return themes

    def add_new_theme(self):
        self.add_theme_dlg.open = True
        self.page.dialog = self.add_theme_dlg
        self.page.update()

    def close_dlg(self, type):
        self.add_theme_dlg.open = False
        self.page.update()

        if type == 1:
            db_manager.create_theme(
                group_id=CURRENT_GROUP_ID,
                description=self.add_theme_dlg.actions[0].controls[0].value
                + "|"
                + self.add_theme_dlg.actions[0].controls[1].value,
            )
            self.page.controls[0].controls[1].content.controls[2] = ThemesTeacherPage()
            self.page.controls[0].controls[1].content.update()


class TaskTeacherCard(ft.UserControl):
    def __init__(self, name, color="bluegrey900", id=0, par=None, description=None):
        super().__init__()
        self.id = id
        self.description = description
        self.par = par
        self.name = name
        self.func = None
        self.icon = ft.Icon(ft.icons.CIRCLE_ROUNDED)
        self.icon.color = "#37474f"
        self.icon.animate_scale = ft.animation.Animation(200, "decelerate")

        self.edit_btn = ft.IconButton(
            icon=ft.icons.EDIT_ROUNDED,
            icon_size=30,
            icon_color=ft.colors.GREEN_600,
            on_click=lambda _: self.edit(),
        )
        self.delete_btn = ft.IconButton(
            icon=ft.icons.DELETE_ROUNDED,
            icon_size=30,
            icon_color=ft.colors.RED_600,
            on_click=lambda e: self.delete(),
        )

        self.dlg_delete = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Вы хотите удалить эту задачу?",
                        size=18,
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.ElevatedButton(
                            text="Удалить задачу",
                            color=ft.colors.RED_600,
                            icon=ft.icons.DELETE_ROUNDED,
                            on_click=lambda _: self.close_dlg(1, 0),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="Отмена",
                            color=ft.colors.WHITE30,
                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                            on_click=lambda _: self.close_dlg(0, 0),
                            expand=True,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.on_delete_selected = 0

        self.card = ft.Card(
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            elevation=0.9,
            animate_scale=ft.animation.Animation(200, "decelerate"),
            margin=ft.margin.only(left=10, right=30, top=10),
            shadow_color=ft.colors.BLACK87,
            content=ft.Container(
                height=60,
                border_radius=ft.border_radius.all(10),
                border=ft.border.all(0.1, ft.colors.BLACK12),
                on_hover=self.anim,
                content=ft.Row(
                    expand=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            on_click=self.go_to_task,
                            alignment=ft.alignment.center_left,
                            expand=10,
                            height=60,
                            content=ft.Row(
                                controls=[
                                    ft.ListTile(
                                        leading=self.icon,
                                        expand=1,
                                        title=ft.Text(
                                            name,
                                            font_family="Consolas",
                                            text_align="topleft",
                                            size=17,
                                        ),
                                    ),
                                ]
                            ),
                        ),
                        ft.Container(
                            height=40,
                            width=2,
                            margin=ft.margin.only(top=5),
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                        ),
                        ft.Container(
                            expand=1,
                            padding=ft.padding.only(top=5),
                            content=ft.Row(
                                controls=[
                                    self.edit_btn,
                                    self.delete_btn,
                                ]
                            ),
                        ),
                    ],
                ),
            ),
        )

        self.TLcontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 0),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            # size=12,
            expand=3,
            margin=0,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            padding=ft.padding.only(left=8, top=2, bottom=2, right=1),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Time limit:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="ограничения по времени(секунд)",
                        border_color="transparent",
                        # width=150,
                        expand=True,
                        value=self.description.split("|")[5]
                        .replace("(", "")
                        .replace(")", "")
                        .split(", ")[0]
                        .strip(),
                        suffix_text="S",
                        text_align="center",
                        color=ft.colors.with_opacity(0.8, "white"),
                        text_style=ft.TextStyle(
                            font_family="Consolas",
                        ),
                    ),
                ]
            ),
        )
        self.MLcontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 1),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            # size=12,
            expand=4,
            margin=ft.margin.only(left=10),
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            padding=ft.padding.only(left=8, top=2, bottom=2, right=1),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Memory limit:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="ограничения по памяти(мегабайт)",
                        border_color="transparent",
                        value=self.description.split("|")[5]
                        .replace(")", "")
                        .replace(")", "")
                        .split(", ")[1]
                        .strip(),
                        # width=150,
                        expand=True,
                        suffix_text="Mb",
                        text_align="center",
                        color=ft.colors.with_opacity(0.8, "white"),
                        text_style=ft.TextStyle(
                            font_family="Consolas",
                        ),
                    ),
                ]
            ),
        )

        if (
            len(
                self.description.split("|")[5]
                .replace(")", "")
                .replace(")", "")
                .split(", ")[2]
                .split("-")
            )
            > 1
        ):
            startvalue = (
                self.description.split("|")[5]
                .replace(")", "")
                .replace(")", "")
                .split(", ")[2]
                .split("-")[0]
                .strip()
            )
            endvalue = (
                self.description.split("|")[5]
                .replace(")", "")
                .replace(")", "")
                .split(", ")[2]
                .split("-")[1]
                .strip()
            )
        else:
            startvalue = endvalue = (
                self.description.split("|")[5]
                .replace(")", "")
                .replace(")", "")
                .split(", ")[2]
                .split("-")[0]
                .strip()
            )

        self.HRslider = ft.Container(
            margin=ft.margin.only(left=10),
            padding=ft.padding.only(left=8, top=7, bottom=7, right=1),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            on_hover=lambda e: self.animate_desc(e, 2),
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Text(
                        "Hard:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.RangeSlider(
                        expand=True,
                        min=0,
                        max=100,
                        start_value=startvalue,
                        divisions=20,
                        end_value=endvalue,
                        # round=1,
                        inactive_color=ft.colors.with_opacity(0.25, "white"),
                        active_color=ft.colors.RED_400,
                        overlay_color=ft.colors.with_opacity(0.4, "white"),
                        label="{value}%",
                        # label_animation=ft.animation.Animation(200, "decelerate"),
                    ),
                ],
            ),
            expand=7,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
        )

        self.Conditioncontainer = ft.Container(
            animate_scale=ft.animation.Animation(200, "decelerate"),
            on_hover=lambda e: self.animate_desc(e, 4),
            alignment=ft.alignment.center,
            expand=1,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            content=ft.Stack(
                controls=[
                    ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Условие:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=12,
                                min_lines=12,
                                border_color="transparent",
                                value=self.description.split("|")[2],
                            ),
                        ],
                    ),
                    # ft.IconButton(icon=ft.icons.FILE_OPEN, bottom=0.9, right=0.9)
                    # ft.IconButton(icon=ft.icons)
                ]
            ),
            margin=ft.margin.only(right=10),
            padding=ft.padding.only(left=10, right=10, top=10, bottom=24),
        )

        self.Namecontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 3),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Название:",
                        font_family="Consolas",
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="Название задачи",
                        expand=True,
                        value=self.description.split("|")[0],
                        border_color="transparent",
                        text_align="center",
                        # max_length=40,
                        label_style=ft.TextStyle(
                            font_family="Consolas",
                            size=16,
                        ),
                    ),
                ],
            ),
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.only(left=10, right=10),
            margin=ft.margin.only(left=10, right=10),
        )

        self.OutputDatacontainer = ft.Stack(
            controls=[
                ft.Container(
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    on_hover=lambda e: self.animate_desc(e, 6),
                    border=ft.border.all(
                        1.5,
                        ft.colors.with_opacity(0.045, "white"),
                    ),
                    border_radius=ft.border_radius.all(10),
                    padding=10,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Выходные данные:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=4,
                                min_lines=4,
                                border_color="transparent",
                                value=self.description.split("|")[4],
                            ),
                        ],
                    ),
                )
            ]
        )

        self.InputDatacontainer = ft.Stack(
            controls=[
                ft.Container(
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    on_hover=lambda e: self.animate_desc(e, 5),
                    border=ft.border.all(
                        1.5,
                        ft.colors.with_opacity(0.045, "white"),
                    ),
                    border_radius=ft.border_radius.all(10),
                    padding=10,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Входные данные:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=4,
                                min_lines=4,
                                border_color="transparent",
                                value=self.description.split("|")[3],
                            ),
                        ],
                    ),
                )
            ]
        )

        self.Addrowbutton = ft.IconButton(
            icon=ft.icons.ADD,
            on_click=self.add_row_to_test_table,
            tooltip="Добавить тест",
        )

        self.Deleterowbutton = ft.IconButton(
            icon=ft.icons.DELETE,
            on_click=self.delete_row_from_test_table,
            tooltip="Удалить тест",
            icon_color=ft.colors.RED_600,
        )

        self.TestsTable = ft.Container(
            content=ft.Column(
                controls=[
                    ft.DataTable(
                        # horizontal_lines=True,
                        data_row_min_height=60,
                        data_row_max_height=120,
                        width=600,
                        # expand=True,
                        bgcolor="#2a3139",
                        border_radius=10,
                        columns=[
                            ft.DataColumn(
                                ft.Text("Input", font_family="Consolas"),
                            ),
                            ft.DataColumn(
                                ft.Text("Output", font_family="Consolas"),
                            ),
                        ],
                        rows=[],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            self.Addrowbutton,
                            self.Deleterowbutton,
                        ],
                    ),
                ]
            )
        )

        for test in db_manager.session.query(Test).all():
            if test.task_id == self.id:
                self.TestsTable.content.controls[0].rows.append(
                    ft.DataRow(
                        # expand=True,
                        cells=[
                            ft.DataCell(
                                content=ft.Container(
                                    # height=100,
                                    expand=True,
                                    content=ft.TextField(
                                        min_lines=5,
                                        max_lines=8,
                                        border_color="transparent",
                                        multiline=True,
                                        value=test.input,
                                    ),
                                )
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    # height=100,
                                    expand=True,
                                    content=ft.TextField(
                                        min_lines=5,
                                        max_lines=8,
                                        border_color="transparent",
                                        multiline=True,
                                        value=test.output,
                                    ),
                                )
                            ),
                        ]
                    )
                )

        self.dlg_edit = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Редактировать задачу",
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.START,
                    height=600,
                    width=800,
                    scroll=ft.ScrollMode.HIDDEN,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Шапка задачи",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        self.Namecontainer,
                        ft.Container(
                            margin=ft.margin.only(left=10, right=10),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    self.TLcontainer,
                                    self.MLcontainer,
                                    self.HRslider,
                                ],
                            ),
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Описание задачи",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        ft.Container(
                            margin=ft.margin.only(left=10, right=10),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    self.Conditioncontainer,
                                    ft.Container(
                                        alignment=ft.alignment.center,
                                        expand=1,
                                        content=ft.Column(
                                            controls=[
                                                self.InputDatacontainer,
                                                self.OutputDatacontainer,
                                            ]
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Тесты",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        ft.Row(
                            alignment="center",
                            controls=[
                                ft.Text(
                                    font_family="Consolas",
                                    size=14,
                                    color=ft.colors.with_opacity(0.65, "white"),
                                    value="*в качестве примера будут использоватся первые min(2, n-1) из n тестов",
                                )
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[self.TestsTable],
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    text="Cохранить",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.ADD_TASK_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1, 1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0, 1),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        to_give_data = {
            self.InputDatacontainer.controls[0]: self.InputDatacontainer.controls[
                0
            ].content.controls[2],
            self.OutputDatacontainer.controls[0]: self.OutputDatacontainer.controls[
                0
            ].content.controls[2],
            self.Namecontainer: self.Namecontainer.content.controls[2],
            self.TLcontainer: self.TLcontainer.content.controls[2],
            self.MLcontainer: self.MLcontainer.content.controls[2],
            self.Conditioncontainer: self.Conditioncontainer.content.controls[
                0
            ].controls[2],
        }

        for cont, inp in to_give_data.items():
            inp.on_change = lambda e, cont=cont, inp=inp: self.higlite_inputs(
                cont, inp.value
            )

    def higlite_inputs(self, cont, value):

        if value:
            cont.border = ft.border.all(1.5, ft.colors.with_opacity(0.045, "white"))
            cont.update()
        else:
            cont.border = ft.border.all(1.5, ft.colors.RED_600)
            cont.update()

        self.page.update()

    def delete_row_from_test_table(self, e):
        if self.TestsTable.content.controls[0].rows:
            self.TestsTable.content.controls[0].rows.pop()
            self.TestsTable.update()
            self.page.update()

    def add_row_to_test_table(self, e):
        self.TestsTable.content.controls[0].rows.append(
            ft.DataRow(
                # expand=True,
                cells=[
                    ft.DataCell(
                        content=ft.Container(
                            # height=100,
                            expand=True,
                            content=ft.TextField(
                                min_lines=5,
                                max_lines=8,
                                border_color="transparent",
                                multiline=True,
                            ),
                        )
                    ),
                    ft.DataCell(
                        content=ft.Container(
                            # height=100,
                            expand=True,
                            content=ft.TextField(
                                min_lines=5,
                                max_lines=8,
                                border_color="transparent",
                                multiline=True,
                            ),
                        )
                    ),
                ]
            )
        )
        self.page.update()

    def animate_desc(self, e, n):
        to_animate = [
            self.TLcontainer,
            self.MLcontainer,
            self.HRslider,
            self.Namecontainer,
            self.Conditioncontainer,
            self.InputDatacontainer.controls[0],
            self.OutputDatacontainer.controls[0],
            # self.
        ]

        if e.data == "true":
            to_animate[n].scale = 1.01

        else:
            to_animate[n].scale = 1

        self.page.update()

    def edit(self):
        self.dlg_edit.open = True
        self.page.dialog = self.dlg_edit
        self.page.update()

    def delete(self):
        if self.dlg_delete.open == True:
            return
        self.dlg_delete.open = True
        self.page.dialog = self.dlg_delete
        self.on_delete_selected = not self.on_delete_selected

        while self.on_delete_selected and self.dlg_delete.open == True:
            self.card.rotate.angle += 0.005
            self.card.update()
            self.page.update()

            time.sleep(0.1)
            if self.on_delete_selected and self.dlg_delete.open == True:
                self.card.rotate.angle -= 0.010
                self.card.update()
                self.page.update()

            time.sleep(0.1)
            if self.on_delete_selected and self.dlg_delete.open == True:
                self.card.rotate.angle = 0
                self.card.update()
                self.page.update()

        # self.card.rotate.angle = 0
        # self.card.update()
        # self.page.update()

    def close_dlg(self, type, par):
        if par == 0:
            self.on_delete_selected = False
            self.dlg_delete.open = False
            self.page.update()

            if type == 1:
                db_manager.remove_task(task_id=self.id)
                show_message(self.page, "Задача успешно удаленна")
                self.func()
                # self.page.update()

        if par == 1:

            if type == 1:
                to_give_data = {
                    self.Namecontainer: self.Namecontainer.content.controls[2],
                    self.Conditioncontainer: self.Conditioncontainer.content.controls[
                        0
                    ].controls[2],
                    self.InputDatacontainer.controls[
                        0
                    ]: self.InputDatacontainer.controls[0].content.controls[2],
                    self.OutputDatacontainer.controls[
                        0
                    ]: self.OutputDatacontainer.controls[0].content.controls[2],
                    self.TLcontainer: self.TLcontainer.content.controls[2],
                    self.MLcontainer: self.MLcontainer.content.controls[2],
                    self.HRslider: self.HRslider.content.controls[2],
                }

                all_ok = True

                for cont, inp in to_give_data.items():
                    if isinstance(inp, ft.RangeSlider):
                        continue
                    if not inp.value:
                        all_ok = False
                        cont.border = ft.border.all(1.5, ft.colors.RED_600)
                        cont.update()
                    else:
                        cont.border = ft.border.all(
                            1.5, ft.colors.with_opacity(0.045, "white")
                        )
                        cont.update()

                tt = False
                for i in range(len(self.TestsTable.content.controls[0].rows)):
                    if (
                        not self.TestsTable.content.controls[0]
                        .rows[i]
                        .cells[0]
                        .content.content.value
                        or not self.TestsTable.content.controls[0]
                        .rows[i]
                        .cells[1]
                        .content.content.value
                    ):

                        all_ok = False
                        tt = True
                        self.TestsTable.border = ft.border.all(1.5, ft.colors.RED_600)
                        self.TestsTable.border_radius = 10
                        self.TestsTable.update()
                        self.page.update()

                if not tt:
                    self.TestsTable.border = None
                    self.TestsTable.update()
                    self.page.update()

                if all_ok:
                    self.dlg_edit.open = False
                    self.page.update()

                    description = (
                        self.Namecontainer.content.controls[2].value
                        + "|"
                        + "-|"
                        + self.Conditioncontainer.content.controls[0].controls[2].value
                        + "|"
                        + self.InputDatacontainer.controls[0].content.controls[2].value
                        + "|"
                        + self.OutputDatacontainer.controls[0].content.controls[2].value
                        + "|"
                        + f"({self.TLcontainer.content.controls[2].value}, {self.MLcontainer.content.controls[2].value}, {int(self.HRslider.content.controls[2].start_value)} - {int(self.HRslider.content.controls[2].end_value)})"
                        + "|"
                        + f"({', '.join(self.TestsTable.content.controls[0].rows[i].cells[0].content.content.value for i in range(len(self.TestsTable.content.controls[0].rows)))})"
                        + "|"
                        + f"({', '.join(self.TestsTable.content.controls[0].rows[i].cells[1].content.content.value for i in range(len(self.TestsTable.content.controls[0].rows)))})"
                    )

                    db_manager.update_task_description(
                        task_id=self.id,
                        new_description=description,
                    )

                    show_message(self.page, "Описание обновленно", "success")

                    for i in range(len(self.TestsTable.content.controls[0].rows)):
                        test_input = (
                            self.TestsTable.content.controls[0]
                            .rows[i]
                            .cells[0]
                            .content.content.value
                        )
                        test_output = (
                            self.TestsTable.content.controls[0]
                            .rows[i]
                            .cells[1]
                            .content.content.value
                        )
                        task_id = self.id
                        test_num = i

                        test_exists = (
                            db_manager.session.query(Test)
                            .filter(Test.task_id == task_id)
                            .filter(Test.num == test_num)
                            .first()
                        )
                        if test_exists:
                            db_manager.update_test_input_output(
                                test_exists.ID, test_input, test_output
                            )
                        else:
                            db_manager.add_test_to_task(
                                task_id, test_num, test_input, test_output
                            )

                    func()

            else:
                self.dlg_edit.open = False
                self.page.update()

    def go_to_task(self, e):
        self.page.update()

    def anim(self, e):
        if e.data == "true":
            self.card.elevation = 8
            self.card.scale = 1.009
            self.icon.scale = 1.2

            self.card.update()
            self.page.update()
        else:

            self.card.elevation = 0.9
            self.card.scale = 1
            self.icon.scale = 1

            self.card.update()
            self.page.update()

    def build(self) -> ft.Container:
        return self.card


class TasksTeacherPage(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        self.TLcontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 0),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            # size=12,
            expand=3,
            margin=0,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            padding=ft.padding.only(left=8, top=2, bottom=2, right=1),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Time limit:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="ограничения по времени(секунд)",
                        border_color="transparent",
                        # width=150,
                        expand=True,
                        suffix_text="S",
                        text_align="center",
                        color=ft.colors.with_opacity(0.8, "white"),
                        text_style=ft.TextStyle(
                            font_family="Consolas",
                        ),
                    ),
                ]
            ),
        )
        self.MLcontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 1),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            # size=12,
            expand=4,
            margin=ft.margin.only(left=10),
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            padding=ft.padding.only(left=8, top=2, bottom=2, right=1),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Memory limit:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="ограничения по памяти(мегабайт)",
                        border_color="transparent",
                        # width=150,
                        expand=True,
                        suffix_text="Mb",
                        text_align="center",
                        color=ft.colors.with_opacity(0.8, "white"),
                        text_style=ft.TextStyle(
                            font_family="Consolas",
                        ),
                    ),
                ]
            ),
        )

        self.HRslider = ft.Container(
            margin=ft.margin.only(left=10),
            padding=ft.padding.only(left=8, top=7, bottom=7, right=1),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            on_hover=lambda e: self.animate_desc(e, 2),
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Text(
                        "Hard:",
                        font_family="Consolas",
                        # size=1.
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.RangeSlider(
                        expand=True,
                        min=0,
                        max=100,
                        start_value=10,
                        divisions=20,
                        end_value=20,
                        # round=1,
                        inactive_color=ft.colors.with_opacity(0.25, "white"),
                        active_color=ft.colors.RED_400,
                        overlay_color=ft.colors.with_opacity(0.4, "white"),
                        label="{value}%",
                        # label_animation=ft.animation.Animation(200, "decelerate"),
                    ),
                ],
            ),
            expand=7,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
        )

        self.Conditioncontainer = ft.Container(
            animate_scale=ft.animation.Animation(200, "decelerate"),
            on_hover=lambda e: self.animate_desc(e, 4),
            alignment=ft.alignment.center,
            expand=1,
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=10,
            content=ft.Stack(
                controls=[
                    ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Условие:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=12,
                                min_lines=12,
                                border_color="transparent",
                            ),
                        ],
                    ),
                    # ft.IconButton(icon=ft.icons.FILE_OPEN, bottom=0.9, right=0.9)
                    # ft.IconButton(icon=ft.icons)
                ]
            ),
            margin=ft.margin.only(right=10),
            padding=ft.padding.only(left=10, right=10, top=10, bottom=24),
        )

        self.Namecontainer = ft.Container(
            on_hover=lambda e: self.animate_desc(e, 3),
            animate_scale=ft.animation.Animation(200, "decelerate"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Название:",
                        font_family="Consolas",
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.045, "white"),
                        width=2,
                        height=40,
                    ),
                    ft.TextField(
                        tooltip="Название задачи",
                        expand=True,
                        border_color="transparent",
                        text_align="center",
                        # max_length=40,
                        label_style=ft.TextStyle(
                            font_family="Consolas",
                            size=16,
                        ),
                    ),
                ],
            ),
            border=ft.border.all(1.5, ft.colors.with_opacity(0.045, "white")),
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.only(left=10, right=10),
            margin=ft.margin.only(left=10, right=10),
        )

        self.OutputDatacontainer = ft.Stack(
            controls=[
                ft.Container(
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    on_hover=lambda e: self.animate_desc(e, 6),
                    border=ft.border.all(
                        1.5,
                        ft.colors.with_opacity(0.045, "white"),
                    ),
                    border_radius=ft.border_radius.all(10),
                    padding=10,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Выходные данные:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=4,
                                min_lines=4,
                                border_color="transparent",
                            ),
                        ],
                    ),
                )
            ]
        )

        self.InputDatacontainer = ft.Stack(
            controls=[
                ft.Container(
                    animate_scale=ft.animation.Animation(200, "decelerate"),
                    on_hover=lambda e: self.animate_desc(e, 5),
                    border=ft.border.all(
                        1.5,
                        ft.colors.with_opacity(0.045, "white"),
                    ),
                    border_radius=ft.border_radius.all(10),
                    padding=10,
                    content=ft.Column(
                        horizontal_alignment="center",
                        controls=[
                            ft.Text(
                                "Входные данные:",
                                font_family="Consolas",
                                size=16,
                                text_align="center",
                            ),
                            ft.Divider(
                                height=2,
                                color=ft.colors.with_opacity(0.45, "white40"),
                            ),
                            ft.TextField(
                                multiline=True,
                                max_lines=4,
                                min_lines=4,
                                border_color="transparent",
                            ),
                        ],
                    ),
                )
            ]
        )

        self.Addrowbutton = ft.IconButton(
            icon=ft.icons.ADD,
            on_click=self.add_row_to_test_table,
            tooltip="Добавить тест",
        )

        self.Deleterowbutton = ft.IconButton(
            icon=ft.icons.DELETE,
            on_click=self.delete_row_from_test_table,
            tooltip="Удалить тест",
            icon_color=ft.colors.RED_600,
        )

        self.TestsTable = ft.Container(
            content=ft.Column(
                controls=[
                    ft.DataTable(
                        # horizontal_lines=True,
                        data_row_min_height=60,
                        data_row_max_height=120,
                        width=600,
                        # expand=True,
                        bgcolor="#2a3139",
                        border_radius=10,
                        columns=[
                            ft.DataColumn(
                                ft.Text("Input", font_family="Consolas"),
                            ),
                            ft.DataColumn(
                                ft.Text("Output", font_family="Consolas"),
                            ),
                        ],
                        rows=[
                            ft.DataRow(
                                # expand=True,
                                cells=[
                                    ft.DataCell(
                                        content=ft.Container(
                                            # height=100,
                                            expand=True,
                                            content=ft.TextField(
                                                min_lines=5,
                                                max_lines=8,
                                                border_color="transparent",
                                                multiline=True,
                                            ),
                                        )
                                    ),
                                    ft.DataCell(
                                        content=ft.Container(
                                            # height=100,
                                            expand=True,
                                            content=ft.TextField(
                                                min_lines=5,
                                                max_lines=8,
                                                border_color="transparent",
                                                multiline=True,
                                            ),
                                        )
                                    ),
                                ]
                            )
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            self.Addrowbutton,
                            self.Deleterowbutton,
                        ],
                    ),
                ]
            )
        )

        self.add_task_dlg = ft.AlertDialog(
            adaptive=True,
            modal=True,
            title=ft.Column(
                horizontal_alignment="center",
                controls=[
                    ft.Text(
                        "Создать задачу",
                        text_align="center",
                        color=ft.colors.with_opacity(0.45, "white"),
                    ),
                    ft.Divider(height=1, color="white40"),
                ],
            ),
            actions=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.START,
                    height=600,
                    width=800,
                    scroll=ft.ScrollMode.HIDDEN,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Шапка задачи",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        self.Namecontainer,
                        ft.Container(
                            margin=ft.margin.only(left=10, right=10),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    self.TLcontainer,
                                    self.MLcontainer,
                                    self.HRslider,
                                ],
                            ),
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Описание задачи",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        ft.Container(
                            margin=ft.margin.only(left=10, right=10),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    self.Conditioncontainer,
                                    ft.Container(
                                        alignment=ft.alignment.center,
                                        expand=1,
                                        content=ft.Column(
                                            controls=[
                                                self.InputDatacontainer,
                                                self.OutputDatacontainer,
                                            ]
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(
                                        1.5,
                                        ft.colors.with_opacity(
                                            0.25, ft.colors.AMBER_100
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.only(left=10, right=10),
                                    content=ft.Text(
                                        "Тесты",
                                        font_family="Consolas",
                                        size=17,
                                        color=ft.colors.with_opacity(0.65, "white"),
                                    ),
                                )
                            ],
                        ),
                        ft.Row(
                            alignment="center",
                            controls=[
                                ft.Text(
                                    font_family="Consolas",
                                    size=14,
                                    color=ft.colors.with_opacity(0.65, "white"),
                                    value="*в качестве примера будут использоватся первые min(2, n-1) из n тестов",
                                )
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[self.TestsTable],
                        ),
                        ft.Row(
                            # expand=True,
                            controls=[
                                ft.ElevatedButton(
                                    text="Cоздать",
                                    color=ft.colors.GREEN_600,
                                    icon=ft.icons.ADD_TASK_ROUNDED,
                                    on_click=lambda _: self.close_dlg(1),
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    text="Отмена",
                                    color=ft.colors.WHITE30,
                                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                    on_click=lambda _: self.close_dlg(0),
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.add_new_task_btn = ft.ElevatedButton(
            on_click=lambda _: self.add_new_task(),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(150, ft.AnimationCurve.BOUNCE_OUT),
            height=45,
            width=185,
            content=ft.Row(
                alignment="center",
                controls=(
                    ft.Icon(
                        ft.icons.ADD_ROUNDED, color="green", size=26, offset=(-0.6, 0)
                    ),
                    ft.Text(
                        "Добавить задачу",
                        font_family="Consolas",
                        size=15,
                        color="green",
                        text_align="center",
                        offset=(-0.15, 0),
                    ),
                ),
            ),
        )

        to_give_data = {
            self.InputDatacontainer.controls[0]: self.InputDatacontainer.controls[
                0
            ].content.controls[2],
            self.OutputDatacontainer.controls[0]: self.OutputDatacontainer.controls[
                0
            ].content.controls[2],
            self.Namecontainer: self.Namecontainer.content.controls[2],
            self.TLcontainer: self.TLcontainer.content.controls[2],
            self.MLcontainer: self.MLcontainer.content.controls[2],
            self.Conditioncontainer: self.Conditioncontainer.content.controls[
                0
            ].controls[2],
        }

        for cont, inp in to_give_data.items():
            inp.on_change = lambda e, cont=cont, inp=inp: self.higlite_inputs(
                cont, inp.value
            )

        # for i in range(len(self.TestsTable.content.controls[0].rows)):
        #     self.TestsTable.content.controls[0].rows[i].cells[0].content.content.on_change = lambda e, cont=self.TestsTable, inp=self.TestsTable.content.controls[0].rows[i].cells[0].content.content: self.higlite_inputs(cont, inp.value)

    def higlite_inputs(self, cont, value):

        if value:
            cont.border = ft.border.all(1.5, ft.colors.with_opacity(0.045, "white"))
            cont.update()
        else:
            cont.border = ft.border.all(1.5, ft.colors.RED_600)
            cont.update()

        self.page.update()

    def delete_row_from_test_table(self, e):
        if self.TestsTable.content.controls[0].rows:
            self.TestsTable.content.controls[0].rows.pop()
            self.TestsTable.update()
            self.page.update()

    def add_row_to_test_table(self, e):
        self.TestsTable.content.controls[0].rows.append(
            ft.DataRow(
                # expand=True,
                cells=[
                    ft.DataCell(
                        content=ft.Container(
                            # height=100,
                            expand=True,
                            content=ft.TextField(
                                min_lines=5,
                                max_lines=8,
                                border_color="transparent",
                                multiline=True,
                            ),
                        )
                    ),
                    ft.DataCell(
                        content=ft.Container(
                            # height=100,
                            expand=True,
                            content=ft.TextField(
                                min_lines=5,
                                max_lines=8,
                                border_color="transparent",
                                multiline=True,
                            ),
                        )
                    ),
                ]
            )
        )
        self.page.update()

    def animate_desc(self, e, n):
        to_animate = [
            self.TLcontainer,
            self.MLcontainer,
            self.HRslider,
            self.Namecontainer,
            self.Conditioncontainer,
            self.InputDatacontainer.controls[0],
            self.OutputDatacontainer.controls[0],
            # self.
        ]

        if e.data == "true":
            to_animate[n].scale = 1.01

        else:
            to_animate[n].scale = 1

        self.page.update()
        # self.page.update()

    def close_dlg(self, type):
        if type == 1:
            to_give_data = {
                self.Namecontainer: self.Namecontainer.content.controls[2],
                self.Conditioncontainer: self.Conditioncontainer.content.controls[
                    0
                ].controls[2],
                self.InputDatacontainer.controls[0]: self.InputDatacontainer.controls[
                    0
                ].content.controls[2],
                self.OutputDatacontainer.controls[0]: self.OutputDatacontainer.controls[
                    0
                ].content.controls[2],
                self.TLcontainer: self.TLcontainer.content.controls[2],
                self.MLcontainer: self.MLcontainer.content.controls[2],
                self.HRslider: self.HRslider.content.controls[2],
            }

            all_ok = True

            for cont, inp in to_give_data.items():
                if isinstance(inp, ft.RangeSlider):
                    continue
                if not inp.value:
                    all_ok = False
                    cont.border = ft.border.all(1.5, ft.colors.RED_600)
                    cont.update()
                else:
                    cont.border = ft.border.all(
                        1.5, ft.colors.with_opacity(0.045, "white")
                    )
                    cont.update()

            tt = False
            for i in range(len(self.TestsTable.content.controls[0].rows)):
                if (
                    not self.TestsTable.content.controls[0]
                    .rows[i]
                    .cells[0]
                    .content.content.value
                    or not self.TestsTable.content.controls[0]
                    .rows[i]
                    .cells[1]
                    .content.content.value
                ):

                    all_ok = False
                    tt = True
                    self.TestsTable.border = ft.border.all(1.5, ft.colors.RED_600)
                    self.TestsTable.border_radius = 10
                    self.TestsTable.update()
                    self.page.update()

            if not tt:
                self.TestsTable.border = None
                self.TestsTable.update()
                self.page.update()

            if all_ok:
                self.close_dlg(0)
                description = (
                    self.Namecontainer.content.controls[2].value
                    + "|"
                    + "-|"
                    + self.Conditioncontainer.content.controls[0].controls[2].value
                    + "|"
                    + self.InputDatacontainer.controls[0].content.controls[2].value
                    + "|"
                    + self.OutputDatacontainer.controls[0].content.controls[2].value
                    + "|"
                    + f"({self.TLcontainer.content.controls[2].value}, {self.MLcontainer.content.controls[2].value}, {int(float(self.HRslider.content.controls[2].start_value))} - {int(float(self.HRslider.content.controls[2].end_value))})"
                    + "|"
                    + f"({', '.join(self.TestsTable.content.controls[0].rows[i].cells[0].content.content.value for i in range(len(self.TestsTable.content.controls[0].rows)))})"
                    + "|"
                    + f"({', '.join(self.TestsTable.content.controls[0].rows[i].cells[1].content.content.value for i in range(len(self.TestsTable.content.controls[0].rows)))})"
                )

                db_manager.add_task_to_theme(
                    theme_id=CURRENT_THEME_ID,
                    description=description,
                )

                for i in range(len(self.TestsTable.content.controls[0].rows)):
                    # db_manager.add_test_to_task(task_id=db_manager.session.query(Task).all()[-1].ID, num=db_manager.session.query(Test).filter(Test.ID == db_manager.session.query(Task).all()[-1].ID).all()[-1].num + 1, input_data=self.TestsTable.content.controls[0].rows[i].cells[0].content.content.value, output_data=self.TestsTable.content.controls[0].rows[i].cells[1].content.content.value)
                    test_input = (
                        self.TestsTable.content.controls[0]
                        .rows[i]
                        .cells[0]
                        .content.content.value
                    )
                    test_output = (
                        self.TestsTable.content.controls[0]
                        .rows[i]
                        .cells[1]
                        .content.content.value
                    )
                    task_id = db_manager.session.query(Task).all()[-1].ID
                    test_num = i + 1
                    db_manager.add_test_to_task(
                        task_id, test_num, test_input, test_output
                    )

                func()

        if type == 0:
            self.add_task_dlg.open = False
            self.page.update()

    def build(self):
        get_data()

        self.view_tasks = ft.Column(
            expand=1,
            scroll=ft.ScrollMode.HIDDEN,
            horizontal_alignment="center",
        )

        def delete_func():
            self.view_tasks.controls.clear()

            # db_manager = DatabaseManager(uri)
            get_data()
            for task_id, task in TASKS_DATA.items():
                if task["theme_id"] == CURRENT_THEME_ID:
                    crd = TaskTeacherCard(
                        name=task["description"].split("|")[0],
                        id=task_id,
                        par=self,
                        description=task["description"],
                    )
                    crd.func = delete_func
                    self.view_tasks.controls.append(crd)

            self.view_tasks.controls.append(self.add_new_task_btn)
            self.view_tasks.update()
            self.page.update()

        global func
        func = delete_func

        for task_id, task in TASKS_DATA.items():
            if task["theme_id"] == CURRENT_THEME_ID:
                crd = TaskTeacherCard(
                    name=task["description"].split("|")[0],
                    id=task_id,
                    par=self,
                    description=task["description"],
                )
                crd.func = delete_func
                self.view_tasks.controls.append(crd)

        self.view_tasks.controls.append(self.add_new_task_btn)
        return self.view_tasks

    def add_new_task(self):
        self.add_task_dlg.open = True
        self.page.dialog = self.add_task_dlg
        self.page.update()


def main(page: ft.Page) -> None:
    page.title = "pytosh"

    # page.scroll = ft.ScrollMode.HIDDEN
    page.vertical_alignment = "center"
    page.padding = 0
    page.route = "/"

    def change_content(route):
        if page.route == "/app~teacher/tasks":
            back = BackButton(size=13)
            back.top = None

            def go_back(e):
                page.controls[0].controls[1].content.offset = ft.transform.Offset(1, 0)
                page.controls[0].controls[1].content.update()
                page.update()

            back.on_click = go_back

            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                alignment=ft.alignment.top_center,
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                on_animation_end=lambda _: page.go("/app~teacher/themes"),
                controls=[
                    ft.Row(
                        vertical_alignment="top",
                        controls=[
                            back,
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"'{db_manager.session.query(Group).filter(Group.ID == CURRENT_GROUP_ID).all()[0].description.split('|')[0]}' ⟶ '{db_manager.session.query(Theme).filter(Theme.ID == CURRENT_THEME_ID).all()[0].description.split('|')[0]}' ⟶ Задачи",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            ),
                        ],
                    ),
                    ft.Divider(height=25, color="transparent"),
                    TasksTeacherPage(),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~teacher/themes":
            back = BackButton(size=13)
            back.top = None

            def go_back(e):
                page.controls[0].controls[1].content.offset = ft.transform.Offset(1, 0)
                page.controls[0].controls[1].content.update()
                page.update()

            back.on_click = go_back

            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                alignment=ft.alignment.top_center,
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                on_animation_end=lambda _: page.go("/app~teacher/groups-manager"),
                controls=[
                    ft.Row(
                        vertical_alignment="top",
                        controls=[
                            back,
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"'{db_manager.session.query(Group).filter(Group.ID == CURRENT_GROUP_ID).all()[0].description.split('|')[0]}' ⟶ Темы",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            ),
                        ],
                    ),
                    ft.Divider(height=25, color="transparent"),
                    ThemesTeacherPage(),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~teacher/groups-manager":
            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content.offset = (0, 0)
            # page.controls[0].controls[1].vertical_alignment = "top"
            page.controls[0].controls[1].content = GroupsEditTeacherPage()

            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student/groups-manager":
            page.controls[0].controls[1].content.clean()

            page.controls[0].controls[1].content = GroupsEditPage()

            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student/account":
            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                alignment=ft.alignment.top_center,
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                # on_animation_end=lambda _: page.go("/app~teacher/groups-manager"),
                controls=[
                    ft.Row(
                        vertical_alignment="top",
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"Аккаунт",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            ),
                        ],
                    ),
                    ft.Divider(height=25, color="transparent"),
                    ThemesTeacherPage(),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student/groups":
            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                animate_offset=ft.animation.Animation(350, "decelerate"),
                offset=ft.transform.Offset(0, 0),
                horizontal_alignment="center",
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    "Группы",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            )
                        ]
                    ),
                    ft.Divider(height=25, color="transparent"),
                    GroupsManager(),
                ],
            )

            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student/themes":
            back = BackButton(size=13)
            back.top = None

            def go_back(e):
                page.controls[0].controls[1].content.offset = ft.transform.Offset(1, 0)
                page.controls[0].controls[1].content.update()
                page.update()

            back.on_click = go_back

            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                alignment=ft.alignment.top_center,
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                on_animation_end=lambda _: page.go("/app~student/groups"),
                controls=[
                    ft.Row(
                        vertical_alignment="top",
                        controls=[
                            back,
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"'{db_manager.session.query(Group).filter(Group.ID == CURRENT_GROUP_ID).all()[0].description.split('|')[0]}' ⟶ Темы",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            ),
                        ],
                    ),
                    ft.Divider(height=25, color="transparent"),
                    ThemesPage(),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if (
            page.route.startswith("/app~student/tasks/")
            and page.route != "/app~student/tasks"
        ):
            task_id = int(page.route.split("/")[-1])

            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                horizontal_alignment="center",
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                on_animation_end=lambda _: page.go("/app~student/tasks"),
                controls=[
                    TaskPage(info=TASKS_DATA[task_id], id=task_id),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student/tasks":
            back = BackButton(size=13)
            back.top = None

            def go_back(e):
                page.controls[0].controls[1].content.offset = ft.transform.Offset(1, 0)
                page.controls[0].controls[1].content.update()
                page.update()

            back.on_click = go_back

            page.controls[0].controls[1].content.clean()
            page.controls[0].controls[1].content = ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                horizontal_alignment="center",
                offset=ft.transform.Offset(0, 0),
                animate_offset=ft.animation.Animation(250, "decelerate"),
                on_animation_end=lambda _: page.go("/app~student/themes"),
                controls=[
                    ft.Row(
                        controls=[
                            back,
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"'{db_manager.session.query(Group).filter(Group.ID == CURRENT_GROUP_ID).all()[0].description.split('|')[0]}' ⟶ '{db_manager.session.query(Theme).filter(Theme.ID == CURRENT_THEME_ID).all()[0].description.split('|')[0]}' ⟶ Задачи",
                                    font_family="Consolas",
                                    size=18,
                                    text_align="center",
                                    weight=110,
                                ),
                                border_radius=10,
                                padding=10,
                                bgcolor="#2a3139",
                            ),
                        ]
                    ),
                    ft.Divider(height=25, color="transparent"),
                    ThemeTasksPage(),
                ],
            )
            page.controls[0].controls[1].update()
            page.update()

        if page.route == "/app~student":
            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

            def AnimateSidebar(e):
                if page.controls[0].controls[0].width != 62:
                    for item in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[0]
                        .content.controls[1]
                        .controls[:]
                    ):
                        item.opacity = 0
                        item.update()

                    for items in icon_btns:
                        if isinstance(items, ft.Container):
                            items.content.controls[0].controls[0].opacity = 0
                            items.content.update()

                    time.sleep(0.2)
                    page.controls[0].controls[0].width = 62
                    page.controls[0].controls[0].update()

                    page.controls[0].controls[1].update()
                else:
                    page.controls[0].controls[0].width = 160
                    page.controls[0].controls[0].update()

                    page.controls[0].controls[1].update()

                    time.sleep(0.2)

                    for item in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[0]
                        .content.controls[1]
                        .controls[:]
                    ):
                        item.opacity = 1
                        item.update()

                    for items in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[3:]
                    ):
                        if isinstance(items, ft.Container):
                            items.content.controls[0].controls[0].opacity = 1
                            items.content.update()

                        # pass

            page.add(
                ft.Row(
                    vertical_alignment="top",
                    controls=[
                        ft.Container(
                            # expand=True,
                            width=160,
                            height=760,
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                            border_radius=10,
                            animate=ft.animation.Animation(500, "decelerate"),
                            alignment=ft.alignment.top_center,
                            margin=10,
                            padding=ft.padding.only(
                                top=-90, left=10, right=10, bottom=0
                            ),
                            content=NavBar(AnimateSidebar),
                        ),
                        ft.Container(
                            expand=True,
                            # width=1210,
                            alignment=ft.alignment.top_center,
                            margin=10,
                            height=760,
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                            animate=ft.animation.Animation(500, "decelerate"),
                            # alignment=ft.alignment.center,
                            padding=10,
                            border_radius=10,
                            content=GroupsManager(),
                        ),
                    ],
                )
            )

            page.go

            page.update()

        if page.route == "/app~teacher":
            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

            def AnimateSidebar(e):
                if page.controls[0].controls[0].width != 62:
                    for item in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[0]
                        .content.controls[1]
                        .controls[:]
                    ):
                        item.opacity = 0
                        item.update()

                    for items in icon_btns:
                        if isinstance(items, ft.Container):
                            items.content.controls[0].controls[0].opacity = 0
                            items.content.update()

                    time.sleep(0.2)
                    page.controls[0].controls[0].width = 62
                    page.controls[0].controls[0].update()

                    page.controls[0].controls[1].update()
                else:
                    page.controls[0].controls[0].width = 160
                    page.controls[0].controls[0].update()

                    page.controls[0].controls[1].update()

                    time.sleep(0.2)

                    for item in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[0]
                        .content.controls[1]
                        .controls[:]
                    ):
                        item.opacity = 1
                        item.update()

                    for items in (
                        page.controls[0]
                        .controls[0]
                        .content.controls[0]
                        .content.controls[3:]
                    ):
                        if isinstance(items, ft.Container):
                            items.content.controls[0].controls[0].opacity = 1
                            items.content.update()

                        # pass

            page.add(
                ft.Row(
                    vertical_alignment="top",
                    controls=[
                        ft.Container(
                            # padding=20,
                            # expand=3,
                            width=160,
                            height=760,
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                            border_radius=10,
                            animate=ft.animation.Animation(500, "decelerate"),
                            alignment=ft.alignment.top_center,
                            margin=10,
                            padding=ft.padding.only(
                                top=-90, left=10, right=10, bottom=0
                            ),
                            content=NavBar(AnimateSidebar),
                        ),
                        ft.Container(
                            expand=True,
                            # padding=20,
                            alignment=ft.alignment.top_center,
                            # width=1210,
                            margin=10,
                            height=760,
                            bgcolor=ft.colors.with_opacity(0.045, "white"),
                            animate=ft.animation.Animation(500, "decelerate"),
                            # alignment=ft.alignment.center,
                            padding=20,
                            border_radius=10,
                            content=ft.Container(
                                content=ft.Column(
                                    height=page.height - 40,
                                    controls=[ft.Text("admin ili kak tam tebya")],
                                ),
                            ),
                        ),
                    ],
                )
            )

            page.go("/app~student/groups-manager")
            page.update()

        if page.route == "/":
            page.controls.clear()

            backgound = ft.Stack(expand=True, controls=[Thing() for __ in range(150)])

            stack = ft.Stack(
                expand=True,
                controls=[
                    backgound,
                    ft.Column(
                        alignment="center",
                        horizontal_alignment="center",
                        controls=[
                            ft.Row(
                                alignment="center",
                                controls=[BodyHello()],
                            )
                        ],
                    ),
                ],
            )

            page.add(stack)

            async def run():
                await asyncio.gather(
                    *(item.animate_thing() for item in backgound.controls),
                )

            asyncio.run(run())

        if page.route == "/login":
            page.controls.clear()

            backgound = ft.Stack(expand=True, controls=[Thing() for __ in range(150)])

            stack = ft.Stack(
                expand=True,
                controls=[
                    backgound,
                    ft.Column(
                        alignment="center",
                        horizontal_alignment="center",
                        controls=[
                            ft.Row(
                                alignment="center",
                                controls=[BodyLogin()],
                            )
                        ],
                    ),
                ],
            )

            page.add(stack)

            async def run():
                await asyncio.gather(
                    *(item.animate_thing() for item in backgound.controls),
                )

            asyncio.run(run())

        if page.route == "/registration":
            page.controls.clear()

            backgound = ft.Stack(expand=True, controls=[Thing() for __ in range(150)])

            stack = ft.Stack(
                expand=True,
                controls=[
                    backgound,
                    ft.Column(
                        alignment="center",
                        horizontal_alignment="center",
                        controls=[
                            ft.Row(
                                alignment="center",
                                controls=[BodyRegistration()],
                            )
                        ],
                    ),
                ],
            )

            page.add(stack)

            async def run():
                await asyncio.gather(
                    *(item.animate_thing() for item in backgound.controls),
                )

            asyncio.run(run())

    page.on_route_change = change_content
    page.controls.clear()

    backgound = ft.Stack(expand=True, controls=[Thing() for __ in range(150)])

    stack = ft.Stack(
        expand=True,
        controls=[
            backgound,
            ft.Column(
                alignment="center",
                horizontal_alignment="center",
                controls=[
                    ft.Row(
                        alignment="center",
                        controls=[BodyHello()],
                    )
                ],
            ),
        ],
    )

    page.add(stack)

    try:

        async def run():
            await asyncio.gather(
                *(item.animate_thing() for item in backgound.controls),
            )

        asyncio.run(run())

    except:
        pass

    page.update()


if __name__ == "__main__":
    ft.app(
        target=main,
        # view=ft.WEB_BROWSER,
    )
