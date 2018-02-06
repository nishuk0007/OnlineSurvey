from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .models import ClientSurvey,SurveyDesingForm
from .serializers import (SignupSerializer, LoginSerializer, LogoutSerializer, ClientSurveySerializer,
                          AllSurveySerializer,SurveyFormSerializer,AllSurveyFormSerializer)
from django.shortcuts import get_object_or_404
import json

###################################################################################
#                    Survey Design Form API VIEW                                  #
###################################################################################
class SurveyDesign(viewsets.ViewSet):
    serializers_class=SurveyFormSerializer
    models = SurveyDesingForm
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def create(self,request):
        store_list = request.POST['jsonformate']
        print(store_list)
        design_data = json.loads(store_list)
        print(design_data[0])
        for data in design_data:
            serializer = self.serializers_class(data=data)
            if serializer.is_valid(raise_exception=True):
                survey_id=ClientSurvey.objects.get(id=data['survey'])
                SurveyDesingForm.objects.create(survey= survey_id,
                                                lebel_data= data['lebel_data'],
                                                level_x= data['level_x'], 
                                                level_y= data['level_y'],
                                                value= data['value'], 
                                                value_x= data['value_x'],
                                                value_y= data['value_y'])
        return Response({
           "status": '200',
           "success" : True,
           "message" : "Successfully Data Saved",
          } )

    def list(self,request):
        # import pdb; pdb.set_trace()
        # surveys=SurveyDesingForm.objects.filter(survey=request.GET['id'])
        surveys=SurveyDesingForm.objects.all() 
        serializer = AllSurveyFormSerializer(surveys, many=True)
        return Response(serializer.data)

    def retrieve(self,request,pk):
        queryset = SurveyDesingForm.objects.filter(survey=pk)
        serializer = AllSurveyFormSerializer(queryset,many=True)
        return Response(serializer.data)

###################################################################################
#                    Survey Form API view                                         #
###################################################################################

class SurveyForm(viewsets.ViewSet):
    serializers_class= ClientSurveySerializer
    model = ClientSurvey
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        serializer = self.serializers_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            name=request.POST['name']
            description=request.POST['description']
            user=request.user
            ClientSurvey.objects.create(name=name,description=description,user=user)
            return Response({
               "status": '200',
               "success" : True,
               "message" : "Successfully Data Saved",
              } )
  
    def retrieve(self,request,pk):
        queryset = ClientSurvey.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = AllSurveySerializer(user)
        return Response(serializer.data)

    def list(self,request):
        surveys=ClientSurvey.objects.filter(user=request.user)
        serializer = AllSurveySerializer(surveys, many=True)
        return Response(serializer.data)

    def update(self, request, pk):
        instance=ClientSurvey.objects.get(id=pk)
        serializer =AllSurveySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": '200',
                          "success" : True,
                          "message" : "Successfully Updated",
                          })

    def partial_update(self, request, pk):
        instance=ClientSurvey.objects.get(id=pk)
        serializer =ClientSurveySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": '200',
                          "success" : True,
                          "message" : "Successfully Updated",
                          })

    def destroy(self, request, pk):
        instance=ClientSurvey.objects.get(id=pk)
        instance.delete()
        return Response({"status": '200',
                          "success" : True,
                          "message" : "Successfully Deleted",
                          })

###################################################################################
#                    User login/logout syste                                      #
###################################################################################

class Signup(viewsets.ViewSet):

    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer
    model = Token  

    def create(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            username = user.username
            raw_password = user.password
            #again set password in HASH format
            user.set_password(raw_password)
            user.save()
            user = authenticate(username=username, password=raw_password)
            token, created = self.model.objects.get_or_create(user=user) 
            headers = { 'access_token': token.key }
            return Response({
                    "status": status.HTTP_201_CREATED,
                    "success" : True,
                    "message" : "Successfully Created Your Account.",
                    }, headers= headers )
        return Response(serializer.errors)


class Login(viewsets.ViewSet):

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    model = Token  
     
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token, created = self.model.objects.get_or_create(user=user)
        except Exception as e:
            pass  
        headers = { 'access_token' : token.key }
        return Response({
                    "status": status.HTTP_200_OK,
                    "message" : 'Successfully login.'
                    }, headers=headers)

class Logout(viewsets.ViewSet):  

    permission_classes = (AllowAny,)
    serializer_class = LogoutSerializer

    def create(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        if token:
            token.delete()
        else:
            pass
        return Response({
                    "status": status.HTTP_200_OK,
                    "message" : 'Successfully logout.'
                    })
