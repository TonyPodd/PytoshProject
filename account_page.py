from typing import List
import flet as ft
import flet_material as fm
from database.db import DatabaseManager, User, Group, Sending, Test, Task, Theme, UserGroup
from database.config import uri
# from execute_code import execute_code
import calendar


# from task import TaskPage
from datetime import datetime
import datetime
import random
import asyncio
from re import match
from functools import partial
import time
import pyperclip
# from req import send

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
CURRENT_USER_ID = 1
TESTS_DATA = {}
func = None
# def get_time():
#     now = datetime.now()
#     formatted_date = now.strftime("%H:%M %d.%m.%Y")
# return formatted_date


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


class State:
    toggle = True


s = State()


class StatBarChart(ft.UserControl):
    def __init__(self, left_axis_labels, bottom_axis_labels):
        super().__init__()

        self.colors = [
            ft.colors.BLUE,
            ft.colors.GREEN,
            ft.colors.YELLOW,
            ft.colors.RED,
            ft.colors.PINK,
            ft.colors.GREY,
            ft.colors.TEAL,
            ft.colors.AMBER,
            ft.colors.BROWN,
        ]
        self.cur_color = 0
        self.cur_x = 0
        self.chart = ft.BarChart(
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                width=1,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                width=1,
            ),
            interactive=True,
            left_axis=ft.ChartAxis(labels=[]),
            bottom_axis=ft.ChartAxis(labels=[]),
        )

        for value, text in left_axis_labels:
            self.chart.left_axis.labels.append(
                ft.ChartAxisLabel(
                    value=value,
                    label=ft.Text(text, size=14, weight=ft.FontWeight.BOLD),
                ),
            )
        for value, text in bottom_axis_labels:
            self.chart.bottom_axis.labels.append(
                ft.ChartAxisLabel(
                    value=value,
                    label=ft.Text(text, size=14, weight=ft.FontWeight.BOLD),
                ),
            )

    def add_bar(self, to, tooltip):
        self.chart.bar_groups.append(
            ft.BarChartGroup(
                x=self.cur_x,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=to,
                        width=40,
                        color=self.colors[self.cur_color],
                        tooltip=tooltip,
                        border_radius=0,
                    ),
                ],
            ),
        )
        self.cur_x += 1
        self.cur_color = (self.cur_color + 1) % len(self.colors)

    def build(self):
        return self.chart


class StatLineChart(ft.UserControl):
    def __init__(self, left_axis_labels = None, bottom_axis_labels = None):
        super().__init__()

        self.colors = [
            ft.colors.BLUE,
            ft.colors.GREEN,
            ft.colors.YELLOW,
            ft.colors.RED,
            ft.colors.PINK,
            ft.colors.GREY,
            ft.colors.TEAL,
            ft.colors.AMBER,
            ft.colors.BROWN,
        ]

        self.cur_color = 0
        self.chart = ft.LineChart(
            interactive=True,
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                width=1,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                width=1,
            ),
            left_axis=ft.ChartAxis(
                labels_size=30,
            ),
            bottom_axis=ft.ChartAxis(
                show_labels=True,
                labels_size=30,
                labels_interval=1,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            expand=True,
        )
        if left_axis_labels:
            for value, text in left_axis_labels:
                self.chart.left_axis.labels.append(
                    ft.ChartAxisLabel(
                        value=value,
                        label=ft.Text(text, size=14, weight=ft.FontWeight.BOLD),
                    ),
                )
                
        if bottom_axis_labels:
            for value, text in bottom_axis_labels:
                self.chart.bottom_axis.labels.append(
                    ft.ChartAxisLabel(
                        value=value,
                        label=ft.Text(text, size=14, weight=ft.FontWeight.BOLD),
                    ),
                )

    def add_line(self, data_points):
        datpoin = [ft.LineChartDataPoint(x, int(y)) for x, y in data_points]
        self.chart.data_series.append(
            ft.LineChartData(
                data_points=datpoin,
                stroke_width=4,
                color=self.colors[self.cur_color],
                # curved=True,
                stroke_cap_round=True,
            )
        )
        self.cur_color = (self.cur_color + 1) % len(self.colors)

    def build(self):
        return self.chart


class StatisticPage(ft.UserControl):
    def __init__(self):
        super().__init__()
        today = datetime.datetime.combine(
            datetime.date.today(), datetime.datetime.max.time()
        )

        # Querying all data, not just for the last week
        query = (
            db_manager.session.query(Sending)
            .filter(Sending.verdict == "accepted")
            .filter(Sending.author == CURRENT_USER_ID)
            .all()
        )

        solved_tasks_week = {}
        solved_tasks_all = {}
        abs_tasks = {}

        current_day = today - datetime.timedelta(days=7)
        while current_day <= today:
            solved_tasks_week[current_day.strftime("%H:%M %d.%m.%Y").split()[1]] = 0
            current_day += datetime.timedelta(days=1)

        for send in query:
            time_formatted = datetime.datetime.strptime(send.time, "%H:%M %d.%m.%Y")
            day_key = time_formatted.strftime("%H:%M %d.%m.%Y").split()[1]
            solved_tasks_all.setdefault(day_key, 0)
            solved_tasks_all[day_key] += 1

            if today - datetime.timedelta(days=7) <= time_formatted <= today:
                solved_tasks_week.setdefault(day_key, 0)
                solved_tasks_week[day_key] += 1

            if send.task_id in abs_tasks:
                abs_tasks[send.task_id] += 1
            else:
                abs_tasks[send.task_id] = 1

        self.groups_dropdown = ft.Dropdown(
            label="Группа",
            hint_text="Выберете группу для отображения статистики",
            options=[],
            on_change=lambda e: self.change_group_chart(),
        )
        self.groups_id = {}

        user_group_list = (
            db_manager.session.query(UserGroup)
            .filter(UserGroup.user_id == CURRENT_USER_ID)
            .all()
        )

        for grp in user_group_list:
            group = (
                db_manager.session.query(Group).filter(Group.ID == grp.group_id).first()
            )
            if group:
                self.groups_dropdown.options.append(
                    ft.dropdown.Option(group.description.split("|")[0])
                )
                self.groups_id[group.ID] = {"description": group.description}

        for id in self.groups_id:
            participants_id = []
            for grp in db_manager.session.query(UserGroup).all():
                if grp.group_id == id:
                    participants_id.append(grp.user_id)
            self.groups_id[id]["party"] = participants_id

        # Building chart for last 7 days
        self.line_chart_week = self.build_chart(solved_tasks_week)

        # Building chart for all days
        self.line_chart_all = self.build_chart(solved_tasks_all)
        self.group_line_chart = StatLineChart(left_axis_labels=[(i, str(i)) for i in range(10)], bottom_axis_labels=[(i, str(i)) for i in range(50, 150)])
        self.group_line_chart.add_line([(120, 1), (130, 1), (140, 1)])
        # self.group_line_chart.update()
        

    def change_group_chart(self):
        grp_id = None
        for id in self.groups_id:
            if (
                self.groups_id[id]["description"].split("|")[0]
                == self.groups_dropdown.value
            ):
                grp_id = id
                break

        query = (
            db_manager.session.query(Sending)
            .filter(Sending.verdict == "accepted")
            .all()
        )
        
        data_to_build = {}
        line_chart = StatLineChart()

        for user_id in self.groups_id[grp_id]["party"]:
            solved_tasks_all = {}
            abs_tasks = {}
        
            for send in query:
                if send.author != user_id:
                    continue
                
                task = (
                    db_manager.session.query(Task)
                    .filter(Task.ID == send.task_id)
                    .first()
                )

                # print(task)
                theme = (
                    db_manager.session.query(Theme)
                    .filter(Theme.ID == task.theme_id)
                    .first()
                )

                if theme.group_id == grp_id:
                    # print(theme.description)

                    time_formatted = datetime.datetime.strptime(send.time, "%H:%M %d.%m.%Y")
                    day_key = time_formatted.strftime("%H:%M %d.%m.%Y").split()[1]
                    solved_tasks_all.setdefault(day_key, 0)
                    solved_tasks_all[day_key] += 1

                    if send.task_id in abs_tasks:
                        abs_tasks[send.task_id] += 1
                    else:
                        abs_tasks[send.task_id] = 1
                        
            data_to_build[user_id] = solved_tasks_all
            
        start_date = datetime.datetime(2024, 1, 1)

        for i in data_to_build:
            data_points = []
            for time_str, count in data_to_build[i].items():
                time = datetime.datetime.strptime(time_str, '%d.%m.%Y')
                days_since_start = (time - start_date).days
                data_points.append((days_since_start, count))
                
            print(data_points)
            line_chart.add_line(data_points=data_points)
            line_chart.update()
            
        self.group_line_chart.update()
        self.update()
        print(data_to_build)
            
        self.page.update()
            
        
    

    def build_chart(self, solved_tasks):
        line_chart = StatLineChart(
            left_axis_labels=[
                (i, str(i)) for i in range(max(solved_tasks.values()) + 1)
            ],
            bottom_axis_labels=[
                (i, ".".join(list(solved_tasks.keys())[i].split(".")[:2]))
                for i in range(len(solved_tasks))
            ],
        )

        data_points = []
        x = 0
        for time, count in solved_tasks.items():
            data_points.append((x, count))
            x += 1
        line_chart.add_line(data_points=data_points)

        return line_chart

    def build(self):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            height=800,
            alignment=ft.alignment.top_center,
            offset=ft.transform.Offset(0, 0),
            animate_offset=ft.animation.Animation(250, "decelerate"),
            controls=[
                ft.Row(
                    vertical_alignment="top",
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Text(
                                f"'{db_manager.session.query(User).filter(User.ID == CURRENT_USER_ID).all()[0].username}' ⟶ Статистика",
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
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=2,
                            border=ft.border.all(
                                3, ft.colors.with_opacity(0.045, "white")
                            ),
                            border_radius=10,
                            padding=15,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                border=ft.border.all(
                                                    1.5,
                                                    ft.colors.with_opacity(
                                                        0.045, "white"
                                                    ),
                                                ),
                                                content=ft.Text(
                                                    "Последние 7 дней",
                                                    font_family="Consolas",
                                                    size=18,
                                                ),
                                                border_radius=10,
                                                padding=10,
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(
                                                    "*количество решенных задач в каждый из последних 7 дней",
                                                    font_family="Consolas",
                                                    size=13,
                                                    color=ft.colors.with_opacity(
                                                        0.45, "white"
                                                    ),
                                                ),
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    self.line_chart_week,
                                ]
                            ),
                        ),
                        ft.Container(
                            expand=3,
                            border=ft.border.all(
                                3, ft.colors.with_opacity(0.045, "white")
                            ),
                            border_radius=10,
                            padding=15,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                border=ft.border.all(
                                                    1.5,
                                                    ft.colors.with_opacity(
                                                        0.045, "white"
                                                    ),
                                                ),
                                                content=ft.Text(
                                                    "Все дни",
                                                    font_family="Consolas",
                                                    size=18,
                                                ),
                                                border_radius=10,
                                                padding=10,
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(
                                                    "*количество решенных задач, за каждый день когда они решались",
                                                    font_family="Consolas",
                                                    size=13,
                                                    color=ft.colors.with_opacity(
                                                        0.45, "white"
                                                    ),
                                                ),
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    self.line_chart_all,
                                ]
                            ),
                        ),
                    ]
                ),
                self.groups_dropdown,
                ft.Row(
                    controls=[
                        ft.Container(
                            # expand=3,
                            border=ft.border.all(
                                3, ft.colors.with_opacity(0.045, "white")
                            ),
                            border_radius=10,
                            padding=15,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                border=ft.border.all(
                                                    1.5,
                                                    ft.colors.with_opacity(
                                                        0.045, "white"
                                                    ),
                                                ),
                                                content=ft.Text(
                                                    "Все дни",
                                                    font_family="Consolas",
                                                    size=18,
                                                ),
                                                border_radius=10,
                                                padding=10,
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(
                                                    "*количество решенных задач, за каждый день когда они решались",
                                                    font_family="Consolas",
                                                    size=13,
                                                    color=ft.colors.with_opacity(
                                                        0.45, "white"
                                                    ),
                                                ),
                                            )
                                        ],
                                        alignment="center",
                                    ),
                                    self.group_line_chart,
                                ]
                            ),
                        ),
                    ]
                ),
                # StatisticPage(),
            ],
        )


def main(page: ft.Page):
    page.add(StatisticPage())
    # data_1 = [
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 1),
    #             ft.LineChartDataPoint(3, 1.5),
    #             ft.LineChartDataPoint(5, 1.4),
    #             ft.LineChartDataPoint(7, 3.4),
    #             ft.LineChartDataPoint(10, 2),
    #             ft.LineChartDataPoint(12, 2.2),
    #             ft.LineChartDataPoint(13, 1.8),
    #         ],
    #         stroke_width=8,
    #         color=ft.colors.LIGHT_GREEN,
    #         curved=True,
    #         stroke_cap_round=True,
    #     ),

    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 1),
    #             ft.LineChartDataPoint(3, 2.8),
    #             ft.LineChartDataPoint(7, 1.2),
    #             ft.LineChartDataPoint(10, 2.8),
    #             ft.LineChartDataPoint(12, 2.6),
    #             ft.LineChartDataPoint(13, 3.9),
    #         ],
    #         color=ft.colors.PINK,
    #         below_line_bgcolor=ft.colors.with_opacity(0, ft.colors.PINK),
    #         stroke_width=8,
    #         curved=True,
    #         stroke_cap_round=True,
    #     ),
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 2.8),
    #             ft.LineChartDataPoint(3, 1.9),
    #             ft.LineChartDataPoint(6, 3),
    #             ft.LineChartDataPoint(10, 1.3),
    #             ft.LineChartDataPoint(13, 2.5),
    #         ],
    #         color=ft.colors.CYAN,
    #         stroke_width=8,
    #         curved=True,
    #         stroke_cap_round=True,
    #     ),
    # ]

    # data_2 = [
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 1),
    #             ft.LineChartDataPoint(3, 4),
    #             ft.LineChartDataPoint(5, 1.8),
    #             ft.LineChartDataPoint(7, 5),
    #             ft.LineChartDataPoint(10, 2),
    #             ft.LineChartDataPoint(12, 2.2),
    #             ft.LineChartDataPoint(13, 1.8),
    #         ],
    #         stroke_width=4,
    #         color=ft.colors.with_opacity(0.5, ft.colors.LIGHT_GREEN),
    #         below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.LIGHT_GREEN),
    #         stroke_cap_round=True,
    #     ),
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 1),
    #             ft.LineChartDataPoint(3, 2.8),
    #             ft.LineChartDataPoint(7, 1.2),
    #             ft.LineChartDataPoint(10, 2.8),
    #             ft.LineChartDataPoint(12, 2.6),
    #             ft.LineChartDataPoint(13, 3.9),
    #         ],
    #         color=ft.colors.with_opacity(0.5, ft.colors.PINK),
    #         below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.PINK),
    #         stroke_width=4,
    #         curved=True,
    #         stroke_cap_round=True,
    #     ),
    #     ft.LineChartData(
    #         data_points=[
    #             ft.LineChartDataPoint(1, 3.8),
    #             ft.LineChartDataPoint(3, 1.9),
    #             ft.LineChartDataPoint(6, 5),
    #             ft.LineChartDataPoint(10, 3.3),
    #             ft.LineChartDataPoint(13, 4.5),
    #         ],
    #         color=ft.colors.with_opacity(0.5, ft.colors.CYAN),
    #         below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.CYAN),
    #         stroke_width=4,
    #         stroke_cap_round=True,
    #     ),
    # ]

    # chart = ft.LineChart(
    #     data_series=data_1,
    #     border=ft.Border(
    #         bottom=ft.BorderSide(4, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
    #     ),
    #     left_axis=ft.ChartAxis(
    #         labels=[
    #             ft.ChartAxisLabel(
    #                 value=1,
    #                 label=ft.Text("1m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=2,
    #                 label=ft.Text("2m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=3,
    #                 label=ft.Text("3m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=4,
    #                 label=ft.Text("4m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=5,
    #                 label=ft.Text("5m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=6,
    #                 label=ft.Text("6m", size=14, weight=ft.FontWeight.BOLD),
    #             ),
    #         ],
    #         labels_size=40,
    #     ),
    #     bottom_axis=ft.ChartAxis(
    #         labels=[
    #             ft.ChartAxisLabel(
    #                 value=2,
    #                 label=ft.Container(
    #                     ft.Text(
    #                         "SEP",
    #                         size=16,
    #                         weight=ft.FontWeight.BOLD,
    #                         color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
    #                     ),
    #                     margin=ft.margin.only(top=10),
    #                 ),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=7,
    #                 label=ft.Container(
    #                     ft.Text(
    #                         "OCT",
    #                         size=16,
    #                         weight=ft.FontWeight.BOLD,
    #                         color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
    #                     ),
    #                     margin=ft.margin.only(top=10),
    #                 ),
    #             ),
    #             ft.ChartAxisLabel(
    #                 value=12,
    #                 label=ft.Container(
    #                     ft.Text(
    #                         "DEC",
    #                         size=16,
    #                         weight=ft.FontWeight.BOLD,
    #                         color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
    #                     ),
    #                     margin=ft.margin.only(top=10),
    #                 ),
    #             ),
    #         ],
    #         labels_size=32,
    #     ),
    #     tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
    #     min_y=0,
    #     max_y=4,
    #     min_x=0,
    #     max_x=14,
    #     # animate=5000,
    #     expand=True,
    # )

    # def toggle_data(e):
    #     if s.toggle:
    #         chart.data_series = data_2
    #         chart.data_series[2].point = True
    #         chart.max_y = 6
    #         chart.interactive = False
    #     else:
    #         chart.data_series = data_1
    #         chart.max_y = 4
    #         chart.interactive = True
    #     s.toggle = not s.toggle
    #     chart.update()

    # page.add(ft.IconButton(ft.icons.REFRESH, on_click=toggle_data), chart)


ft.app(main)
