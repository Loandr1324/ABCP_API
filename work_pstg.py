import psycopg2
from config import DATABASES
import logging
from sshtunnel import SSHTunnelForwarder # TODO Удалить после тестов


def action_db(query):
    """
    Подключаемся к базе данных и выполняем запрос query.

    :param query: str -> Запрос к базе данных на языке postgresql
    :return: result -> Результат запроса, если он есть
    """
    connection = False
    result = None
    try:
        # Создаём тоннель по SSH
        # with SSHTunnelForwarder(
        #         ('192.168.100.107', 22),
        #         ssh_username=DATABASES['SSH_username'],
        #         ssh_password=DATABASES['SSH_password'],
        #         remote_bind_address=('192.168.100.107', 5432)
        # ) as server:
        #
        #     # Подключаемся к Базе данных
        #     connection = psycopg2.connect(
        #         user=DATABASES['DB_user_name'],
        #         database=DATABASES['DB_NAME'],
        #         password=DATABASES['DB_password'],
        #         port=server.local_bind_port
        #     )  # TODO Раскомментировать при тестах

        # Подключаемся к Базе данных TODO Закомментировать при тестах
        with psycopg2.connect(
                host=DATABASES['HOST'],
                user=DATABASES['DB_user_name'],
                database=DATABASES['DB_NAME'],
                password=DATABASES['DB_password']
        ) as connection:

            connection.autocommit = True # Задаём автоматическое подтверждение запроса
            cursor = connection.cursor()

            # Отправляем запрос в БД
            cursor.execute(query)

            # Возвращаем результат запроса, если он есть
            try:
                return cursor.fetchall()
            except BaseException as _ex:
                print(_ex)
                return

    except Exception as _ex:
        logging.error(f"Произошла ошибка при подключении к базе данных {_ex}") # Заменить print на logging

    finally:
        if connection:
            connection.close()


def check_new_pay(id_pay):
    """
    Проверяем наличие оплаты в базе данных

    :param id_pay: int Id оплаты полученной от ABCP
    :return: список tuple с результатом запроса
    """
    logging.info(f"Send a payment {id_pay} request to the database")
    query_bd = f"SELECT id_pay FROM online_payments WHERE id_pay = {id_pay}"
    result = action_db(query_bd)
    return result


def ins_db_new_pay(dict_pay):
    """
    Добавляем данные о новой оплате в базу данных online_payments

    :param dict_pay: словарь с данными об оплате полученные из ABCP_API
    :return:
    """
    logging.info(f"Adding a new payment to the database {dict_pay['id']}")

    query_bd = f"INSERT INTO online_payments VALUES (" \
               f"{int(dict_pay['id'])}, " \
               f"'{dict_pay['dateTime']}', " \
               f"{int(dict_pay['customerId'])}, " \
               f"'{dict_pay['customerName']}', " \
               f"{int(dict_pay['office'])}, " \
               f"{int(dict_pay['orderId'])}, " \
               f"{int(dict_pay['amount'])}, " \
               f"'new'" \
               f");"
    result = action_db(query_bd)
    logging.info(f"Entry {dict_pay['id']} successfully added to payment table")
    print(f"result: {result}")
    return


def list_email_manager(office):
    """
    Возвращает список мэйл адресов сотрудников офиса

    :param office: int or str номер id офиса
    :return: list мэйл адресов
    """
    import json
    logging.info(f"Get a list of office email addresses {office}")
    query_bd = f"SELECT email FROM managers WHERE office_id = {office}"
    result = action_db(query_bd)
    logging.info(f"Successfully list email addresses {result}")
    return [i[0] for i in result]
