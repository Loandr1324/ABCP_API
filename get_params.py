import config
from config import start_end_time
import logging
from datetime import datetime, timedelta


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

        dateStart, dateEnd = start_end_time()
        dateStart = dateStart.strftime('%Y-%m-%d')
        dateEnd = dateEnd.strftime('%Y-%m-%d')

        params = config.GENERAL_PARAMS.copy()
        params.update({
            'filter[dateStart]': dateStart,
            'filter[dateEnd]': dateEnd,
            'filter[statusIds][]': 2
        })

        logging.info(f"{datetime.utcnow()} - Set params for payments\nDate start = {dateStart}\nDate end = {dateEnd}")


    else:
        # Задаём переменные запроса по покупателям по периоду регистрации
        url = config.GLOBAL_URL + 'cp/users'

        dateRegStart, dateRegEnd = start_end_time()
        dateRegStart = dateRegStart.strftime('%Y-%m-%d %H:%M:%S')
        dateRegEnd = dateRegEnd.strftime('%Y-%m-%d %H:%M:%S')

        params.update({
            'dateRegistredStart': dateRegStart,
            'dateRegistredEnd': dateRegEnd
        })

        logging.info(f"{datetime.utcnow()} - Set params for users\nDate start = {dateRegStart}\nDate end = {dateRegEnd}")

    return url, params