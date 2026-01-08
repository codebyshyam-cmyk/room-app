from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Room,Topic,Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
"""rooms = [
    {'id': 1,
     'name':"lets learn python"
     },
    {'id': 2,
     'name':"lets learn c++"
     },
    {'id': 3,
     'name':"lets learn rust"
     }
]"""

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        username= request.POST.get('username').lower()
        password = request.POST.get('password').lower()
        
        
        
        user = authenticate(request,username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else :
            messages.error(request,'username or password doesnt exit')
    context = {'page':page}
    return render(request,'base/login_register.html',context)

def register(request):
    page = 'logout'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('login-room')
        else :
            messages.error(request,'an error occured during registration')
    context={'form':form}
    return render(request,'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q)|
                                Q(name__icontains=q)|
                                Q(description__icontains=q)|
                                Q(host__username__icontains=q)) 
    topic = Topic.objects.all()
    room_count=rooms.count()

    context = {'rooms':rooms,'topics':topic,'room_count':room_count}
    return render(request,'base/home.html',context)



def room(request,pk):
    rooms = Room.objects.get(id=pk)
    participant = rooms.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room =rooms ,
            body = request.POST.get('body'))
        rooms.participants.add(request.user)
        return redirect('room',pk=rooms.id)
    room_message = rooms.message_set.all()  .order_by('-created')
    context = {'room':rooms,'room_message':room_message,'participants':participant}
    return render(request,'base/room.html',context=context)


@login_required(login_url= 'login-room')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url= 'login-room')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
            return HttpResponse("you are not allowed here")
    
    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url= 'login-room')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
            return HttpResponse("you are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url= 'login-room')
def deleteMessage(request,pk):
    message= Message.objects.get(id=pk)
    if request.user != message.user:
            return HttpResponse("you are not allowed here")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})

def logoutpage(request):
    logout(request)
    return redirect('home')
    