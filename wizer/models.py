import os
import logging
import datetime

from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from colorfield.fields import ColorField
from workoutizer import settings as django_settings

log = logging.getLogger(__name__)


class Sport(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=24, unique=True, verbose_name="Sport Name:")
    icon = models.CharField(max_length=24, verbose_name="Icon:")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color = ColorField(default="#42FF71", verbose_name="Color:")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sport, self).save(*args, **kwargs)


class Traces(models.Model):
    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    calories = models.IntegerField(null=True, blank=True)
    # coordinates
    latitude_list = models.CharField(max_length=10000000000, default="[]")
    longitude_list = models.CharField(max_length=10000000000, default="[]")
    # distance
    distance_list = models.CharField(max_length=10000000000, default="[]")
    # elevation
    altitude_list = models.CharField(max_length=10000000000, default="[]")
    max_altitude = models.FloatField(blank=True, null=True)
    min_altitude = models.FloatField(blank=True, null=True)
    # heart rate
    heart_rate_list = models.CharField(max_length=10000000000, default="[]")
    avg_heart_rate = models.IntegerField(null=True, blank=True)
    max_heart_rate = models.IntegerField(null=True, blank=True)
    min_heart_rate = models.IntegerField(null=True, blank=True)
    # cadence
    cadence_list = models.CharField(max_length=10000000000, default="[]")
    avg_cadence = models.IntegerField(null=True, blank=True)
    max_cadence = models.IntegerField(null=True, blank=True)
    min_cadence = models.IntegerField(null=True, blank=True)
    # speed
    speed_list = models.CharField(max_length=10000000000, default="[]")
    avg_speed = models.FloatField(null=True, blank=True)
    max_speed = models.FloatField(null=True, blank=True)
    min_speed = models.FloatField(null=True, blank=True)
    # temperature
    temperature_list = models.CharField(max_length=10000000000, default="[]")
    avg_temperature = models.FloatField(null=True, blank=True)
    max_temperature = models.FloatField(null=True, blank=True)
    min_temperature = models.FloatField(null=True, blank=True)
    # training effect
    aerobic_training_effect = models.FloatField(blank=True, null=True)
    anaerobic_training_effect = models.FloatField(blank=True, null=True)
    # timestamps
    timestamps_list = models.CharField(max_length=10000000000, default="[]")
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.file_name = self.path_to_file.split("/")[-1]
        log.debug(f"creating file name from path {self.path_to_file} -> {self.file_name}")
        super(Traces, self).save()


def default_sport(return_pk: bool = True):
    sport = Sport.objects.filter(slug="unknown").first()
    if not sport:
        sport = Sport(name="unknown", color="gray", icon="question-circle", slug="unknown")
        sport.save()
    if return_pk:
        return sport.pk
    else:
        return sport


class Activity(models.Model):
    def __str__(self):
        return f"{self.name} ({self.sport})"

    name = models.CharField(max_length=200, verbose_name="Activity Name:", default="unknown")
    sport = models.ForeignKey(Sport, on_delete=models.SET_DEFAULT, default=default_sport, verbose_name="Sport:")
    date = models.DateTimeField(blank=False, default=timezone.now, verbose_name="Date:")
    duration = models.DurationField(verbose_name="Duration:", default=datetime.timedelta(minutes=30))
    distance = models.FloatField(blank=True, null=True, verbose_name="Distance:", default=0)
    description = models.CharField(max_length=600, blank=True, null=True, verbose_name="Description:")
    trace_file = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=True, null=True)
    is_demo_activity = models.BooleanField(verbose_name="Is this a Demo Activity:", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.trace_file:
            self.trace_file.delete()
            log.debug(f"deleted trace object {self.trace_file}")
            if os.path.isfile(self.trace_file.path_to_file):
                os.remove(self.trace_file.path_to_file)
                log.debug(f"deleted trace file also: {self.name}")
        super(Activity, self).delete(*args, **kwargs)
        log.debug(f"deleted activity: {self.name}")


class Lap(models.Model):
    start_time = models.DateTimeField(blank=False)
    end_time = models.DateTimeField(blank=False)
    elapsed_time = models.DurationField(blank=False)
    trigger = models.CharField(max_length=120, blank=False)
    start_lat = models.FloatField(blank=True, null=True)
    start_long = models.FloatField(blank=True, null=True)
    end_lat = models.FloatField(blank=True, null=True)
    end_long = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    trace = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=False)
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label:")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class BestSection(models.Model):
    """
    Contains all best sections of all activities. Best sections could be e.g. the fastest 5km of an activity. This model
    stores the start and end of each section, which is used to render the sections in the activity view.
    """

    def __str__(self):
        return f"{self.section_type} {self.section_distance}km: {self.max_value}m/s"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=False)
    section_type = models.CharField(max_length=120, blank=False)
    section_distance = models.IntegerField(blank=False)
    start_index = models.IntegerField(blank=False)
    end_index = models.IntegerField(blank=False)
    max_value = models.FloatField(blank=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(BestSection, self).save()
        self.check_if_section_suits_for_top_score_and_update()

    def save_section_as_new_top_score(self, rank: int):
        new_top_score = BestSectionTopScores(
            activity=self.activity,
            sport=self.activity.sport,
            section=self,
            rank=rank,
        )
        new_top_score.save()

    def check_if_section_suits_for_top_score_and_update(self):
        relevant_top_scores = BestSectionTopScores.objects.filter(
            sport=self.activity.sport,
            section__section_type=self.section_type,
            section__section_distance=self.section_distance,
        ).order_by("rank")
        found_rank = 0
        looking_at_rank = 0
        for top_score_section in relevant_top_scores:
            looking_at_rank = top_score_section.rank
            if self.max_value > top_score_section.section.max_value:
                # self section should be stored at current rank
                if not found_rank:
                    found_rank = looking_at_rank
            if found_rank:
                # shift current top score section back by one rank
                top_score_section.rank += 1
                top_score_section.save()
        # if no suitable rank was found among the available top score sections, use the looking_at_rank + 1
        if not found_rank:
            found_rank = looking_at_rank + 1

        # only save top score in case found_rank <= 3
        if found_rank <= 3 and not in_top_scores_already(self, relevant_top_scores):
            log.debug(
                f"Activity scored rank {found_rank} for {self.section_type} {self.activity.sport.name} "
                f"{self.section_distance}km!"
            )
            self.save_section_as_new_top_score(rank=found_rank)
            self.delete_all_ranks_worse_than_third_rank()

    def delete_all_ranks_worse_than_third_rank(self):
        # delete all top scores, where rank > 3
        top_scores_to_be_deleted = BestSectionTopScores.objects.filter(
            sport=self.activity.sport,
            rank__gt=3,
        ).order_by("rank")
        for top_score_section in top_scores_to_be_deleted:
            log.debug(
                f"Deleting top score section of '{top_score_section.activity.name}' because a better one was found."
            )
            top_score_section.delete()


def in_top_scores_already(section: BestSection, top_score_sections) -> bool:
    for ts_section in top_score_sections:
        if (
            section.section_distance == ts_section.section.section_distance
            and section.section_type == ts_section.section.section_type
            and section.activity.pk == ts_section.section.activity.pk
        ):
            return True
        else:
            return False


class BestSectionTopScores(models.Model):
    """
    Collection of the top three best sections of each sport.
    """

    def __str__(self):
        return f"Rank: {self.rank}: {self.section}"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=False)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, blank=False)
    section = models.ForeignKey(BestSection, on_delete=models.CASCADE, blank=False)

    class Rank(models.IntegerChoices):
        FIRST = 1
        SECOND = 2
        THIRD = 3

    rank = models.IntegerField(choices=Rank.choices)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Settings(models.Model):
    days_choices = [(9999, "all"), (365, 365), (180, 180), (90, 90), (30, 30), (10, 10)]

    path_to_trace_dir = models.CharField(
        max_length=120, default=django_settings.TRACKS_DIR, verbose_name="Path to Traces Directory:"
    )
    path_to_garmin_device = models.CharField(
        max_length=120, default="/run/user/1000/gvfs/", verbose_name="Path to Garmin Device:"
    )
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    delete_files_after_import = models.BooleanField(verbose_name="Delete fit Files after Copying: ", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


def get_settings():
    return Settings.objects.get_or_create(pk=1)[0]
