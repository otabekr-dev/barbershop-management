import asyncio

from django.core.management.base import BaseCommand
from apps.notifications.models import Notification
from apps.notifications.service import send_notification

class Command(BaseCommand):
    help = 'Send Pending Telegram notifications'

    def handle(self, *args, **options):
        asyncio.run(self.process_notifications())

    async def process_notifications(self):
        notifications = await self.get_pending_notifications()

        if not notifications:
            self.stdout.write('Pending notifications not found')

        for notification in notifications:
            result = await send_notification(notification=notification)

            if result:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notification {notification.id} sent successfully.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Notification {notification.id} failed'
                    )
                )

    async def get_pending_notifications(self):
        return [
            notification 
            async for notification in Notification.objects.filter(
                status=Notification.Status.PENDING
            ).select_related(
                'recipient',
                'booking__customer',
                'booking__service'
            )
        ]
    