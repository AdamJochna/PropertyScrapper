import random
from datetime import timedelta

import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from main_app.models import ExecutedTask, ScrappedOffer, PlannedTask, User
from main_app.plots import *
from main_app.serializers import ExecutedTaskSerializer, ScrappedOfferSerializer, PlannedTaskSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


def authenticate_user(username, password):
    users = User.objects.filter(username=username).filter(password=password).filter(verified='True')
    if len(users) == 1:
        return users[0]
    else:
        return None


class UserViewSet(APIView):
    def post(self, request):
        print('UserViewSet request: {}'.format(request.data))
        user = authenticate_user(request.data['username'], request.data['password'])

        if request.data['requestType'] == 'loginUser':
            if user is not None:
                return Response({"log": "success"})
            else:
                return Response({"log": "error"})

        elif request.data['requestType'] == 'registerUser':
            data = {
                'username': request.data['username'],
                'password': request.data['password'],
                'email': request.data['requestData']['email'],
                'verified': 'False',
                'verificationCode': str(random.randint(100000, 999999)),
            }

            send_mail('Verification code',
                      'Your verification code: {}'.format(data['verificationCode']),
                      settings.EMAIL_HOST_USER,
                      [data['email']])

            serializer = UserSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response({"log": "success"})

        elif request.data['requestType'] == 'verifyEmail':
            users = User.objects.filter(username=request.data['username']).filter(password=request.data['password'])
            if len(users) == 1:
                user = users[0]

                if user.verificationCode == request.data['requestData']['verificationCode']:
                    user.verified = 'True'
                    user.save()
                    return Response({"log": "success"})
                else:
                    return Response({"log": "error"})
            else:
                return Response({"log": "error"})


class PlannedTaskViewSet(APIView):
    def post(self, request):
        print('PlannedTaskViewSet request: {}'.format(request.data))
        user = authenticate_user(request.data['username'], request.data['password'])

        if user is not None:
            if request.data['requestType'] == 'updateTaskAfterRun':
                if user.username == 'admin':
                    task = PlannedTask.objects.get(pk=request.data['requestData']['id'])
                    task.status = 'waiting'

                    if task.recurring == 'Only one run':
                        task.delete()
                    else:
                        deltas = {
                            "Every 1 minute": timedelta(minutes=1),
                            "Every 3 minutes": timedelta(minutes=3),
                            "Every day": timedelta(days=1),
                            "Every 3 days": timedelta(days=3),
                            "Every week": timedelta(days=7),
                            "Every month": timedelta(days=30)
                        }

                        while task.nextRun <= timezone.localtime(timezone.now()):
                            task.nextRun += deltas[task.recurring]

                        task.save()

                    return Response({"log": "success"})
                else:
                    return Response({"log": "error"})

            elif request.data['requestType'] == 'getReadyTasks':
                if user.username == 'admin':
                    tasks_ready = PlannedTask.objects.filter(nextRun__lt=timezone.localtime(timezone.now()))
                    tasks_ready.update(status='readyToRun')
                    tasks_ready = PlannedTask.objects.filter(status='readyToRun')
                    serializer = PlannedTaskSerializer(tasks_ready, many=True)
                    return Response(serializer.data)
                else:
                    return Response({"log": "error"})

            elif request.data['requestType'] == 'setNewTask':
                data = request.data['requestData']
                data['owner_id'] = user.id
                serializer = PlannedTaskSerializer(data=data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                return Response({"log": "success"})

            elif request.data['requestType'] == 'deleteTask':
                task = PlannedTask.objects.get(pk=request.data['requestData']['id'])
                if task.owner_id == user.id:
                    task.delete()
                    return Response({"log": "success"})
                else:
                    return Response({"log": "error"})

            elif request.data['requestType'] == 'getPlannedTasks':
                tasks = PlannedTask.objects.filter(owner_id=user.id)
                serializer = PlannedTaskSerializer(tasks, many=True)
                return Response(serializer.data)
        else:
            return Response({"log": "error"})


class ScrappedOfferViewSet(APIView):
    def post(self, request):
        print('ScrappedOfferViewSet request: {}'.format(request.data))
        user = authenticate_user(request.data['username'], request.data['password'])

        if user is not None:
            if user.username == 'admin':
                if request.data['requestType'] == 'setNewScrappedOffer':
                    serializer = ScrappedOfferSerializer(data=request.data['requestData'])

                    serializer.is_valid(raise_exception=False)
                    print(serializer.errors)

                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

                    return Response({"log": "success"})
            else:
                return Response({"log": "error"})
        else:
            return Response({"log": "error"})


class ExecutedTaskViewSet(APIView):
    def post(self, request):
        print('ExecutedTaskViewSet request: {}'.format(request.data))
        user = authenticate_user(request.data['username'], request.data['password'])

        if user is not None:
            if request.data['requestType'] == 'updateExecutedTask':
                tasks = ExecutedTask.objects.filter(id=request.data['requestData']['id'])
                tasks.delete()

                serializer = ExecutedTaskSerializer(data=request.data['requestData'])

                serializer.is_valid()
                print(serializer.errors)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response({"log": "success"})
                else:
                    return Response({"log": "error"})

            elif request.data['requestType'] == 'getExecutedTasks':
                print(ExecutedTask.objects.all())
                executed_tasks = ExecutedTask.objects.filter(owner_id=user.id)
                serializer = ExecutedTaskSerializer(executed_tasks, many=True)
                return Response(serializer.data)
        else:
            return Response({"log": "error"})


class ChartViewSet(APIView):
    def post(self, request):
        print('ChartViewSet request: {}'.format(request.data))
        user = authenticate_user(request.data['username'], request.data['password'])

        if user is not None:
            if request.data['requestType'] == 'getCharts':
                ids = request.data['requestData']['executedTasks'].split(',')
                ids = [idx for idx in ids if len(ExecutedTask.objects.filter(id=idx)) == 1]
                id_datetime = {}
                id_df = {}
                loc = request.data['requestData']['localization']

                for idx in ids:
                    id_datetime[idx] = ExecutedTask.objects.filter(id=idx)[0].runStart
                    id_df[idx] = ScrappedOffer.objects.filter(task_run_id=idx).filter(
                        address__icontains='|' + loc + '|')
                    id_df[idx] = pd.DataFrame(list(id_df[idx].values()))

                ids = sorted(ids, key=lambda x: id_datetime[x].timestamp())
                dts = [id_datetime[idx] for idx in ids]
                last_date = dts[-1].strftime("%d.%m.%Y")
                charts = {}

                plots = [
                    ('Scatterplot of offers for date: {}'.format(last_date), plot_4),
                    ('Distributions of prices for date: {}'.format(last_date), plot_3),
                    ('Prices of flats over time', plot_0),
                    ('Distributions of prices over time', plot_5),
                    ('Flats building types', plot_2),
                    ('New vs used flats', plot_1),
                ]

                if len(ids) == 1:
                    plots = plots[:2]

                for plot in plots:
                    try:
                        tmp_plot = plot[1](ids, dts, id_df)
                        charts[plot[0]] = tmp_plot
                    except:
                        pass

                plt.close("all")
                return Response(charts)

        else:
            return Response({"log": "error"})
