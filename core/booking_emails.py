"""Email helpers for the appointment booking flow.

Three transactional emails:

* ``send_confirmation_to_visitor`` — sent right after a slot is booked.
  Includes the meeting time in the visitor's local timezone and a
  cancel-by-link.
* ``send_notification_to_owner`` — internal notification so the owner
  sees the booking in their inbox immediately.
* ``send_cancellation_notice`` — tells both sides when a booking is
  cancelled via the cancel-link.

Failures here NEVER block the booking itself — the DB write happens
first and emails are best-effort. Each sender logs and swallows errors.
"""
import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _owner_email():
    """Resolve the notification recipient (owner) at send time."""
    try:
        from .models import SiteSettings
        s = SiteSettings.objects.first()
        if s and s.email:
            return s.email
    except Exception:
        pass
    return getattr(settings, 'BOOKING_OWNER_EMAIL', None) or settings.DEFAULT_FROM_EMAIL


def _from_email():
    return settings.DEFAULT_FROM_EMAIL


def _format_in_tz(dt, tz_name):
    """Format a tz-aware datetime in the visitor's IANA tz for display."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
        local = dt.astimezone(tz)
        return local.strftime('%A, %d %B %Y · %H:%M %Z')
    except Exception:
        return dt.strftime('%A, %d %B %Y · %H:%M')


def _safe_send(subject, body_text, body_html, recipients, fail_silently=True):
    """Send a multi-alternative email, swallowing backend errors."""
    if not recipients:
        return
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=_from_email(),
        to=recipients,
    )
    if body_html:
        msg.attach_alternative(body_html, 'text/html')
    try:
        msg.send(fail_silently=fail_silently)
    except Exception as e:
        logger.warning('Booking email send failed (subject=%r): %s', subject, e)


# ---------------------------------------------------------------------------
# 1. Visitor confirmation
# ---------------------------------------------------------------------------

def send_confirmation_to_visitor(appointment, request=None):
    """Email the visitor that their call is booked, with cancel link."""
    subject = f"Your call with Mostakim Jihad is confirmed — {_format_in_tz(appointment.start_datetime, appointment.timezone)}"
    visitor_when = _format_in_tz(appointment.start_datetime, appointment.timezone)
    owner_when = _format_in_tz(appointment.start_datetime, settings.TIME_ZONE if hasattr(settings, 'TIME_ZONE') else 'Asia/Dhaka')
    cancel_url = ''
    if request is not None:
        cancel_url = request.build_absolute_uri(
            reverse('booking_cancel', args=[appointment.cancel_token])
        )

    context = {
        'appointment': appointment,
        'visitor_when': visitor_when,
        'owner_when': owner_when,
        'cancel_url': cancel_url,
        'duration_minutes': appointment.duration_minutes,
        'owner_email': _owner_email(),
    }

    text = (
        f"Hi {appointment.name},\n\n"
        f"Your call with Mostakim Jihad is confirmed.\n\n"
        f"  When (your time): {visitor_when}\n"
        f"  When (owner time): {owner_when}\n"
        f"  Duration: {appointment.duration_minutes} minutes\n\n"
    )
    if appointment.notes:
        text += f"  Your notes:\n  {appointment.notes}\n\n"
    if cancel_url:
        text += f"Need to reschedule or cancel? Use this link:\n  {cancel_url}\n\n"
    text += (
        "You'll receive a meeting link separately (or by email before the call).\n\n"
        "Looking forward to it,\nMostakim Jihad"
    )

    html = _render_html('core/email/booking_confirmed.html', context, fallback=text)
    _safe_send(subject, text, html, [appointment.email])


# ---------------------------------------------------------------------------
# 2. Owner notification
# ---------------------------------------------------------------------------

def send_notification_to_owner(appointment):
    subject = f"New booking — {appointment.name} on {_format_in_tz(appointment.start_datetime, settings.TIME_ZONE)}"
    owner_when = _format_in_tz(appointment.start_datetime, settings.TIME_ZONE if hasattr(settings, 'TIME_ZONE') else 'Asia/Dhaka')
    visitor_when = _format_in_tz(appointment.start_datetime, appointment.timezone)
    context = {
        'appointment': appointment,
        'owner_when': owner_when,
        'visitor_when': visitor_when,
    }
    text = (
        f"New appointment booked.\n\n"
        f"  When (your time): {owner_when}\n"
        f"  When (visitor):   {visitor_when} ({appointment.timezone})\n"
        f"  Duration: {appointment.duration_minutes} minutes\n\n"
        f"  Name:     {appointment.name}\n"
        f"  Email:    {appointment.email}\n"
        f"  Phone:    {appointment.phone or '—'}\n"
        f"  Company:  {appointment.company or '—'}\n"
        f"  Notes:    {appointment.notes or '—'}\n\n"
        f"Manage it in Django admin: /admin/core/appointment/{appointment.id}/\n"
    )
    html = _render_html('core/email/booking_owner_notification.html', context, fallback=text)
    _safe_send(subject, text, html, [_owner_email()])


# ---------------------------------------------------------------------------
# 3. Cancellation notice (sent to both parties)
# ---------------------------------------------------------------------------

def send_cancellation_notice(appointment):
    when = _format_in_tz(appointment.start_datetime, appointment.timezone)
    subject_visitor = f"Your call on {when} has been cancelled"
    text = (
        f"Hi {appointment.name},\n\n"
        f"Your call on {when} has been cancelled.\n\n"
        f"If you'd like to reschedule, just reply to this email or book a new slot from the website.\n\n"
        f"— Mostakim Jihad"
    )
    _safe_send(subject_visitor, text, None, [appointment.email])

    if appointment.cancellation_reason:
        reason = f"\nReason given: {appointment.cancellation_reason}\n"
    else:
        reason = ""
    text_owner = (
        f"Booking cancelled.\n\n"
        f"  When:   {when}\n"
        f"  Visitor: {appointment.name} <{appointment.email}>\n"
        f"  Phone:   {appointment.phone or '—'}"
        f"{reason}"
    )
    _safe_send(f"[Cancelled] {appointment.name} — {when}", text_owner, None, [_owner_email()])


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def _render_html(template_name, context, fallback=''):
    """Render an HTML template if it exists, else return the plain-text fallback."""
    try:
        return render_to_string(template_name, context)
    except Exception as e:
        logger.debug('No HTML email template %s (%s); using plain text.', template_name, e)
        return fallback
