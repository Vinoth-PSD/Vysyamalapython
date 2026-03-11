from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from datetime import date


class Command(BaseCommand):
    help = "Trigger expired memberships into datahistory"

    def handle(self, *args, **kwargs):

        today = date.today()

        self.stdout.write(f"Running expiry check for {today}")

        try:
            with connection.cursor() as cursor:

                # Step 1: Get expired profiles
                cursor.execute("""
                    SELECT 
                        ProfileId,
                        Owner_id,
                        Plan_id
                    FROM logindetails
                    WHERE Status = 1
                    AND DATE(membership_enddate) = %s
                """, [today])

                rows = cursor.fetchall()

                if not rows:
                    self.stdout.write("No expired profiles found.")
                    return

                for row in rows:
                    profile_id = row[0]
                    owner_id = row[1]
                    plan_id = row[2]

                    # Step 2: Insert into datahistory
                    cursor.execute("""
                        INSERT INTO datahistory (
                            profile_id,
                            owner_id,
                            date_time,
                            profile_status,
                            plan_id,
                            others
                        )
                        VALUES (%s, %s, NOW(), %s, %s, %s)
                    """, [
                        profile_id,
                        owner_id,
                        1,          # profile_status
                        plan_id,
                        "Expired"   # static others
                    ])

                self.stdout.write(f"{len(rows)} expired profiles inserted into datahistory.")

        except Exception as e:
            self.stdout.write(f"Error: {e}")