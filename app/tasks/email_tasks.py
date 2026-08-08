import asyncio
from typing import Optional

from pydantic import EmailStr
from app.core.mail import fm
from app.core.celery_app import celery
from fastapi_mail import MessageSchema

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

    except Exception as e:
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

    except Exception as e:
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

    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_reservation_created_email(
    self,
    user_email: EmailStr,
    user_name: str,
    reservation_name: str,
    start_date: str,
    start_time: str,
    end_date: Optional[str] = None,
    end_time: Optional[str] = None,
):
    try:
        message = MessageSchema(
            subject="Tu reserva está confirmada",
            recipients=[user_email],
            template_body={
                "user_name": user_name,
                "reservation_name": reservation_name,
                "start_date": f"{date_formatter(start_date)} {time_to_12h(start_time)}",
                "end_date": f"{date_formatter(end_date)} {time_to_12h(end_time)}",
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="reservation_created.html"
            )
        )

    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_reservation_cancelled_email(
    self,
    user_email: EmailStr,
    user_name: str,
    user_first_surname: str,
    reservation_name: str,
    start_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_date: Optional[str] = None,
    end_time: Optional[str] = None,
):
    try:
        message = MessageSchema(
            subject="Tu reserva fue cancelada",
            recipients=[user_email],
            template_body={
                "user_name": user_name,
                "user_first_surname": user_first_surname,
                "reservation_name": reservation_name,
                "start_date": f"{date_formatter(start_date)} {time_to_12h(start_time)}",
                "end_date": f"{date_formatter(end_date)} {time_to_12h(end_time)}",
            },
            subtype="html",
        )

        asyncio.run(
            fm.send_message(
                message, template_name="reservation_cancelled.html"
            )
        )

    except Exception as e:
        raise self.retry(exc=e, countdown=60)
