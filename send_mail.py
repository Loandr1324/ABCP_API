from config import log_mail, psw_mail, LIST_EMAIL_IGNOR, EMAIL_ADMIN
from datetime import datetime, timedelta
import logging
import smtplib  # Импортируем библиотеку по работе с SMTP

# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.text import MIMEText  # Текст/HTML


def send(to_emails=None, message=None):
    """
    Отправляем письмо

    :param to_emails: list or str список адресов
    :param message: dict
        {
        'Subject': str - Тема письма
        'email_content': str - Текст письма
        }
    :return:
    """
    if to_emails is None or message is None:
        logging.error(f"{datetime.utcnow()}"
                      f" - No options to send email. Pass all parameters to the function: 'to_emails' and 'message'")
    else:
        logging.info(f"{datetime.utcnow()} - Send message to emails...")

        addr_from = log_mail  # Отправитель
        # Убираем из адресов получателей игнор список адресов и добавляем адрес администратора
        addr_to = [mail for mail in to_emails if mail not in LIST_EMAIL_IGNOR] + EMAIL_ADMIN
        # print(f'Correct list email: {addr_to}') # TODO Удалить после тестов
        # addr_to = ['7034@balancedv.ru'] #TODO Удалить после тестов

        password = psw_mail  # Пароль

        msg = MIMEMultipart()  # Создаем сообщение
        msg['From'] = addr_from  # Адресат
        msg['To'] = ','.join(addr_to)  # Получатель
        msg['Subject'] = message['Subject']  # Тема сообщения

        # Текст сообщения в формате html
        email_content = message['email_content']

        msg.attach(MIMEText(email_content, 'html'))  # Добавляем в сообщение html

        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)  # Создаем объект SMTP
        # server.starttls()                                  # Начинаем шифрованный обмен по TLS
        server.login(addr_from, password)  # Получаем доступ
        server.send_message(msg)  # Отправляем сообщение
        server.quit()  # Выходим
        logging.info(f"{datetime.utcnow()} - Mail sending completed")
    return


def mes_new_pay(dict_pay=None):
    """
    Создаём текст письма по оплатам

    :param dict_pay: Словарь с информацией по оплатам клиентов
        {
            'date': str,
            'clientName': str,
            'orderId': str,
            'amount': str в формате округлённого целого числа
        }
    :return: str текст сообщения
    """
    # Переводим дату с Московского на наше время
    date_pay = datetime.strptime(dict_pay['date'], '%Y-%m-%d %H:%M:%S')
    date_pay = date_pay + timedelta(hours=7)
    amount = '{:,}'.format(int(dict_pay['amount'])).replace(',', ' ')

    text = {'Subject': f"Проведение online-оплаты от клиента {dict_pay['clientName']}"}
    if dict_pay is not None:
        text['email_content'] = f"""
        <html>
          <head></head>
          <body>
            <p>
                Проведена online - оплата<br>
                Клиент: {dict_pay['clientName']}<br>
                Дата и время: {date_pay}<br>
                Сумма: {amount},00 руб.<br>
                &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;&nbsp;
                <br>
    
                <a href="https://cp.abcp.ru/?page=orders&id_order={dict_pay['orderId']}">
                    Перейти к заказу: {dict_pay['orderId']}
                </a>
                &emsp;
                <b></b>
            </p>
          </body>
        </html>
        """
    else:
        text['email_content'] = "Ошибка!!!\nИнформации по оплатам нет. Обратитесь к администратору."
    return text
