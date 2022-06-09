from functools import partial
from django.contrib.auth.models import User
import math
import json
import operator


class SharityOfferRecommender:
    """Context-Aware recommendations for offers."""

    @staticmethod
    def recommend(offers, user, limit=None):
        if len(offers) > 0:
            offers_ordered_by_distance = SharityOfferRecommender.__order_by_coordinates(offers, user)
            relevance_score_dataset = SharityOfferRecommender.__calculate_relevance_scores(
                offers_ordered_by_distance,
                user
            )

            return SharityOfferRecommender.__order_offers_by_relevance_scores(relevance_score_dataset, offers, limit)

        return list(offers)

    @staticmethod
    def __order_by_coordinates(offers, user: User):
        def distance(user_coordinates, offer):
            return math.hypot(
                offer.get_latitude() - user_coordinates['lat'],
                offer.get_longitude() - user_coordinates['lon'],
            )

        offers_list = list(offers)

        offers_list.sort(
            key=partial(
                distance,
                {
                    'lat': user.profile.get_latitude(),
                    'lon': user.profile.get_longitude()
                }
            )
        )

        return offers_list

    @staticmethod
    def __calculate_relevance_scores(offers_ordered_by_distance_dataset, user: User):
        scores = {}
        location_score = 1
        unit_location_score = location_score / len(offers_ordered_by_distance_dataset)
        member_claims_list = json.loads(user.profile.claims)

        # if len(member_claims_list) > 0:
        for key, offer in enumerate(offers_ordered_by_distance_dataset):
            offer_claims_list = json.loads(offer.claims)

            # if len(offer_claims_list) > 0:
            if len(member_claims_list) != 0 and len(member_claims_list) > len(offer_claims_list):
                member_and_offer_relevance_rate = len(offer_claims_list) / len(member_claims_list)
            elif len(offer_claims_list) != 0 and len(offer_claims_list) > len(member_claims_list):
                member_and_offer_relevance_rate = len(member_claims_list) / len(offer_claims_list)
            else:
                member_and_offer_relevance_rate = 0

            unit_member_relevance_score = float(100 / len(member_claims_list)) if len(member_claims_list) > 0 else 0
            unit_relevance_score = unit_member_relevance_score * member_and_offer_relevance_rate
            scores[str(offer.uuid)] = location_score - (key * unit_location_score)
            for user_claim in json.loads(user.profile.claims):
                if user_claim in offer_claims_list:
                    scores[str(offer.uuid)] += unit_relevance_score

        return dict(
            sorted(
                scores.items(),
                key=operator.itemgetter(1),
                reverse=True
            )
        )

    @staticmethod
    def __order_offers_by_relevance_scores(relevance_score_dataset: dict, offers, limit: int):
        offers_ordered_by_relevance_scores_dataset = []

        for relevance_score_key in relevance_score_dataset.keys():
            offers_ordered_by_relevance_scores_dataset.append(
                next(filter(lambda offer: str(offer.uuid) == relevance_score_key, offers), None)
            )

        return offers_ordered_by_relevance_scores_dataset[0:limit]
