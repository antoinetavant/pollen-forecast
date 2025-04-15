from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CityforecastConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cityforecast'

    def ready(self):
        from django_q.tasks import schedule, Schedule
        from django.dispatch import receiver

        @receiver(post_migrate)
        def schedule_task(sender, **kwargs):
            # Ensure this runs only for the 'cityforecast' app
            if sender.name == "cityforecast":
                # Schedule the task if it doesn't already exist
                if not Schedule.objects.filter(
                    name="Load Pollen Data for Prefectures"
                ).exists():
                    schedule(
                        "cityforecast.tasks.load_pollen_data_for_prefectures",
                        schedule_type="D",
                        name="Load Pollen Data for Prefectures",
                        repeats=-1,
                    )