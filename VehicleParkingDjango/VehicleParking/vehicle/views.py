from json import JSONDecodeError, JSONDecoder
import sys
from unicodedata import category
from django.db.models import Q
from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate
from datetime import datetime, timedelta, time
import random
from rest_framework.viewsets import ModelViewSet
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.core import serializers

# from email.headerregistry import Address
# from .models import Address
# from .serializer import AddeSeriazer
# from django.http import HttpResponse
# from django.views.decorators import gzip
# from django.http import StreamingHttpResponse
# import cv2
# import threading
# Create your views here.

# class AddressViewSet (ModelViewSet):
#     serialixer_class = AddeSeriazer
#     queryset = Address.objects.all()

def Index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def admin_login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request,user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
        return render(request, 'admin_home.html',)
    d = {'error': error}
    return render(request, 'admin_login.html', d)


def admin_home(request):
    # if not request.user.is_authenticated:
    #     return redirect('admin_home')
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    today = datetime.now().date()
    yesterday = today - timedelta(1)
    lasts = today - timedelta(7)

    tv = Vehicle.objects.filter(pdate=today).count()
    yv = Vehicle.objects.filter(pdate=yesterday).count()
    ls = Vehicle.objects.filter(pdate__gte=lasts,pdate__lte=today).count()
    totalv = Vehicle.objects.all().count()

    d = {'tv':tv,'yv':yv,'ls':ls,'totalv':totalv}
    return render(request,'admin_home.html', d)


def Logout(request):
    logout(request)
    return redirect('index')


def change_password(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    error = ""
    if request.method == "POST":
        o = request.POST['password']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = "not"
        except:
            error = "yes"
    d = {'error': error}
    return render(request,'change_password.html',d)


def add_category(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    error = ""
    if request.method=="POST":
        cn = request.POST['categoryname']
        try:
            Category.objects.create(categoryname=cn)
            error = "no"
        except:
            error = "yes"
    d = {'error':error}
    return render(request, 'add_category.html', d)

def manage_category(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    category = Category.objects.all()
    d = {'category':category}
    return render(request, 'manage_category.html', d)

def categories(request):
    category = Category.objects.all()
    data = list(category.values())
    return JsonResponse(data, safe=False)


def delete_category(request,pid):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('manage_category')



def edit_category(request,pid):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    category = Category.objects.get(id=pid)
    error = ""
    if request.method == 'POST':
        cn = request.POST['categoryname']
        category.categoryname = cn
        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    d = {'error': error,'category':category}
    return render(request, 'edit_category.html',d)

@csrf_protect
@csrf_exempt
def add_vehicle(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    error = ""
    category1 = Category.objects.all()
    if request.method=="POST":
        data = json.loads(request.body)
        # print()
        pn = str(random.randint(10000000, 99999999))
        ct =  data['category']
        vc =  data['vehiclecompany']
        rn =  data['regno']
        slot= data['parkingSlot']
        on =  data['ownername']
        oc =  data['ownercontact']
        pd =  data['pdate']
        it =  data['intime']
        status = "In"

        category = Category.objects.get(categoryname=ct)
        slot = Slot.objects.get(slot=slot)
        if slot.status == "UNAVAILABLE":
            d = {'response':error,'message':'slot unavailable'}
            return JsonResponse(d, safe=False)
        if Vehicle.objects.filter(ownername=on).count() > 0:
            d = {'response':error,'message':'You are already booked on another slot.'}
            return JsonResponse(d, safe=False)

        Vehicle.objects.create(parkingnumber=pn,category=category,vehiclecompany=vc,regno=rn,ownername=on,ownercontact=oc,pdate=pd,intime=it,outtime='',parkingslot = slot,parkingcharge='',remark='',status=status)
        slot.status= "UNAVAILABLE"
        slot.save()
    d = {'response':error,'message':'successfully booked'}
    # return render(request, 'add_vehicle.html', d)
    return JsonResponse(d, safe=False)

def manage_incomingvehicle(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    vehicle = Vehicle.objects.filter(status="In")
    d = {'vehicle':vehicle}
    return render(request, 'manage_incomingvehicle.html', d)

def manage_slots(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    slots = Slot.objects.all()
    d = {'slots':slots}
    return render(request, 'manage_slots.html', d)

def view_incomingdetail(request,pid):
    # if not request.user.is_authenticated:
    #     return redirect('admin_home')
    # error = ""
    vehicle = Vehicle.objects.get(id=pid)
    if request.method == 'POST':
        rm = request.POST['remark']
        ot = request.POST['outtime']
        pc = request.POST['parkingcharge']
        status = "Out"
        try:
            vehicle.remark = rm
            vehicle.outtime = ot
            vehicle.parkingcharge = pc
            vehicle.status = status
            vehicle.save()
            error = "no"
        except:
            error = "yes"

    d = {'vehicle': vehicle}
    return render(request,'view_incomingdetail.html', d)

@csrf_exempt
def view_incomingdetail_api(request,pid):
    vehicle = Vehicle.objects.get(id=pid)
    json_data = json.loads(request.body)
    error = "Nothing happpened"
    if request.method == 'POST':
        rm = json_data['remark']
        ot = json_data['outtime']
        pc = json_data['parkingcharge']
        status = "Out"
        try:
            vehicle.remark = rm
            vehicle.outtime = ot
            vehicle.parkingcharge = pc
            vehicle.status = status
            vehicle.save()
            error = "Checkout successful"
        except:
            error = "Checkout failed"

    
    return JsonResponse({"resp" : error}, safe=False)

def current_booking(request,username):
    # if not request.user.is_authenticated:
    #     return redirect('admin_home')
    # error = ""
    print(request.body)
    vehicle = Vehicle.objects.get(ownername=username, status="In")
    error = "Success"
    if request.method == 'POST':
        rm = request.POST['remark']
        ot = request.POST['outtime']
        pc = request.POST['parkingcharge']
        status = "Out"
        try:
            vehicle.remark = rm 
            vehicle.outtime = ot
            vehicle.parkingcharge = pc
            vehicle.status = status
            vehicle.save()
            error = "no"
        except:
            error = "yes"





    data = {
       "parkingNumber": vehicle.parkingnumber,
       "parkingSlot": vehicle.parkingslot ,
       "intime": vehicle.intime
       }

    obj = {
    "data": data,
    "response": error
    }
    return JsonResponse(  obj, safe=False)


def manage_outgoingvehicle(request):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    vehicle = Vehicle.objects.filter(status="Out")
    d = {'vehicle':vehicle}
    return render(request, 'manage_outgoingvehicle.html', d)

def receipts_api(request, username):
    vehicles = Vehicle.objects.filter(ownername=username,status="Out")

    data = list(vehicles.values())
    return JsonResponse(data, safe=False)


def view_outgoingdetail(request,pid):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'view_outgoingdetail.html', d)


def print_detail(request,pid):
    #if not request.user.is_authenticated:
        #return redirect('admin_login')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'print.html', d)

def print_detail_api(request,pid):
    vehicle = Vehicle.objects.get(id=pid)

    data = {'vehicle': vehicle}

    return JsonResponse(data, safe=False)


def search(request):
    q = None
    if request.method == 'POST':
        q = request.POST['searchdata']
    try:
        vehicle = Vehicle.objects.filter(Q(parkingnumber=q))
        vehiclecount = Vehicle.objects.filter(Q(parkingnumber=q)).count()

    except:
        vehicle = ""
    d = {'vehicle': vehicle,'q':q,'vehiclecount':vehiclecount}
    return render(request, 'search.html',d)


def betweendate_reportdetails(request):
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'betweendate_reportdetails.html')



def betweendate_report(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        fd = request.POST['fromdate']
        td = request.POST['todate']
        vehicle = Vehicle.objects.filter(Q(pdate__gte=fd) & Q(pdate__lte=td))
        vehiclecount = Vehicle.objects.filter(Q(pdate__gte=fd) & Q(pdate__lte=td)).count()
        d = {'vehicle': vehicle,'fd':fd,'td':td,'vehiclecount':vehiclecount}
        return render(request, 'betweendate_reportdetails.html', d)
    return render(request, 'betweendate_report.html')


@csrf_exempt
def slot(request):
    
    if request.method == "POST":
        slot = request.POST['slot']
        desc = request.POST['desc']
        Slot.objects.create(slot=slot,desc=desc,status="AVAILABLE")
        return redirect('manage_slots')



    if request.method == "GET":
        slots = Slot.objects.all()
        data = list(slots.values())
        return JsonResponse(data, safe=False)
        

@csrf_exempt
def slotUpdate(request):
    
    if request.method == "POST":
        slot = request.POST['slot']
        status = request.POST['status']
        u = Slot.objects.get(id=slot) 
        u.status = status
        u.save()
        Slot.objects.create(slot=slot,status=status)
        return JsonResponse(["Success"], safe=False)

@csrf_exempt
def slotDelete(request):
    
    if request.method == "POST":
        slotId = request.POST['slot']
        u = Slot.objects.get(id=slotId) 
        u.delete()
        return redirect('manage_slots')

@csrf_exempt
def register(request):
    json_data = json.loads(request.body)
    # print(json_data['name'])
    user = User.objects.create_user(
        json_data['name'],
        json_data['email'], 
        json_data['password'])
    user.save()
    return JsonResponse(["Success"], safe=False)

@csrf_exempt
def Login(request):
    json_data = json.loads(request.body)
    user = authenticate(username=json_data['name'], password=json_data['password'])
    # user = authenticate(username='john', password='secret')
    if user is not None:
        # data = list(user.values())
         
        # # data = json.dumps('json',user)
        # data = serializers.serialize('json', [ user ])
        print(user)
        obj = {
            "name": user.get_username(),
            # "id": user.get_email_field_name()
        }
        return JsonResponse(  obj, safe=False)
    else:
        return JsonResponse(["Login failed"], safe=False)