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
    :param message:
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
    date_pay = datetime.strptime(dict_pay['dateTime'], '%Y-%m-%d %H:%M:%S')
    date_pay = date_pay + timedelta(hours=7)
    date_pay = datetime.strftime(date_pay, '%Y-%m-%d в %H:%M:%S')
    amount = '{:,}'.format(int(dict_pay['amount'])).replace(',', ' ')

    if dict_pay is not None:
        text = {'Subject': f"Проведение online-оплаты от клиента {dict_pay['customerName']}",
                'email_content': f"""
        <html>
          <head></head>
          <body>
            <table align="center" cellpadding="0" cellspacing="0" width="710" style="font-family:'arial', 
            sans-serif;font-size:13px;margin:0">
                <tbody>
                    <tr>
                        <td style="border:20px solid #e3f8ff">
                            <table cellpadding="0" cellspacing="0" width="100%">
                                <tbody>
                            <tr>
                        <td style="padding:15px 15px 0 15px">
                            <span style="display:block;font-size:15px">Проведена оплата</span>
                        </td>
                            </tr>
                            <tr>
                        <td style="border-bottom-color:#e3f8ff;
                        border-bottom-style:solid;
                        border-bottom-width:10px;
                        padding:15px">
                            <p style="margin:3px 0 3px 0"><b>Клиент:</b> {dict_pay['customerName']}</p>
                            <p style="margin:3px 0 3px 0"><b>Дата и время:</b> {date_pay}</p>
                            <p style="margin:3px 0 3px 0"><b>Сумма:</b> {amount},00р.</p>
                            <p style="margin:3px 0 3px 0"><b>Тип платежа:</b> Онлайн оплата через сайт</p>
                            <p style="margin:3px 0 3px 0">
                                <a href="https://cp.abcp.ru/?page=orders&id_order={dict_pay['orderId']}">
                                    <b>Перейти к заказу:</b> {dict_pay['orderId']}
                                </a>
                            </p>
                        </td>
                            </tr>
                            <tr>
                        <td style="padding:15px">С Уважением, <br> 
                            <a href="https://macardv.ru/" data-link-id="37" target="_blank" rel="noopener noreferrer">
                                https://macardv.ru
                            </a>
                        </td>
                            </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
          </body>
        </html>
        """}
    else:
        text = {'Subject': f"Ошибка при отправке письма. Пустая оплата",
                'email_content': "Ошибка!!!\nИнформации по оплатам нет. Обратитесь к администратору."}
    return text
