from rest_framework import serializers
from main_app.models import *
from rest_framework import serializers, fields


class ExecutedTaskSerializer(serializers.HyperlinkedModelSerializer):
    runStart = fields.DateTimeField(input_formats=['%d.%m.%Y %H:%M:%S'])

    class Meta:
        model = ExecutedTask
        fields = ['owner_id', 'id', 'parent_planned_task_id', 'runStart', 'status']


class ScrappedOfferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScrappedOffer
        fields = ['owner_id', 'task_run_id', 'site', 'price', 'address', 'level', 'size',
                  'rooms', 'market', 'building_type', 'price_per_msq']


class PlannedTaskSerializer(serializers.HyperlinkedModelSerializer):
    firstRun = fields.DateTimeField(input_formats=['%d.%m.%Y %H:%M'])
    nextRun = fields.DateTimeField(input_formats=['%d.%m.%Y %H:%M'])

    class Meta:
        model = PlannedTask
        fields = ['owner_id', 'id', 'taskName', 'site', 'offersType',
                  'regions', 'localizations', 'firstRun',
                  'recurring', 'status', 'nextRun']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'verified', 'verificationCode']