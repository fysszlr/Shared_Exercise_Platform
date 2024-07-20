from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from UserInfo.models import UserInfo
from backend.models import *
from Exercise.views import *
import datetime
import json
import random

# Create your views here.

class addWrongLog(View):
    # def get(self, request):
    #     return render(request, 'add_wrong_log.html')

    def post(self, request):
        response = request_template.copy()
        data = json.loads(request.body)
        exerciseid = data['exerciseid']
        userid = 0  # 如何获取当前用户id

        if Problem.objects.filter(id=exerciseid).exists() == False:
            response['success'] = False
            response['errCode'] = 700101
            return JsonResponse(response)
        timestamp = int(datetime.datetime.now().timestamp())
        UserInfo.objects.get(id=userid).problemlog.append((timestamp, exerciseid, False))
        UserInfo.objects.get(id=userid).save()
        response['data'] = {'timestamp': timestamp}
        return JsonResponse(response)


class addRightLog(View):
    # def get(self, request):
    #     return render(request, 'add_right_log.html')

    def post(self, request):
        response = request_template.copy()
        data = json.loads(request.body)
        exerciseid = data['exerciseid']
        userid = 0  # 如何获取当前用户id

        if Problem.objects.filter(id=exerciseid).exists() == False:
            response['success'] = False
            response['errCode'] = 700201
            return JsonResponse(response)
        timestamp = int(datetime.datetime.now().timestamp())
        UserInfo.objects.get(id=userid).problemlog.append((timestamp, exerciseid, True))
        UserInfo.objects.get(id=userid).save()
        response['data'] = {'timestamp': timestamp}
        return JsonResponse(response)


class getCurrentEvaluation(View):
    def get(self, request):
        userid=0
        user=UserInfo.objects.get(id=userid)
        loginTime=[]
        for log in user.log:
            if log[1]=='login':
                loginTime.append(log[0])
        loginTime.append(datetime.datetime.now().timestamp())
        loginPos=0
        rate=0
        rightsum=0
        wrongsum=0
        data={'score':[],'time':[]}
        for problemlog in UserInfo.objects.get(id=userid).problemlog:
            if problemlog[0]>loginTime[loginPos+1]:
                if rightsum+wrongsum!=0:
                    rate=rightsum/(rightsum+wrongsum)
                data['score'].append(int(rate*100))
                data['time'].append(loginTime[loginPos])
                loginPos+=1
                if loginPos+1>=len(loginTime):
                    break
            if problemlog[2]==True:
                rightsum+=1
            else:
                wrongsum+=1

        response=request_template.copy()
        response['data']=data
        return JsonResponse(response)


class getRecommendExercise(View):
    def get(self, request):
        userid = 0
        getdata=json.loads(request.body)
        pattern=getdata['pattern']
        quantity=getdata['quantity']
        problems = list(getReachableExercise.getReachableExercise(userid))
        recommend=[]
        for i in problems:
            problem=Problem.objects.get(id=i)
            tags=problem.tags
            for tag in tags:
                if tag==pattern:
                    recommend.append(getExerciseByID.getExercise(i))
                    break
        if len(recommend)<quantity:
            data={'satisfy':False,'recommend':recommend}
        else:
            data={'satisfy':True,'recommend':random.sample(recommend,quantity)}

        response = request_template.copy()
        response['data'] = data
        return JsonResponse(response)