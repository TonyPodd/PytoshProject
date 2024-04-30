import pymysql
from config import *

try:
    connection = pymysql.Connection(
        host=host,
        user=user,
        password=password,
        database=name,
        cursorclass=pymysql.cursors.DictCursor,
        port=3306
    )
    print('Ok')
    try:
        with connection.cursor() as cursor:
            create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    TYPE ENUM('teacher', 'student') NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """
            create_user_groups_table = """
                CREATE TABLE IF NOT EXISTS user_groups (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    group_id INT,
                    FOREIGN KEY (user_id) REFERENCES users(ID),
                    FOREIGN KEY (group_id) REFERENCES user_groups(ID)
                )
            """
            create_themes_table = """
                CREATE TABLE IF NOT EXISTS themes (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    group_id INT,
                    FOREIGN KEY (group_id) REFERENCES user_groups(ID)
                )
            """
            create_tasks_table = """
                CREATE TABLE IF NOT EXISTS tasks (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    description TEXT NOT NULL,
                    theme_id INT,
                    FOREIGN KEY (theme_id) REFERENCES themes(ID)
                )
            """
            create_tests_table = """
                CREATE TABLE IF NOT EXISTS tests (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    task_id INT,
                    num INT,
                    input TEXT NOT NULL,
                    output TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(ID)
                )
            """
            create_sendings_table = """
                CREATE TABLE IF NOT EXISTS sendings (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    code TEXT NOT NULL,
                    author INT,
                    task_id INT,
                    verdict VARCHAR(255),
                    FOREIGN KEY (author) REFERENCES users(ID),
                    FOREIGN KEY (task_id) REFERENCES tasks(ID)
                )
            """

            cursor.execute(create_users_table)
            cursor.execute(create_user_groups_table)
            cursor.execute(create_themes_table)
            cursor.execute(create_tasks_table)
            cursor.execute(create_tests_table)
            cursor.execute(create_sendings_table)

        connection.commit()

    finally:
        connection.close()
        print('All correct!!!')

except Exception as e:
    print("Error...")
    print(e)
