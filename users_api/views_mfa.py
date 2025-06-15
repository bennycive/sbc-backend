from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import base64
import os
import json
import hashlib
import cbor2

User = get_user_model()

RP_ID = 'localhost'  # Replace with your domain in production
ORIGIN = 'http://localhost:4200'  # Adjust this to match your frontend origin


def base64url_to_bytes(data):
    padding = '=' * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ''
    return base64.urlsafe_b64decode(data + padding)


def bytes_to_base64url(data):
    return base64.b64encode(data).decode('utf-8')


# class MfaRegisterOptionsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         challenge = os.urandom(32)
#         request.session['challenge'] = bytes_to_base64url(challenge)

#         user_id = str(user.id).encode('utf-8')
#         user_name = user.username
#         display_name = getattr(user, 'get_full_name', None)
#         if callable(display_name):
#             display_name = display_name()
#         if not display_name:
#             display_name = user.username

#         registration_options = {
#             "challenge": bytes_to_base64url(challenge),
#             "rp": {
#                 "name": "Your RP Name",
#                 "id": RP_ID
#             },
#             "user": {
#                 "id": bytes_to_base64url(user_id),
#                 "name": user_name,
#                 "displayName": display_name
#             },
#             "pubKeyCredParams": [
#                 {"type": "public-key", "alg": -7},   # ES256
#                 {"type": "public-key", "alg": -257}  # RS256
#             ],
#             "authenticatorSelection": {
#                 "userVerification": "preferred"
#             },
#             "timeout": 60000,
#             "attestation": "none"
#         }
        
#         return Response(registration_options)

class MfaRegisterOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        challenge = os.urandom(32)
        request.session['challenge'] = bytes_to_base64url(challenge)

        user_id = str(user.id).encode('utf-8')
        user_name = user.username
        display_name = getattr(user, 'get_full_name', None)
        if callable(display_name):
            display_name = display_name()
        if not display_name:
            display_name = user.username

        registration_options = {
            "challenge": bytes_to_base64url(challenge),
            "rp": {
                "name": "UDOM",
                "id": RP_ID  # Make sure RP_ID is defined in your settings
            },
            "user": {
                "id": bytes_to_base64url(user_id),
                "name": user_name,
                "displayName": display_name
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},   # ES256
                {"type": "public-key", "alg": -257}  # RS256
            ],
            # --- UPDATED SECTION ---
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "requireResidentKey": True
            },
            # --- END OF UPDATE ---
            "timeout": 60000,
            "attestation": "none"
        }
        
        return Response(registration_options)

# @method_decorator(csrf_exempt, name='dispatch')
# class MfaRegisterCompleteView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         challenge_b64 = request.session.get('challenge')
#         if not challenge_b64:
#             return Response({'error': 'Challenge not found in session'}, status=status.HTTP_400_BAD_REQUEST)
#         expected_challenge = base64url_to_bytes(challenge_b64)
#         registration_response = request.data

#         try:
#             client_data_json = base64url_to_bytes(registration_response.get('clientDataJSON'))
#             attestation_object = base64url_to_bytes(registration_response.get('attestationObject'))

#             client_data = json.loads(client_data_json.decode('utf-8'))
#             if client_data['type'] != 'webauthn.create':
#                 return Response({'error': 'Invalid clientData type'}, status=status.HTTP_400_BAD_REQUEST)
#             if client_data['challenge'] != bytes_to_base64url(expected_challenge):
#                 return Response({'error': 'Challenge mismatch'}, status=status.HTTP_400_BAD_REQUEST)
#             if client_data['origin'] != ORIGIN:
#                 return Response({'error': 'Origin mismatch'}, status=status.HTTP_400_BAD_REQUEST)

#             attestation = cbor2.loads(attestation_object)
#             auth_data = attestation.get('authData')
#             if not auth_data:
#                 return Response({'error': 'No authData in attestation'}, status=status.HTTP_400_BAD_REQUEST)

#             rp_id_hash = auth_data[0:32]
#             flags = auth_data[32]
#             sign_count = int.from_bytes(auth_data[33:37], 'big')

#             expected_rp_id_hash = hashlib.sha256(RP_ID.encode('utf-8')).digest()
#             if rp_id_hash != expected_rp_id_hash:
#                 return Response({'error': 'RP ID hash mismatch'}, status=status.HTTP_400_BAD_REQUEST)

#             credential_data = auth_data[37:]
#             aaguid = credential_data[0:16]
#             cred_id_len = int.from_bytes(credential_data[16:18], 'big')
#             cred_id = credential_data[18:18+cred_id_len]
#             credential_public_key = credential_data[18+cred_id_len:]

#             user.profile.webauthn_credential_id = bytes_to_base64url(cred_id)
#             user.profile.webauthn_public_key = bytes_to_base64url(credential_public_key)
#             user.profile.save()

#             return Response({"status": "ok"})

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MfaRegisterCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Temporarily fakes the verification process and always returns success.
        This is for frontend debugging and must be replaced with real logic.
        """
        # It's still useful to see what the frontend is sending
        print("--- MFA REGISTRATION COMPLETE (FAKE) ---")
        print("Received payload:", request.data)
        print("-----------------------------------------")

        # Always return a success response
        return Response(
            {"status": "success", "detail": "MFA registration faked successfully."},
            status=status.HTTP_200_OK
        )




class MfaAuthenticateOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.profile.webauthn_credential_id:
            return Response({'error': 'No registered credential'}, status=status.HTTP_400_BAD_REQUEST)

        challenge = os.urandom(32)
        request.session['challenge'] = bytes_to_base64url(challenge)

        allow_credentials = [{
            'type': 'public-key',
            'id': user.profile.webauthn_credential_id,
            'transports': ['usb', 'nfc', 'ble', 'internal']
        }]

        authentication_options = {
            'challenge': bytes_to_base64url(challenge),
            'rpId': RP_ID,
            'allowCredentials': allow_credentials,
            'userVerification': 'preferred',
            'timeout': 60000,
        }

        return Response(authentication_options)


@method_decorator(csrf_exempt, name='dispatch')
class MfaAuthenticateCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        challenge_b64 = request.session.get('challenge')
        if not challenge_b64:
            return Response({'error': 'Challenge not found in session'}, status=status.HTTP_400_BAD_REQUEST)
        expected_challenge = base64url_to_bytes(challenge_b64)
        authentication_response = request.data

        try:
            client_data_json = base64url_to_bytes(authentication_response.get('clientDataJSON'))
            authenticator_data = base64url_to_bytes(authentication_response.get('authenticatorData'))
            signature = base64url_to_bytes(authentication_response.get('signature'))
            user_handle = base64url_to_bytes(authentication_response.get('userHandle'))

            client_data = json.loads(client_data_json.decode('utf-8'))
            if client_data['type'] != 'webauthn.get':
                return Response({'error': 'Invalid clientData type'}, status=status.HTTP_400_BAD_REQUEST)
            if client_data['challenge'] != bytes_to_base64url(expected_challenge):
                return Response({'error': 'Challenge mismatch'}, status=status.HTTP_400_BAD_REQUEST)
            if client_data['origin'] != ORIGIN:
                return Response({'error': 'Origin mismatch'}, status=status.HTTP_400_BAD_REQUEST)

            # NOTE: Cryptographic signature verification is required here using user.profile.webauthn_public_key
            # This is where you would verify `signature` against the `authenticatorData` + `clientDataHash`
            # using the public key stored in the user profile.

            # Assume verification is successful
            return Response({"status": "ok"})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
