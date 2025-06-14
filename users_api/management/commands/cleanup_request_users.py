from django.core.management.base import BaseCommand
from users_api.models import TranscriptCertificateRequest, ProvisionalResultRequest, CustomUser

class Command(BaseCommand):
    help = 'Cleanup TranscriptCertificateRequest and ProvisionalResultRequest user fields by assigning users based on available data'

    def handle(self, *args, **options):
        # Example logic: Assign user if possible based on some criteria
        # This is a placeholder and should be customized based on your data

        # For demonstration, we will just print requests with null user
        transcript_null_user = TranscriptCertificateRequest.objects.filter(user__isnull=True)
        provisional_null_user = ProvisionalResultRequest.objects.filter(user__isnull=True)

        self.stdout.write(f"TranscriptCertificateRequests with null user: {transcript_null_user.count()}")
        self.stdout.write(f"ProvisionalResultRequests with null user: {provisional_null_user.count()}")

        # TODO: Implement logic to assign user to requests if possible
        # For example, if you have a way to map requests to users by other fields, do it here

        # Example: If you have a field like matriculation_number in request, you can find user by that
        # For now, just output the IDs for manual review
        self.stdout.write("TranscriptCertificateRequest IDs with null user:")
        for req in transcript_null_user:
            self.stdout.write(f"  ID: {req.id}")

        self.stdout.write("ProvisionalResultRequest IDs with null user:")
        for req in provisional_null_user:
            self.stdout.write(f"  ID: {req.id}")

        self.stdout.write("Please implement custom logic to assign users to these requests based on your data.")
