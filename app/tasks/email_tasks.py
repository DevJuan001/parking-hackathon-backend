import asyncio
import smtplib
from datetime import date, datetime, time, timedelta

from fastapi_mail import MessageSchema
from pydantic import EmailStr

from app.core.celery_app import celery
from app.core.mail import fm
from app.utils.date_formatter import date_formatter, time_to_12h


@celery.task(bind=True, max_retries=3)
def send_welcome_email(self, user_name: str, user_first_surname: str, user_email: EmailStr, password: str):
    try:
        message = MessageSchema(
            subject="Bienvenido a Tracklinker",
            recipients=[user_email],
            template_body={
                "name": user_name,
                "surname": user_first_surname,
                "email": user_email,
                "password": password
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="welcome_mail.html"
            )
        )

    except (ConnectionError, TimeoutError, OSError, smtplib.SMTPException) as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def recovery_password_email(self, user_email: EmailStr, user_name: str):
    try:
        message = MessageSchema(
            subject="Recuperación de contraseña",
            recipients=[user_email],
            template_body={"name": user_name},
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="recover_password.html"
            )
        )

    except (ConnectionError, TimeoutError, OSError, smtplib.SMTPException) as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_welcome_registration_email(
    self,
    user_name: str,
    user_first_surname: str,
    user_email: EmailStr
):
    try:
        message = MessageSchema(
            subject="Bienvenido a Parking Hackathon",
            recipients=[user_email],
            template_body={
                "name": user_name,
                "surname": user_first_surname
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="welcome_registration_mail.html"
            )
        )

    except (ConnectionError, TimeoutError, OSError, smtplib.SMTPException) as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_reservation_created_email(
    self,
    user_email: EmailStr,
    user_name: str,
    parking_name: str,
    parking_location: str,
    reservation_id: int,
    reservation_name: str,
    total: str,
    payment_status: str,
    start_date: str,
    start_time: time,
    end_date: str | None = None,
    end_time: time | None = None,
):
    try:
        raw_end_time = end_time if end_time else (
            datetime.combine(date.min, start_time) + timedelta(minutes=30)
        )

        message = MessageSchema(
            subject="Tu reserva está confirmada",
            recipients=[user_email],
            template_body={
                "user_name": user_name,
                "parking_name": parking_name,
                "parking_location": parking_location,
                "reservation_id": reservation_id,
                "reservation_name": reservation_name,
                "total": total,
                "payment_status": payment_status,
                "raw_start_date": f"{start_date}T{start_time}",
                "raw_end_date": f"{end_date if end_date else start_date}T{raw_end_time}",
                "start_date": f"{date_formatter(start_date)} {time_to_12h(start_time)}",
                "end_date": f"{date_formatter(end_date)} {time_to_12h(end_time)}" if end_date and end_time else "",
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="reservation_created.html"
            )
        )

    except (ConnectionError, TimeoutError, OSError, smtplib.SMTPException) as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_reservation_cancelled_email(
    self,
    user_email: EmailStr,
    user_name: str,
    reservation_id: int,
    reservation_name: str,
    template_name: str,
    start_date: date | None = None,
    start_time: time | None = None,
    end_date: date | None = None,
    end_time: time | None = None,
):
    try:
        message = MessageSchema(
            subject="Tu reserva fue cancelada",
            recipients=[user_email],
            template_body={
                "user_name": user_name,
                "reservation_id": reservation_id,
                "reservation_name": reservation_name,
                "start_date": f"{date_formatter(start_date)} {time_to_12h(start_time)}",
                "end_date": f"{date_formatter(end_date)} {time_to_12h(end_time)}" if end_date and end_time else "",
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name=template_name
            )
        )

    except (ConnectionError, TimeoutError, OSError, smtplib.SMTPException) as e:
        raise self.retry(exc=e, countdown=60)
