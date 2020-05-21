from django.db import models


class ExecutedTask(models.Model):
    owner_id = models.IntegerField()
    id = models.CharField(max_length=100, primary_key=True)
    parent_planned_task_id = models.IntegerField()
    runStart = models.DateTimeField()
    status = models.CharField(max_length=100)


class PlannedTask(models.Model):
    owner_id = models.IntegerField()
    taskName = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    offersType = models.CharField(max_length=100)
    regions = models.CharField(max_length=1000, blank=True)
    localizations = models.CharField(max_length=1000, blank=True)
    firstRun = models.DateTimeField()
    recurring = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    nextRun = models.DateTimeField()


class ScrappedOffer(models.Model):
    owner_id = models.IntegerField()
    task_run_id = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    price = models.IntegerField()
    address = models.CharField(max_length=100)
    level = models.IntegerField(null=True)
    size = models.CharField(max_length=100)
    rooms = models.IntegerField()
    market = models.CharField(max_length=100)
    building_type = models.CharField(max_length=100, null=True)
    price_per_msq = models.IntegerField()


class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    verified = models.BooleanField()
    verificationCode = models.CharField(max_length=100)
