from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm, CreateViewForm, SharerForm, SharerUpdateForm, DriverRegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, FormView
from .models import Ride, Sharer, Driver, Vehicle
from django.urls import reverse
from django.forms import DateTimeField
from django.utils.safestring import mark_safe
from django.db.models import Q
import datetime
from django.core.mail import send_mail


# Create your views here.
def about(request):
    return render(request, 'ride_app/about.html', {'title': 'About'})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}, your account is created. You can log in now!')
            return redirect('login')
        else:
            errdict = form.errors.as_data()
            result = set()
            errset = set(errdict.keys())
            for key in errset:
                if key == 'password1' or key == 'password2':
                    result.add('password')
                else:
                    result.add(key)
            error_message = 'Invalid ' + ' '.join(list(result)) + '. Please follow instructions'
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
    else:
        form = RegisterForm()
    return render(request, 'ride_app/register.html', {'RegisterForm': form})



def logout_view(request):
    logout(request)
    if not request.user.is_authenticated:
        messages.success(request, f'You have successfully logged out. You can log in again.')
    return redirect('login')


@login_required
def userhome(request):
    return render(request, 'ride_app/home.html')



class RideCreateView(LoginRequiredMixin,CreateView):
    #model = Ride
    template_name = 'ride_app/ride_req.html'
    #fields = ['dest_addr', 'arr_date_time', 'no_persons_owner', 'can_shared', 'max_allowed_persons', 'special_request', 'owner_vehicle_type']
    form_class = CreateViewForm

    def form_valid(self, form):
        #form.instance.owner_name = self.request.user.username
        #form.instance.owner_email = self.request.user.email
        form.instance.owner = self.request.user
        form.instance.status = 'open'

        return super(RideCreateView, self).form_valid(form)



class RideListView(LoginRequiredMixin, ListView):
    model = Ride

    template_name = 'ride_app/ride_activities.html'
    context_object_name = 'qs'
    ordering = ['-arr_date_time']
    # filter ride status
    def get_queryset(self):
        qs = Ride.objects.filter(status__in = ["open", "confirmed"])
        return qs



class RideDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ride
    template_name = 'ride_app/ride_delete.html'
    success_url = '/home/activities'

    def delete(self, request, *args, **kwargs):
        if self.get_object().status == "open":
            return super(RideDeleteView, self).delete(request, *args, **kwargs)
        else:
            error_message = "You cannot cancel a confirmed ride"
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return redirect('/home/activities')



    def test_func(self):
        ride = self.get_object()
        #if self.request.user.username == ride.owner_name:
        if self.request.user == ride.owner:
            return True
        return False



class RideDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Ride

    def test_func(self):
        ride = self.get_object()
        # if self.request.user.username == ride.owner_name:
        if self.request.user == ride.owner:
            return True
        for sharer in ride.sharer.all():
            if self.request.user == sharer.user:
                return True
        return False


class RideUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ride
    fields = ['dest_addr', 'arr_date_time', 'no_persons_owner', 'can_shared', 'special_request', 'owner_vehicle_type']
    template_name =  'ride_app/ride_update.html'
    condition = None


    def form_valid(self, form):
        # form.instance.owner_name = self.request.user.username
        # form.instance.owner_email = self.request.user.email
        form.instance.owner = self.request.user
        form.instance.status = 'open'

        form_dest_addr = form.cleaned_data.get('dest_addr')
        form_arr_date_time = form.cleaned_data.get('arr_date_time')
        form_can_shared = form.cleaned_data.get('can_shared')

        ride = self.get_object()
        ride.arr_date_time = form_arr_date_time
        ride.save()
        old_dest_addr = ride.dest_addr
        old_can_shared = ride.can_shared

        # check if destination address is changed
        if form_dest_addr != old_dest_addr:
            ride.dest_addr = form_dest_addr
            ride.save()
            send_mail(f'The ride {ride.unique_id} you shared has changed its destination address',
                      f'The new destination address is {form_dest_addr}. You can cancel the share if the new destination address does not fit you',
                      'djangohw1server@gmail.com',
                      [share.user.email for share in ride.sharer.all()],
                      fail_silently=False, )

        # check if new arrive date time is ok for sharers
        for share in ride.sharer.all():
            earliest_time = share.earliest_time
            latest_time = share.latest_time
            if form_arr_date_time < earliest_time:
                # specific sharer
                send_mail(f'The ride {ride.unique_id} has changed its arrival time',
                          f'The new arrival time is before your allowed earliest time',
                          'djangohw1server@gmail.com',
                          [share.user.email for share in ride.sharer.all()],
                          fail_silently=False, )
            if form_arr_date_time > latest_time:
                # specific sharer
                send_mail(f'The ride {ride.unique_id} has changed its arrival time',
                          f'The new arrival time is after your allowed latest time',
                          'djangohw1server@gmail.com',
                          [share.user.email for share in ride.sharer.all()],
                          fail_silently=False, )

        # originally can shared, now cannot
        if old_can_shared == True and form_can_shared == False and len(ride.sharer.all()):
            error_message = "You cannot change the sharable status because the ride already has sharers"
            messages.error(self.request, error_message, extra_tags='html_safe alert alert-danger')
            return redirect(f'/home/activities/{ride.id}/update')

        # originally cannot shared, now allowed
        if old_can_shared == False and form_can_shared == True:
            ride.can_shared = True
            ride.save()
            return redirect(f'/home/activities/{ride.id}/update_can_shared')



        return super(RideUpdateView, self).form_valid(form)

    def test_func(self):
        ride = self.get_object()
        if self.request.user == ride.owner and ride.status == "open":
            return True
        else:
            if self.request.user != ride.owner:
                self.condition = 'wrong_user'
            elif ride.status != 'open':
                self.condition = 'confirmed'
            return False

    def handle_no_permission(self):
        print(self.condition)
        if self.condition == 'wrong_user':
            error_message = 'You are not allowed to update this ride because you are not the owner'
        elif self.condition == 'confirmed':
            error_message = 'You can not update your request if the ride has been confirmed'
        messages.error(self.request, error_message, extra_tags='html_safe alert alert-danger')
        success_url = '/home/activities/' + str(self.get_object().id)
        return redirect(success_url)

    def get_success_url(self):
        messages.success(self.request, 'Ride Updated')
        success_url = '/home/activities/'+ str(self.object.id)
        return success_url




def activities(request):
    return render(request, 'ride_app/ride_activities.html')



def validate(request, date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        error_message = "Please enter the datetime field with format YYYY-MM-dd HH:mm."
        messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
        return False


def validateInt(request, no_persons_sharer):
    try:
        val = int(no_persons_sharer)
        if val <= 0:
            raise ValueError
        return True
    except:
        error_message = "Please enter an integer greater than zero."
        messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
        return False


@login_required
def Sharer_CreateView(request):
    dest_addr_query = request.GET.get("dest_addr")
    earliest_time = request.GET.get("earliest_time")
    latest_time = request.GET.get("latest_time")
    no_persons_sharer = request.GET.get("no_persons")

    qs = Ride.objects.filter(status='open', can_shared=True, dest_addr=dest_addr_query)

    # GET request
    if request.method == "GET":

        # first enter sharer home page
        while dest_addr_query is None  or earliest_time is None or\
                latest_time is None or no_persons_sharer is None:
            return render(request, 'ride_app/sharer_rides.html')

        # empty fields
        while dest_addr_query == '' or earliest_time == '' or\
                latest_time == '' or no_persons_sharer == '':
            error_message = "Please enter the blank fields."
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return render(request, 'ride_app/sharer_rides.html')

        # earliest time or latest time is invalid
        while not validate(request, earliest_time) or not validate(request, latest_time):
            return render(request, 'ride_app/sharer_rides.html')

        qs = qs.filter(arr_date_time__range=[earliest_time, latest_time])

        # number of passengers invalid
        while not validateInt(request, no_persons_sharer):
            return render(request, 'ride_app/sharer_rides.html')

        # check if latest time is less than earliest time
        if earliest_time > latest_time:
            error_message = "Please make sure latest time is after earliest time."
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return render(request, 'ride_app/sharer_rides.html')

        # filter rides
        context = {"queryset": qs}
        return render(request, 'ride_app/sharer_rides.html', context)

    # POST request
    if request.method == "POST":
        qs = qs.filter(arr_date_time__range=[earliest_time, latest_time])
        data = request.POST.copy()
        joined_ride = Ride.objects.get(pk = data.get('join_ride'))

        # check if sharer is the owner
        context = {"queryset": qs}
        if joined_ride.owner == request.user:
            error_message = "You are owner of this ride. You cannot join your own ride."
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return render(request, 'ride_app/sharer_rides.html', context)

        # check if the sharer has already joined the rides
        accumulated_persons = 0
        for sharer in joined_ride.sharer.all():
            if sharer.user == request.user:
                messages.error(request, "You are already in this ride.", extra_tags='html_safe alert alert-danger')
                return render(request, 'ride_app/sharer_rides.html', context)
            else:
                # count number of persons
                accumulated_persons += sharer.no_persons_sharer
                continue

        # check if the total number of persons would be exceeded if the sharer and his party want to join the ride
        if accumulated_persons + int(no_persons_sharer) > joined_ride.max_allowed_persons:
            left_persons = joined_ride.max_allowed_persons - (accumulated_persons)
            error_message = f'This ride only allows {left_persons} more sharers. <br/> You can reduce the number of persons from your party or choose another ride.'
            messages.error(request, mark_safe(error_message), extra_tags='html_safe alert alert-danger')
            return render(request, 'ride_app/sharer_rides.html', context)

        new_sharer = Sharer(dest_arr=dest_addr_query, earliest_time=earliest_time, latest_time=latest_time,
                                no_persons_sharer=no_persons_sharer)
        new_sharer.user = request.user
        new_sharer.save()
        joined_ride.sharer.add(new_sharer)
        joined_ride.save()
        messages.success(request, f"You have joined the ride {joined_ride.unique_id}. You can view and edit in active-rides.")
        return render(request, 'ride_app/sharer_rides.html', context)




@login_required
def RideSharerUpdateView(request, ride_pk, sharer_pk):
    template_name =  'ride_app/ride_sharerupdate.html'
    print("request get: ", sharer_pk)

    form = SharerUpdateForm()

    if request.method == 'POST':
        form = SharerUpdateForm(request.POST)
        if form.is_valid():
            no_persons = form.cleaned_data.get('no_of_persons')
            print(no_persons)
            # change number of sharer persons in ride
            no_of_sharer_person = Sharer.objects.get(pk = sharer_pk)
            original_no_person = no_of_sharer_person.no_persons_sharer
            no_of_sharer_person.no_persons_sharer = no_persons
            no_of_sharer_person.save()

            # check not exceed max allowed persons
            cnt = 0
            for share in Ride.objects.get(pk = ride_pk).sharer.all():
                cnt += share.no_persons_sharer
            if cnt > Ride.objects.get(pk = ride_pk).max_allowed_persons:
                error_message = "You have exceeded the maximum allowed persons operation failed"
                no_of_sharer_person.no_persons_sharer = original_no_person
                no_of_sharer_person.save()
                messages.error(request, error_message,extra_tags='html_safe alert alert-danger')
                return render(request, template_name, {"form": form})

            return redirect("/home/activities/" + str(ride_pk))

    else:
        if Sharer.objects.get(pk = sharer_pk).user != request.user:
            error_message = "You cannot edit other sharer's rides."
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return redirect("/home/activities/" + str(ride_pk))
        if Ride.objects.get(pk = ride_pk).status == 'open':
            form = SharerUpdateForm()
            return render(request, template_name, {"form": form, "ride_id": ride_pk})
        else:
            messages.error(request, 'This ride has been confirmed; you cannot edit it', extra_tags='html_safe alert alert-danger')
            return redirect('/home/activities/'+ str(ride_pk))



@login_required
def RideSharerDeleteView(request, ride_pk, sharer_pk):
    ride = Ride.objects.get(pk = ride_pk)
    sharer = Sharer.objects.get(pk = sharer_pk)
    if request.method == "POST":
        ride.sharer.remove(sharer)
        sharer.delete()
        messages.success(request, 'You have successfully delete your share')
        return render(request, 'ride_app/ride_activities.html', {'rides': Ride.objects.all()})
    else:
        return render(request, 'ride_app/sharer_delete.html', {'ride': ride})



class DriverRegisterView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    #model = Driver
    form_class = DriverRegisterForm
    template_name = "ride_app/driver_register.html"

    def form_valid(self, form):
        vehicle_make = form.cleaned_data['vehicle_make']
        vehicle_type = form.cleaned_data['vehicle_type']
        vehicle_capacity = form.cleaned_data['vehicle_capacity']
        plate_number = form.cleaned_data['plate_number']
        special_vehicle_info =  form.cleaned_data['special_vehicle_info']
        new_vehicle = Vehicle(vehicle_type = vehicle_type, vehicle_make = vehicle_make, vehicle_capacity = vehicle_capacity, plate_number = plate_number, special_vehicle_info = special_vehicle_info)
        new_vehicle.save()
        driver_license = form.cleaned_data['license_no']
        new_driver = Driver(user = self.request.user, license_no =  driver_license , driver_status = 'no', vehicle = new_vehicle)
        new_driver.save()
        return super(DriverRegisterView, self).form_valid(form)

    def test_func(self):
        try:
            self.request.user.driver
            return False
        except:
            return True

    def handle_no_permission(self):
        error_message = "You have already registered as a driver. You can update your profile in 'Driver' section."
        messages.error(self.request, error_message, extra_tags='html_safe alert alert-danger')
        fail_url = '/home'
        return redirect(fail_url)

    def get_success_url(self):
        messages.success(self.request, 'You have successfully registered as a driver')
        success_url = '/home'
        return success_url



@login_required()
def DriverMenuView(request):
    # check the user is a driver
    if request.method == "GET":
        try:
            driver = request.user.driver
            # filter vehicle type
            qs = Ride.objects.filter(owner_vehicle_type__in = [driver.vehicle.vehicle_type, "All"], status = "open")

            # filter destination address, earliest time, latest time
            dest_addr = request.GET.get("dest_addr")
            earliest_time = request.GET.get("earliest_time")
            latest_time = request.GET.get("latest_time")

            # check None and empty
            if dest_addr is not None and dest_addr != '':
                qs = qs.filter(dest_addr=dest_addr)
            if earliest_time is not None and earliest_time != '':
            # validate time format
                while not validate(request, earliest_time):
                    return render(request, 'ride_app/driver_menu.html')
                qs = qs.filter(arr_date_time__gte = earliest_time)

            # earliest time is before latest time
            if latest_time is not None and latest_time != '':
                while not validate(request, latest_time):
                    return render(request, 'ride_app/driver_menu.html')
                if earliest_time != '':
                    if earliest_time > latest_time:
                        error_message = "Please make sure latest time is after earliest time."
                        messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
                        return render(request, 'ride_app/driver_menu.html')
                qs = qs.filter(arr_date_time__lte = latest_time)

            # filter number of passengers
            cnt_list = []
            res = []
            for ride in qs:
                cnt = ride.no_persons_owner
                if ride.special_request != '' and ride.special_request != driver.vehicle.special_vehicle_info:
                    continue
                if ride.owner == request.user:
                    continue
                flag = 0
                for share in ride.sharer.all():
                    if share.user == request.user:
                        flag = 1
                        break
                    cnt += share.no_persons_sharer
                if flag == 1:
                    continue
                if cnt > driver.vehicle.vehicle_capacity:
                    continue
                res.append(ride.id)
                cnt_list.append(cnt)
            qs = qs.filter(pk__in = res)

            return render(request, 'ride_app/driver_menu.html', {'queryset1': zip(qs, cnt_list), 'driver1': driver})


        except:
             error_message = "You are currently not a driver. You can register as a driver by clicking on 'Be a Driver'"
             messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
             return redirect('/home')

    # confirm the ride
    if request.method == "POST":
        data = request.POST.copy()
        taken_ride = Ride.objects.get(pk=data.get('take_ride'))
        taken_ride.driver = request.user.driver
        taken_ride.status = "confirmed"
        taken_ride.save()
        success_message = f"You have taken the ride {taken_ride.unique_id}"
        messages.success(request, success_message)
        send_mail(f'Your ride {taken_ride.unique_id} has been confirmed',
                  f'Driver {taken_ride.driver.user.first_name} has taken your ride. \nYou can view his information in your ride details now.',
                  'djangohw1server@gmail.com',
                  [taken_ride.owner.email],
                  fail_silently=False,)
        send_mail(f'The ride {taken_ride.unique_id} you shared has been confirmed',
                  f'Driver {taken_ride.driver.user.first_name} has taken that ride. \nYou can view his information in your ride details now.',
                  'djangohw1server@gmail.com',
                  [share.user.email for share in taken_ride.sharer.all()],
                  fail_silently=False,)
        return redirect("/home/activities")


@login_required
def DriverProfileView(request, pk):
    try:
        driver = request.user.driver
        real_driver = Driver.objects.get(pk = pk)
        if driver != real_driver:
            return HttpResponse("404: You cannot view others' profile")
        return render(request, 'ride_app/driver_profile.html', context={'object': driver})
    except:
        error_message = "You are not a driver yet"
        messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
        return redirect('/home')



@login_required
def DriverDetailView(request, pk):
    taken_ride = Ride.objects.get(pk = pk)
    if not taken_ride.driver:
        return HttpResponse("404: This ride is open")
    if taken_ride.driver.user != request.user:
        return HttpResponse("404: You are not the driver of this ride")
    # compute the total number of passengers
    cnt = taken_ride.no_persons_owner
    for share in taken_ride.sharer.all():
        cnt += share.no_persons_sharer
    return render(request, 'ride_app/taken_ride_detail.html', {"object": taken_ride, "no_of_passengers": cnt})


@login_required
def DriverCompleteView(request, pk):
    taken_ride = Ride.objects.get(pk = pk)

    if not taken_ride.driver:
        return HttpResponse("404: This ride is open")

    if taken_ride.driver.user != request.user:
        return HttpResponse("404: You are not the driver of this ride")

    if request.method == "POST":
        taken_ride.status = "complete"
        taken_ride.save()
        success_message = "You have successfully completed the ride"
        messages.success(request, success_message)
        return redirect("/home/activities")

    else:
        return render(request, 'ride_app/driver_complete.html', {'ride': taken_ride})


@login_required
def DriverUpdateView(request, pk):
    driver = Driver.objects.get(pk = pk)
    if request.user != driver.user:
        return HttpResponse("404: You are not allowed to edit others' profile ")

    # check if the driver has uncompleted rides
    for ride in driver.rides.all():
        if ride.status == "confirmed":
            error_message = "You can only update your profile after you complete all confirmed rides"
            messages.error(request, error_message, extra_tags='html_safe alert alert-danger')
            return redirect('/home/drivermenu/profile/' + str(pk))

    form = DriverRegisterForm(initial = {'vehicle_make': driver.vehicle.vehicle_make, 'vehicle_type': driver.vehicle.vehicle_type,\
                                     'vehicle_capacity': driver.vehicle.vehicle_capacity, 'plate_number':driver.vehicle.plate_number,\
                                     'speical_vehicle_info': driver.vehicle.special_vehicle_info, 'license_no': driver.license_no
                                     })
    if request.method == "POST":
        form = DriverRegisterForm(request.POST)
        if form.is_valid():
            vehicle = driver.vehicle
            vehicle.vehicle_make = form.cleaned_data['vehicle_make']
            vehicle.vehicle_type = form.cleaned_data['vehicle_type']
            vehicle.vehicle_capacity = form.cleaned_data['vehicle_capacity']
            vehicle.plate_number = form.cleaned_data['plate_number']
            vehicle.special_vehicle_info =  form.cleaned_data['special_vehicle_info']
            vehicle.save()
            driver.license_no = form.cleaned_data['license_no']
            driver.save()
            success_message = 'You have successfully updated your driver profile'
            messages.success(request, success_message)
        return redirect('/home/drivermenu/profile/' + str(pk))
    else:
        return render(request, 'ride_app/driver_update.html', {'form' : form, 'driver':driver})



class CompletedRideListView(LoginRequiredMixin, ListView):
    model = Ride

    template_name = 'ride_app/ride_history.html'
    context_object_name = 'qs'
    ordering = ['-arr_date_time']
    # filter ride status
    def get_queryset(self):
        qs = Ride.objects.filter(status="complete")
        return qs



@login_required
def OwnerUpdateNumberView(request, pk):
    template_name = 'ride_app/owner_update_number.html'

    form = SharerUpdateForm()

    if request.method == 'POST':
        form = SharerUpdateForm(request.POST)
        if form.is_valid():
            no_persons = form.cleaned_data.get('no_of_persons')
            # change number of sharer persons in ride
            ride = Ride.objects.get(pk=pk)
            ride.max_allowed_persons = no_persons
            ride.save()

            return redirect("/home/activities/" + str(pk))

    else:
        ride = Ride.objects.get(pk=pk)
        if ride.owner != request.user:
            return HttpResponse("404: You cannot edit other owners' rides")
        if ride.can_shared == True and ride.status == 'open':
            form = SharerUpdateForm()
            return render(request, template_name, {"form": form, "ride_id": pk})
        else:
            messages.error(request, 'This ride is not sharable or has been confirmed; you cannot edit it',
                           extra_tags='html_safe alert alert-danger')
            return redirect('/home/activities/' + str(pk))