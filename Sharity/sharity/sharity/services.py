from functools import partial
import math


class SharityOfferRecommender:
    """Context-Aware recommendations for offers."""

    @staticmethod
    def recommend(offers, user):
        SharityOfferRecommender.__order_by_coordinates(offers, user)
        pass

    @staticmethod
    def __order_by_coordinates(offers, user):
        def distance(offer, user_coordinates):
            return math.hypot(
                offer.coordinates['lat'] - user_coordinates['lat'],
                offer.coordinates['lon'] - user_coordinates['lon']
            )

        return offers.sort(key=partial(distance, user.coordinates))

    @staticmethod
    def __calculate_tag_similarity_score(offers, user):
        for offer in offers:
            for user_interest in user.userInterests:
                pass

