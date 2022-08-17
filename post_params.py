import config
import logging
from datetime import datetime


def post_url_params_setprofile(user_id, office):
    """
    Получаем Id клиента и Id офиса клиента

    :param user_id: строка str - цифровой код клиента.
    :param office: строка str - цифровой код офиса клиента.
    :return: url, params POST-запроса для установки базового профиля клиента согласно его офиса
    """

    url = config.GLOBAL_URL + 'cp/user'

    params = config.GENERAL_PARAMS.copy()
    params['userId'] = user_id

    # Подставляем базовый профиль согласно офису клиента в параметры запроса
    if office in config.LIST_IdOffice_SV:
        params['profileId'] = config.profileSV_ID

    elif office in config.LIST_IdOffice_AV:
        params['profileId'] = config.profileAV_ID

    logging.info(f"{datetime.utcnow()} - Set params for post request user")
    return url, params
