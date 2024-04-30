import pymysql
from sqlalchemy import create_engine, Column, Integer, String, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from database.config import *

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TYPE = Column(Enum("teacher", "student"), nullable=False)
    email = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    groups = relationship("Group", secondary="user_groups")


class Group(Base):
    __tablename__ = "groups"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    leader = Column(Integer, ForeignKey("users.ID", ondelete="SET NULL"))
    description = Column(Text)
    participants = relationship(
        "User", secondary="user_groups", back_populates="groups"
    )
    themes = relationship("Theme", back_populates="group")


class UserGroup(Base):
    __tablename__ = "user_groups"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.ID", ondelete="CASCADE"))
    group_id = Column(Integer, ForeignKey("groups.ID", ondelete="CASCADE"))


class Theme(Base):
    __tablename__ = "themes"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.ID"))
    description = Column(Text, nullable=False)
    color = Column(Text, default="bluegrey900")
    group = relationship("Group", back_populates="themes")
    tasks = relationship("Task", back_populates="theme")


class Task(Base):
    __tablename__ = "tasks"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    theme_id = Column(Integer, ForeignKey("themes.ID"))

    theme = relationship("Theme", back_populates="tasks")
    tests = relationship("Test", back_populates="task")
    cost = Column(Integer, default=1)


class Test(Base):
    __tablename__ = "tests"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.ID"))
    num = Column(Integer, nullable=False, autoincrement=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)

    task = relationship("Task", back_populates="tests")


class Sending(Base):
    __tablename__ = "sendings"
    ID = Column(Integer, primary_key=True)
    code = Column(Text)
    author = Column(Integer)
    task_id = Column(Integer)
    verdict = Column(Text)
    total_tests = Column(Integer)
    accepted_tests = Column(Integer)
    info_test = Column(Text)
    time = Column(Text)
    num = Column(Integer)


class DatabaseManager:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, echo=False, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_task_to_theme(self, theme_id, description):
        task = Task(description=description, theme_id=theme_id)
        self.session.add(task)
        self.session.commit()

    def add_test_to_task(self, task_id, num, input_data, output_data):
        test = Test(task_id=task_id, num=num, input=input_data, output=output_data)
        self.session.add(test)
        self.session.commit()

    def update_task_description(self, task_id, new_description):
        task = self.session.query(Task).filter_by(ID=task_id).first()
        if task:
            task.description = new_description
            self.session.commit()

    def update_test_input_output(self, test_id, new_input=None, new_output=None):
        test = self.session.query(Test).filter_by(ID=test_id).first()
        if test:
            if new_input is not None:
                test.input = new_input
            if new_output is not None:
                test.output = new_output
            self.session.commit()

    def update_theme(self, theme_id, new_description):
        theme = self.session.query(Theme).filter_by(ID=theme_id).first()
        if theme:
            theme.description = new_description
            self.session.commit()

    def add_user(self, user_type, email, username, password):
        user = User(TYPE=user_type, email=email, username=username, password=password)
        self.session.add(user)
        self.session.commit()

    def remove_user(self, user_id):
        user = self.session.query(User).filter_by(ID=user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()

    def update_user_credentials(self, user_id, new_username=None, new_password=None):
        user = self.session.query(User).filter_by(ID=user_id).first()
        if user:
            if new_username:
                user.username = new_username
            if new_password:
                user.password = new_password
            self.session.commit()

    def create_group(self, leader_id, description):
        group = Group(leader=leader_id, description=description)
        self.session.add(group)
        self.session.commit()

    def add_user_to_group(self, user_id, group_id):
        user_group = UserGroup(user_id=user_id, group_id=group_id)
        self.session.add(user_group)
        self.session.commit()

    def create_theme(self, group_id, description):
        theme = Theme(group_id=group_id, description=description)
        self.session.add(theme)
        self.session.commit()

    def remove_theme(self, theme_id):
        theme = self.session.query(Theme).filter_by(ID=theme_id).first()
        if theme:
            for task in theme.tasks:
                self.remove_task(task.ID)
            self.session.delete(theme)
            self.session.commit()

    def remove_task(self, task_id):
        task = self.session.query(Task).filter_by(ID=task_id).first()
        if task:
            self.session.query(Sending).filter_by(task_id=task_id).delete()

            for test in task.tests:
                self.remove_test(test.ID)

            self.session.delete(task)
            self.session.commit()

    def remove_test(self, test_id):
        test = self.session.query(Test).filter_by(ID=test_id).first()
        if test:
            self.session.delete(test)
            self.session.commit()

    def save_solution(
        self,
        code,
        author_id,
        task_id,
        verdict="compiling",
        total_tests=0,
        accepted_tests=0,
        info_test="",
        time="",
        num=0,
    ):
        sending = Sending(
            code=code,
            author=author_id,
            task_id=task_id,
            verdict=verdict,
            total_tests=total_tests,
            accepted_tests=accepted_tests,
            info_test=info_test,
            time=time,
            num=num,
        )
        self.session.add(sending)
        self.session.commit()


if __name__ == "__main__":
    db_username = user
    db_password = password
    db_host = host
    db_name = name
    db_manager = DatabaseManager(
        f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"
    )
    # for i in range(9, 16):
    # db_manager.remove_user(15)
    # print(f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}")
    # db_manager.remove_user(5)
    # users = db_manager.session.query(User)
    # tasks = db_manager.session.query(Task).all()
    # for i in tasks:
    #     print(i.theme_id)
    # db_manager.remove_task(task_id=3)
    # db_manager.remove_theme(theme_id=1)
    # db_manager.add_user_to_group(user_id=1, group_id=1)
    # db_manager.remove_group(group_id=2)
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # db_manager.create_theme(group_id=1, description="Тема 1")
    # # db_manager.create_theme(group_id=1, description="Тем12312312")
    # for i in range(10):
    #     db_manager.add_task_to_theme(theme_id=2, description=f'Задание {i+2}')
    # db_manager.save_solution(author_id=1, task_id=6, code="print('hello)\nprint('world')")
