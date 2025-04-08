import json
import math
from enum import IntEnum

from django.core.exceptions import BadRequest
from django.db.models import Count, ExpressionWrapper
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from django.db.models.expressions import RawSQL

from mood_capture.models import MoodUpload

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


class MoodThreshold(IntEnum):
    SAD = 0
    NEUTRAL = 1
    HAPPY = 2


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def capture_mood(request):
    post_body = json.loads(request.body)
    try:
        mood = MoodUpload.Mood[post_body.get("mood").upper()]
    except (KeyError, ValueError):
        raise BadRequest('Request must have valid `mood` argument')

    try:
        lat = float(post_body.get("lat"))
        lng = float(post_body.get("lng"))
    except (KeyError, ValueError):
        raise BadRequest('Request must have valid `lat` and `lng` arguments')

    MoodUpload(user=request.user, mood=mood, lat=lat, lng=lng).save()

    return HttpResponse(status=200)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def mood_frequency_distribution(request):
    d = {MoodUpload.Mood(r["mood"]).name: r["total"] for r in
         MoodUpload.objects.filter(user=request.user).values("mood")
         .annotate(total=Count("mood")).all()}
    return JsonResponse(d)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def closest_happy_location(request):
    get_body = request.GET

    try:
        lat = float(get_body.get("lat"))
        lng = float(get_body.get("lng"))
    except (KeyError, ValueError):
        raise BadRequest('Request must have valid `lat` and `lng` arguments')

    formula = "POWER((%s - lat), 2) + POWER((%s - lng), 2)"
    distance_sqr_raw_sql = RawSQL(
        formula,
        (lat, lng)
    )

    o = MoodUpload.objects.filter(user=request.user, mood=MoodUpload.Mood.HAPPY).\
        annotate(distance=distance_sqr_raw_sql).\
        order_by("distance").values('lat', 'lng').first()

    return JsonResponse(o, safe=False)
