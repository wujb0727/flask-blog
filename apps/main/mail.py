from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from apps import mail


def send_mail(to, subject, template, **kwargs):
    """
    发送邮件
    :param to:邮件的接收方
    :param subject:邮件主题
    :param template:邮件正文模板的路径
    :param kwargs:用来渲染邮件正文模板的 变量
    :return:
    """
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_async_mail, args=(current_app._get_current_object(), msg))
    thread.start()
    return thread


# 异步发送邮件
def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)
