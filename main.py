# Author Loik Andrey 7034@balancedv.ru
import config
import send_mail
from get_params import get_url_params
from post_params import post_url_params_setprofile
import work_pstg
import requests
import logging
import time
from datetime import datetime, timedelta

logging.basicConfig(filename="abcp_api.log", level=logging.INFO)


def req_get_abcp(url_params):
    """
    Посылаем GET-запрос согласно переданных параметров из url_params => (url, params)

    :return: list словарей с данными ответа
    """
    try:
        req = requests.get(url_params[0], params=url_params[1])

        if req.status_code == 200 and len(req.json()) > 0:
            logging.info(f"{datetime.utcnow()} - Correct answer. Working...")
            return req.json()

        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f"{datetime.utcnow()} - Empty answer.\n"
                         f"Not new data, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
            return {}

    except BaseException:
        logging.exception(f"{datetime.utcnow()} - Failed to send GET request:\n{BaseException}")
        return {}


def req_post_abcp(url_params):
    """
    Посылаем POST-запрос согласно переданных параметров из url_params => (url, params)

    :return: list словарей с данными ответа
    """

    try:
        req = requests.post(url_params[0], data=url_params[1])

        if req.status_code == 200 and len(req.json()) > 0:
            logging.info(f"{datetime.utcnow()} - Correct answer. Working...")
            return req.json()

        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f"{datetime.utcnow()} - Empty answer.\n"
                         f"Not new data, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
            return {}

    except BaseException:
        logging.exception(f"{datetime.utcnow()} - Failed to send POST request:\n{BaseException}")
        return {}


def set_profile_clients(js):
    """
    Подставляем базовый профиль согласно офису нового клиента

    :param js: json массив словарей с данными клиентов

    :return: None
    """

    for item in js:
        # Отрабатываем подстановку офиса только для клиентов с базовым профилем без платёжных систем
        if item['profileId'] == config.BASE_PROFILE:

            # Отрабатываем подстановку профиля если у клиента только один офис
            if len(item['offices']) == 1:

                logging.info(f"{datetime.utcnow()} - The client has one office: {item['offices'][0]}. Set profile.")

                # Получаем параметры для отправки POST-запроса
                url_params = post_url_params_setprofile(item['userId'], item['offices'][0])

                # Выполняем POST запрос на подстановку офиса
                req_set_user_profile = req_post_abcp(url_params)

                # Логируем результаты выполнения POST запроса подстановки офиса
                if len(req_set_user_profile) > 0:
                    logging.info(f"{datetime.utcnow()} - "
                                 f"Client {req_set_user_profile['userId']} successfully installed profile "
                                 f"{req_set_user_profile['profileId']}"
                                 )
                else:
                    logging.error(f"{datetime.utcnow()} - "
                                  f"Client {item['userId']} failed to install profile {item['profileId']}"
                                  )
            else:
                # Логируем ошибку, в случае количества офисов больше одного
                logging.error(
                    f" { datetime.utcnow()} - "
                    f"Quantity client offices: {len(item['offices'])}."
                    f"It is not possible to automatically install a profile."
                    f"Requires manual installation."
                    )

        else:
            # Логируем, если у пользователя не нужно менять офис
            logging.info(
                f" {datetime.utcnow()} - "
                f"Do not change. Client {item['userId']} the correct profile {item['profileId']}."
                )
    return


def check_add_new_pay(js):
    """
    Проверяем есть ли новые оплаты из полученного списка оплат.

    :param js: список словарей по новым оплатам из запроса на платформу ABCP

    :return:
    """

    # Проходим по каждому элементу со списком оплат
    for item in js:
        id_pay = item['id']

        # Отправляем запрос в базу данных по платежу
        res = work_pstg.check_new_pay(item['id'])

        # Если платежа нет в базе данных платежей, значит он новый.
        # Тогда отправляем письмо менеджерам офиса и добавляем платёж в базу данных
        if res is None:
            logging.error(f"{datetime.utcnow()} - Can't check payment. No command or invalid database query")

        elif len(res) == 0:
            # Логируем информацию по новому платежу
            logging.info(f"{datetime.utcnow()} - New pay: {id_pay} client Id: {item['customerId']}")

            # Определяем офис клиента для дальнейшей отправки писем менеджерам этого офиса.
            # TODO Перенести запросы по офису в базу данных
            req_param_user = get_url_params(user=item['customerId'])
            client = req_get_abcp(req_param_user)[0]

            if len(client) > 0:
                if len(client['offices']) == 1:
                    logging.info(f"{datetime.utcnow()} - "
                                 f"Client: {item['customerId']} have office: {client['offices'][0]}"
                                 )
                    item['office'] = client['offices'][0] # Добавляем офис клиента в словарь с новой оплатой
                else:
                    logging.error(
                        f" {datetime.utcnow()} - "
                        f"Quantity client offices: { len(client['offices']) }."
                        f"It is not possible to send email."
                    )
                    return

                # Получение списка email сотрудников по номеру офиса
                logging.info(f"{datetime.utcnow()} - Create list email mangers office {item['office']}")
                # TODO Перенести запрос по списку мэйлов менеджеров в базу данных
                email_list = check_dict_mng(item['office'])

                # Отправка информации на почту сотрудников офиса
                logging.info(f"{datetime.utcnow()} - Send email mangers office {email_list}")

                # Подготавливаем текст письма
                message = send_mail.mes_new_pay(item)

                # Отправляем письмо менеджерам о новой оплате
                # email_list = []  # TODO используем при тестах
                send_mail.send(email_list, message)

                # Добавление новой оплаты в базу данных
                work_pstg.ins_db_new_pay(item)
        else:
            logging.info(f"{datetime.utcnow()} - No new payments")
    return


def check_dict_mng(office):
    """
    Проверяем есть ли в словаре LIST_EMAIL_MENAGER офис с адресами почты менеджеров.
    Если данных нет или они устарели, то перезаполняет словарь.

    :param office: str - Id офиса

    :return: dict, где ключи это тип str Id офиса, а значения это тип list с адресами почты
    """
    if len(config.LIST_EMAIL_MENAGER) == 0:
        update_dict_mng()
    elif config.LIST_EMAIL_MENAGER['updateDate'] < datetime.utcnow() - timedelta(days=31):
        update_dict_mng()
    return config.LIST_EMAIL_MENAGER['email_offices'][office]


def update_dict_mng():
    """
    Обновляем список email адресов сотрудников по офисам и заполняем ими глобальный словарь LIST_EMAIL_MENAGER
    """
    # Записываем дату обновления
    config.LIST_EMAIL_MENAGER['updateDate'] = datetime.utcnow()

    # Получаем массив сотрудников
    req_param_mng = get_url_params(managers=True)
    js_managers = req_get_abcp(req_param_mng)

    # Записываем email адреса сотрудников по офисам
    config.LIST_EMAIL_MENAGER['email_offices'] = dict.fromkeys(config.LIST_IdOffice_AV + config.LIST_IdOffice_SV, [])

    for item in config.LIST_EMAIL_MENAGER['email_offices']:
        list_emails = [i['email'] for i in js_managers if i['officeId'] == item]
        config.LIST_EMAIL_MENAGER['email_offices'][item] = list_emails
    return


def pause_work_time():
    """
    Определяем количество секунд паузы в зависимости от рабочего времени

    :return: int -> Количество секунд
    """
    hour_utc = datetime.utcnow().strftime('%H')  # Получаем текущий час по UTC
    # Выбираем количество секунд паузы, согласно рабочему графику сотрудников и логируем
    # Рабочее время сотрудников по часовому поясу UTC с 23 до 9
    if 23 > int(hour_utc) >= 9:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_utc}. Pause 50 min. Working hours from 23 to 9")
        pause_sec = config.sleep_non_work
    else:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_utc}. Pause 5 min. Working hours from 23 to 9")
        pause_sec = config.sleep_work
    return pause_sec


def main():
    while True:
        # Получаем массив новых клиентов
        req_param_users = get_url_params()  # Получаем параметры запроса по пользователям
        js_user_id = req_get_abcp(req_param_users)

        # Подставляем профиль если полученный массив не пустой
        if len(js_user_id) > 0:
            # print(js_user_id) # TODO Удалить после тестов
            set_profile_clients(js_user_id)

        time.sleep(5)

        # Получаем массив новых оплат
        req_param_payments = get_url_params(payments=True)  # Получаем параметры запроса по оплатам
        js_payments = req_get_abcp(req_param_payments)

        # Проверяем новые оплаты и отправляем письма
        if len(js_payments) > 0:
            # print(js_payments) # TODO Удалить после тестов
            check_add_new_pay(js_payments)

        # Устанавливаем паузу согласно рабочему времени
        time.sleep(pause_work_time())


def main1():
    # Получаем массив новых оплат
    req_param_payments = get_url_params(payments=True)  # Получаем параметры запроса по оплатам
    js_payments = req_get_abcp(req_param_payments)

    # Проверяем новые оплаты и отправляем письма
    if len(js_payments) > 0:
        print(js_payments)
        check_add_new_pay(js_payments)


def main2():
    # work_pstg()
    pass


if __name__ == '__main__':
    main()
    # main1()
    # main2()
