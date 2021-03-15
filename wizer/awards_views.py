from typing import List, Dict

from django.shortcuts import render

from wizer import models
from wizer import configuration
from wizer.views import WKZView


class AwardsViews(WKZView):
    template_name = "awards.html"

    def get(self, request):
        self.context["page"] = "awards"
        top_fastest_awards = get_top_awards_for_all_sports(top_score=configuration.rank_limit, kinds=["fastest"])
        self.context["top_fastest_awards"] = top_fastest_awards
        top_climb_awards = get_top_awards_for_all_sports(top_score=configuration.rank_limit, kinds=["climb"])
        self.context["top_climb_awards"] = top_climb_awards
        return render(request, template_name=self.template_name, context=self.context)


def _get_best_sections_of_sport_and_distance(
    sport: models.Sport, distance: int, top_score: int, kinds: List[str]
) -> List[models.BestSection]:
    awards_per_distance = list(
        models.BestSection.objects.filter(
            activity__sport=sport,
            activity__evaluates_for_awards=True,
            section_distance=distance,
            section_type__in=kinds,
        ).order_by("-max_value")[:top_score]
    )
    return awards_per_distance


def get_top_awards_for_one_sport(sport: models.Sport, top_score: int, kinds: List[str]) -> List[models.BestSection]:
    awards = []
    for bs in configuration.best_sections:
        if bs["kind"] in kinds:
            for distance in bs["distances"]:
                awards_per_distance = _get_best_sections_of_sport_and_distance(
                    sport, distance, top_score, configuration.available_best_sections
                )
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
