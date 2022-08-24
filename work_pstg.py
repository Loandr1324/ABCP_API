import psycopg2
from config import HOST, DB_NAME, SSH_username, SSH_password, DB_user_name
import logging
from sshtunnel import SSHTunnelForwarder # TODO Удалить после тестов


def action_db(action=None, data=None):
    """
    Подключаемся к базе данных и выполняем действие согласно action с данными data.

    action = 'ins_pay':

    :param action: action = 'check_pay': проверяем есть ли в базе данных платёж.
    :param data: при action = 'check_pay' передаём id платежа.
    :param action: action = 'ins_pay': добавляем в базу данных новый платёж
    :param data: при action = 'ins_pay' передаём словарь с данными платежа из ABCP
    :return: result
    """
    connection = False
    result = None
    try:
        # Создаём тоннель по SSH
        with SSHTunnelForwarder(
                ('192.168.100.107', 22),
                ssh_username=SSH_username,
                ssh_password=SSH_password,
                remote_bind_address=('192.168.100.107', 5432)
        ) as server:

            # Подключаемся к Базе данных
            connection = psycopg2.connect(
                # host=host, # TODO Раскомментировать после тестов
                user=DB_user_name,
                database=DB_NAME,
                port=server.local_bind_port
            )
            connection.autocommit = True
            cursor = connection.cursor()

            def check_new_pay(id_pay):
                """
                Проверяем наличие оплаты в базе данных

                :param id_pay: int Id оплаты полученной от ABCP
                :return: список tuple с результатом запроса
                """
                logging.info(f"Send a payment {id_pay} request to the database")
                cursor.execute(f"SELECT id_pay FROM online_payments WHERE id_pay = {id_pay}")
                return cursor.fetchall()

            def ins_db_new_apy(dict_pay):
                """
                Добавляем данные о новой оплату в базу данных online_payments

                :param dict_pay: словарь с данными об оплате полученные из ABCP_API
                :return:
                """
                logging.info(f"Adding a new payment to the database {dict_pay['id']}")

                cursor.execute(
                    f"INSERT INTO online_payments VALUES ("
                    f"{int(dict_pay['id'])}, "
                    f"'{dict_pay['dateTime']}', "
                    f"{int(dict_pay['customerId'])}, "
                    f"'{dict_pay['customerName']}', "
                    f"{int(dict_pay['office'])}, "
                    f"{int(dict_pay['orderId'])}, "
                    f"{int(dict_pay['amount'])}, "
                    f"'new'"
                    f");"
                )
                logging.info(f"Entry {dict_pay['id']} successfully added to payment table")
                return


            if action == 'check_pay':
                result = check_new_pay(data)
            elif action == 'ins_pay':
                ins_db_new_apy(data)
    except Exception as _ex:
        logging.error(f"Произошла ошибка при подключении к базе данных {_ex}") # Заменить print на logging

    finally:
        if connection:
            server.close()
            connection.close()
    return result
