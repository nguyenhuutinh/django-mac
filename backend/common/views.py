from django.views import generic
from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils.timezone import now



from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

from common.upload_task import create_task


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny



class IndexView(generic.TemplateView):
    template_name = 'common/index.html'


class RestViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='rest-check',
    )
    @csrf_exempt
    def rest_check(self, request):
        print("ooo")
        return Response(
            {"result": "If you're seeing this, the REST API is working!"},
            status=status.HTTP_200_OK,
        )
    # def home(request):
    #     return render(request, "home.html")

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='run-task',
    )
    @csrf_exempt
    def run_task(self, request):
        # print(request.POST)

        task_type = 100
        task = create_task.delay(int(task_type))
        print("upload done")
        print(task.result)

        task_result = AsyncResult(task.id)
        print(task_result.result)
        downloadLink = 'https://drive.google.com/uc?id={}&export=download'.format(task_result.result)
        # task_id = task.info["id"]
        print("downloadLink")
        print(downloadLink)
        return JsonResponse({"result": downloadLink }, status=202)



    # @csrf_exempt
    # def get_status(request, task_id):
    #     task_result = AsyncResult(task_id)
    #     result = {
    #         "task_id": task_id,
    #         "task_status": task_result.status,
    #         "task_result": task_result..
    #     }
    #     return JsonResponse(result, status=200)



