import base64
import json
from http import HTTPStatus
from secrets import token_bytes
from datetime import datetime, timezone

import jwt  # PyJWT
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from webauthn import verify_registration_response
from webauthn.helpers.structs import RegistrationCredential

from .models import WebAuthnDevice

RP_ID = getattr(settings, "WEBAUTHN_RP_ID", "localhost")
RP_NAME = getattr(settings, "WEBAUTHN_RP_NAME", "UDOM Authentication System")
ORIGIN = getattr(settings, "WEBAUTHN_ORIGIN", "http://localhost:4200")

# Helper to create unsigned JWT with challenge inside payload
def create_challenge_jwt(challenge_bytes: bytes) -> str:
    challenge_b64url = base64.urlsafe_b64encode(challenge_bytes).rstrip(b"=").decode("ascii")
    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "challenge": challenge_b64url,
        "iat": int(datetime.now(timezone.utc).timestamp())
    }
    token = (
        base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
        + "."
        + base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        + "."
    )
    return token

# Helper to decode challenge JWT and extract challenge bytes
def decode_challenge_jwt(token: str) -> bytes:
    try:
        # Decode without verifying signature (alg=none)
        payload = jwt.decode(token, options={"verify_signature": False})
        challenge_b64url = payload.get("challenge")
        if not challenge_b64url:
            raise ValueError("Challenge missing from JWT payload")
        # Add padding if needed
        padding = "=" * (-len(challenge_b64url) % 4)
        challenge_bytes = base64.urlsafe_b64decode(challenge_b64url + padding)
        return challenge_bytes
    except Exception as e:
        raise ValueError(f"Invalid challenge JWT: {str(e)}")


class MfaRegisterOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        display_name = request.user.username

        # Use cryptographically strong random bytes (e.g. 32 bytes)
        challenge_bytes = token_bytes(32)
        challenge_jwt = create_challenge_jwt(challenge_bytes)

        hex_id = f"{request.user.id:x}"
        if len(hex_id) % 2 == 1:
            hex_id = f"0{hex_id}"

        response_data = {
            "publicKey": {
                "rp": {"id": RP_ID, "name": RP_NAME},
                "user": {
                    "id": hex_id,
                    "name": request.user.email,
                    "displayName": display_name,
                },
                "pubKeyCredParams": [
                    {"type": "public-key", "alg": -7},  # ES256
                    {"type": "public-key", "alg": -257} # RS256
                ],
                "attestation": "direct",
                "timeout": 60000,
                "challenge": challenge_jwt,  # Send JWT as challenge string
            }
        }

        return JsonResponse(response_data)

    def post(self, request, *args, **kwargs):
        # Get challenge JWT from client payload
        challenge_jwt = request.data.get("challengeJWT")
        if not challenge_jwt:
            return Response({"error": "Missing challenge JWT"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expected_challenge_bytes = decode_challenge_jwt(challenge_jwt)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        name = data.get("name")

        pub_key_credential_raw = data.get("pubKeyCredential")
        if isinstance(pub_key_credential_raw, dict):
            pub_key_credential = json.dumps(pub_key_credential_raw)
        else:
            pub_key_credential = pub_key_credential_raw

        try:
            verification = verify_registration_response(
                credential=RegistrationCredential.parse_raw(pub_key_credential),
                expected_challenge=expected_challenge_bytes,
                expected_origin=ORIGIN,
                expected_rp_id=RP_ID,
                require_user_verification=False,
            )

            if WebAuthnDevice.objects.filter(user=request.user, credential_id=verification.credential_id).exists():
                return Response({"error": "Device already registered."}, status=status.HTTP_409_CONFLICT)
            print(request.data)
            WebAuthnDevice.objects.create(
                user=request.user,
                name=name,
                credential_id=verification.credential_id,
                public_key=verification.credential_public_key,
                attestation_format=verification.fmt,
                credential_type=verification.credential_type,
                sign_count=verification.sign_count,
                aaguid=verification.aaguid
            )

            return Response(status=HTTPStatus.CREATED)
        except Exception as e:
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class MfaAuthenticateOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        challenge_bytes = token_bytes(32)
        challenge_jwt = create_challenge_jwt(challenge_bytes)

        credential_ids = WebAuthnDevice.objects.filter(user=request.user).values_list("credential_id", flat=True)
        allow_credentials = [
            {
                "id": cred_id.hex(),
                "type": "public-key",
                "transports": ["usb", "ble", "nfc", "internal"],
            }
            for cred_id in credential_ids
        ]

        return Response(
            {
                "publicKey": {
                    "challenge": challenge_jwt,
                    "allowCredentials": allow_credentials,
                    "timeout": 60000,
                    "rpId": RP_ID,
                    "userVerification": "preferred",
                }
            }
        )


class MfaAuthenticateCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        challenge_jwt = request.data.get("challengeJWT")
        if not challenge_jwt:
            return Response({"error": "Missing challenge JWT"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expected_challenge_bytes = decode_challenge_jwt(challenge_jwt)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            credential = AuthenticationCredential.parse_obj(request.data)
            device = WebAuthnDevice.objects.get(user=request.user, credential_id=credential.raw_id)

            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=expected_challenge_bytes,
                expected_rp_id=RP_ID,
                expected_origin=ORIGIN,
                credential_public_key=device.public_key,
                credential_current_sign_count=device.sign_count,
                require_user_verification=False,
            )

            device.sign_count = verification.new_sign_count
            device.save()
            request.session["mfa_authenticated"] = True
            return Response(status=status.HTTP_200_OK)

        except WebAuthnDevice.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Authentication failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
