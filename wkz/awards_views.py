from typing import List, Dict, Union

from django.shortcuts import render

from wkz import models
from wkz import configuration as cfg
from wkz.views import WKZView


awards_info_texts = {
    "general": (
        f"This page lists the top {cfg.rank_limit} activities in the respective category. Both individual "
        "activities and entire sports can be disabled for awards."
    ),
    "fastest": (
        "The fastest sections are determined by computing the average velocity over the given section distance."
    ),
    "climb": (
        "The best climb sections are determined by computing the accumulated evelation gain per minute over the "
        "given section distance."
    ),
    "ascent": ("The total ascent equals the aggregated sum of all uphill meters gained during one activity."),
}


class AwardsViews(WKZView):
    template_name = "awards/awards.html"

    def get(self, request):
        self.context["page_name"] = "Awards"

        # get fastest awards
        top_fastest_awards = get_top_awards_for_all_sports(top_score=cfg.rank_limit, kinds=["fastest"])
        self.context["top_fastest_awards"] = top_fastest_awards

        # get climb awards
        top_climb_awards = get_top_awards_for_all_sports(top_score=cfg.rank_limit, kinds=["climb"])
        self.context["top_climb_awards"] = top_climb_awards

        # get ascent awards
        top_ascent_awards = _get_top_ascent_awards_for_all_sports()
        self.context["top_ascent_awards"] = top_ascent_awards

        # get info text for hover over question mark
        self.context["info_text"] = awards_info_texts

        return render(request, template_name=self.template_name, context=self.context)


def _get_top_ascent_awards_for_all_sports() -> Dict[models.Sport, list]:
    top_awards = {}
    for sport in models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown").order_by("name"):
        top_awards[sport] = _get_top_ascent_awards_for_one_sport(sport)
    return top_awards


def get_ascent_ranking_of_activity(activity: models.Activity) -> Union[int, None]:
    list_of_ascent_awards = _get_top_ascent_awards_for_one_sport(activity.sport)
    if activity in list_of_ascent_awards:
        return list_of_ascent_awards.index(activity) + 1
    else:
        return None


def _get_top_ascent_awards_for_one_sport(sport: models.Sport) -> list:
    return list(
        (
            models.Activity.objects.filter(
                sport=sport,
                evaluates_for_awards=True,
            )
            .exclude(trace_file__total_ascent=None)
            .order_by("-trace_file__total_ascent")[: cfg.rank_limit]
        )
    )


def _get_best_sections_of_sport_and_distance(
    sport: models.Sport, distance: int, top_score: int, kinds: List[str]
) -> List[models.BestSection]:
    awards_per_distance = list(
        models.BestSection.objects.filter(
            activity__sport=sport,
            activity__evaluates_for_awards=True,
            distance=distance,
            kind__in=kinds,
        ).order_by("-max_value")[:top_score]
    )
    return awards_per_distance


def get_top_awards_for_one_sport(sport: models.Sport, top_score: int, kinds: List[str]) -> List[models.BestSection]:
    awards = []
    for bs in cfg.best_sections:
        if bs["kind"] in kinds:
            for distance in bs["distances"]:
                awards_per_distance = _get_best_sections_of_sport_and_distance(sport, distance, top_score, kinds)
                for rank, section in enumerate(awards_per_distance):
                    setattr(section, "rank", rank + 1)
                if awards_per_distance:
                    awards += awards_per_distance
    return awards


def get_top_awards_for_all_sports(top_score: int, kinds: List[str]) -> Dict[models.Sport, List[models.BestSection]]:
    top_awards = {}
    for sport in models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown").order_by("name"):
        awards = get_top_awards_for_one_sport(sport, top_score, kinds)
        if awards:
            top_awards[sport] = awards
    return top_awards
