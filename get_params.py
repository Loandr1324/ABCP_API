import config
from config import start_end_time
import logging
from datetime import datetime


def get_url_params(user=None, managers=False, payments=False):
    """
    Получаем тип запроса и возвращаем url и params GET-запроса в зависимости от типа запроса.
    Если тип запроса не передан, то возвращаем параметры для получения списка покупателей за последний час.

    :param user: строка str userID. Передаётся в случае, когда необходимо получить информацию по одному клиенту,
    по его цифровому коду. По умолчанию None.
    :param managers: True. Передаётся если необходимо получить список сотрудников. По умолчанию False.
    :param payments: True. Передаётся если необходимо получить список новых оплат. По умолчанию False.
    :return: url, params для GET-запроса
    """
    params = config.GENERAL_PARAMS.copy()

    if user is not None:
        # Задаём переменные запроса покупателя по Id покупателя
        url = config.GLOBAL_URL + 'cp/users'
        params.update({
            'customersIds[]': user
        })
        logging.info(f"{datetime.utcnow()} - Set params for user {user}")

    elif managers:
        # Задаём переменные запроса по менеджерам
        url = config.GLOBAL_URL + 'cp/managers'

        logging.info(f"{datetime.utcnow()} - Set params for managers")

    elif payments:
        # Задаём переменные запроса по менеджерам
        url = config.GLOBAL_URL + 'cp/onlinePayments'

        date_start, date_end = start_end_time()
        date_start = date_start.strftime('%Y-%m-%d')
        date_end = date_end.strftime('%Y-%m-%d')

        params = config.GENERAL_PARAMS.copy()
        params.update({
            'filter[dateStart]': date_start,
            'filter[dateEnd]': date_end,
            'filter[statusIds][]': 2
        })

        logging.info(f"{datetime.utcnow()} - Set params for payments\nDate start = {date_start}\nDate end = {date_end}")

    else:
        # Задаём переменные запроса по покупателям по периоду регистрации
        url = config.GLOBAL_URL + 'cp/users'

        date_reg_start, date_reg_end = start_end_time()
        date_reg_start = date_reg_start.strftime('%Y-%m-%d %H:%M:%S')
        date_reg_end = date_reg_end.strftime('%Y-%m-%d %H:%M:%S')

        params.update({
            'dateRegistredStart': date_reg_start,
            'dateRegistredEnd': date_reg_end
        })

        logging.info(f"{datetime.utcnow()} - Set params for users\n"
                     f"Date start = {date_reg_start}\n"
                     f"Date end = {date_reg_end}")

    return url, params
