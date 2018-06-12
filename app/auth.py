from __future__ import print_function
import json

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

from app.models import TermRegistration
from app.serializers import SessionSerializer
from app.views import __active_session__


@csrf_exempt
def auth_mobile_admin(request):
    # for reg in TermRegistration.objects.all():
    #     reg.Sponsor_id = reg.default_sponsor
    #     reg.save()

    if request.method == 'POST':
        request_body = json.loads(request.body)
        name = request_body["Username"]
        pwd = request_body["Password"]
        user = authenticate(username=name, password=pwd)
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                response = HttpResponse(
                    json.dumps({'Status': True, 'msg': 'user authenticated', 'Token': "Token %s" % token.key,
                                'Username': "%s" % user.username, 'Id': "%d" % user.id, 'Email': "%s" % user.email,
                                'SessionJson': SessionSerializer(__active_session__(), many=False,
                                                             context={'request': request}).data}),
                    content_type="application/json")
                response['X-Authorization'] = "Token %s" % token.key
                return response
            else:
                return HttpResponse(
                    json.dumps({'Status': False, 'msg': 'user account is not active.', 'errorCode': 11404}),
                    status=401),
        else:
            return HttpResponse(
                json.dumps({'Status': False, 'msg': 'user account doesn\'t exist.', 'errorCode': 11401}), status=401)
    else:
        return HttpResponseNotAllowed(request.method + ' method is not allowed.')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        # Get request post body
        request_body = json.loads(request.body)
        # Get user registration details from post body
        username = request_body["username"]
        raw_password = request_body['password']
        password = make_password(raw_password)
        email = request_body['email']
        first_name = request_body['first_name']
        last_name = request_body['last_name']
        # Check if user exists in database
        users = User.objects.filter(username=username)
        # Evaluate true if user doesn't exit
        if len(users) == 0:
            # create new user object
            new_user = User(password=password, is_superuser=0, username=username, first_name=first_name,
                            last_name=last_name, email=email, is_staff=0, is_active=1, )
            # save user object to database
            new_user.save()
            # Get added user info from database
            added_user = get_object_or_404(User, username=username)
            # Authenticate user for token generation
            auth_user = authenticate(username=username, password=raw_password)
            # Generate user token
            token, created = Token.objects.get_or_create(user=auth_user)

            # Add user details to response to be returned
            response = HttpResponse(
                json.dumps(
                    {'status': True, 'msg': 'user authenticated', 'token': "Token %s" % token.key,
                     'id': "%s" % added_user.id,
                     'username': "%s" % added_user.username, 'is_superuser': "%d" % added_user.is_superuser,
                     'first_name': "%s" % added_user.first_name, 'last_name': "%s" % added_user.last_name,
                     'email': "%s" % added_user.email, 'is_staff': "%d" % added_user.is_staff,
                     'is_active': "%d" % added_user.is_active}),
                content_type="application/json")
            response['X-Authorization'] = "Token %s" % token.key

            return response
        else:
            return HttpResponseNotAllowed(request.method + ' method is not allowed.')
    else:
        return HttpResponseNotAllowed(request.method + ' method is not allowed.')


@csrf_exempt
def check_username(request):
    if request.method == "GET":
        username = request.GET.get("username")
        users = User.objects.filter(username=username)
        if len(users) > 0:
            user = users[0]
            response = HttpResponse(
                json.dumps(
                    [{'id': "%s" % user.id,
                      'username': "%s" % user.username, 'is_superuser': "%d" % user.is_superuser,
                      'first_name': "%s" % user.first_name, 'last_name': "%s" % user.last_name,
                      'email': "%s" % user.email, 'is_staff': "%d" % user.is_staff,
                      'is_active': "%d" % user.is_active}]
                )
            )
        else:
            response = HttpResponse(
                json.dumps(
                    []
                )
            )
        return response
