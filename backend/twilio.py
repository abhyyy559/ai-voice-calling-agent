"""
Twilio integration for outbound calls and webhooks.
Replaces Plivo integration.
"""
import os
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.request_validator import RequestValidator

router = APIRouter(prefix="/twilio", tags=["twilio"])

# Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

# Request validator for webhook signature verification
validator = RequestValidator(TWILIO_AUTH_TOKEN) if TWILIO_AUTH_TOKEN else None


def validate_twilio_request(request: Request, body: str) -> bool:
    """Validate that the request came from Twilio."""
    if not validator:
        return True  # Skip validation if no token (dev mode)

    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    return validator.validate(url, body, signature)


@router.post("/webhook")
async def twilio_webhook(request: Request):
    """
    Handle incoming Twilio call webhooks.
    Returns TwiML to connect the call to LiveKit via Media Streams.
    """
    # Read body for validation
    body = await request.body()
    body_str = body.decode("utf-8")

    # Validate request (skip in dev if needed)
    if not validate_twilio_request(request, body_str):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Parse form data
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    from_number = form_data.get("From")
    to_number = form_data.get("To")

    # Log call event
    print(f"Twilio webhook: CallSid={call_sid}, Status={call_status}, From={from_number}, To={to_number}")

    # Generate TwiML response
    response = VoiceResponse()

    if call_status in ["ringing", "in-progress"]:
        # Connect to LiveKit via Media Stream
        connect = Connect()
        stream = Stream(url=f"{LIVEKIT_URL}/twilio/media-stream")
        connect.append(stream)
        response.append(connect)
    elif call_status == "completed":
        # Call ended - handle cleanup
        print(f"Call {call_sid} completed")
    elif call_status in ["busy", "no-answer", "failed", "canceled"]:
        print(f"Call {call_sid} ended with status: {call_status}")

    return Response(content=str(response), media_type="application/xml")


@router.post("/place-test-call")
async def place_test_call(to_number: str = Form(...)):
    """
    Place an outbound test call via Twilio.
    """
    if not twilio_client:
        raise HTTPException(status_code=500, detail="Twilio client not configured")

    if not TWILIO_PHONE_NUMBER:
        raise HTTPException(status_code=500, detail="TWILIO_PHONE_NUMBER not configured")

    # Webhook URL for call events
    webhook_base = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
    webhook_url = f"{webhook_base}/twilio/webhook"

    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=webhook_url,
            method="POST",
            status_callback=f"{webhook_base}/twilio/status-callback",
            status_callback_method="POST",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=True,
            recording_channels="dual",
        )

        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "from": call.from_formatted,
            "to": call.to_formatted,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place call: {str(e)}")


@router.post("/status-callback")
async def status_callback(request: Request):
    """
    Handle Twilio call status callbacks.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    call_duration = form_data.get("CallDuration")
    recording_url = form_data.get("RecordingUrl")

    print(f"Status callback: CallSid={call_sid}, Status={call_status}, Duration={call_duration}, Recording={recording_url}")

    return {"status": "received"}


def place_outbound_call(to_number: str, webhook_base: str) -> dict:
    """
    Helper function to place outbound call (for dialer worker).
    """
    if not twilio_client or not TWILIO_PHONE_NUMBER:
        return {"success": False, "error": "Twilio not configured"}

    webhook_url = f"{webhook_base}/twilio/webhook"

    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=webhook_url,
            method="POST",
            status_callback=f"{webhook_base}/twilio/status-callback",
            status_callback_method="POST",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=True,
            recording_channels="dual",
        )

        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


from fastapi import Response