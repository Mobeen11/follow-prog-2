from django.shortcuts import render

# others redirect or http imorts
from django.shortcuts import render, Http404, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone

# models & forms import
from django.contrib.auth.models import User
from .models import UserProfile
from .models import RelationShip
from .models import Post
from follow_unfollow.form import RegisterForm
from follow_unfollow.form import LoginForm
from django.db.models import Q
from .form import PostForm
from tinymce.widgets import TinyMCE
from tinymce.views import render_to_link_list
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
# Create your views here.

def register_view(request):
    register_form = RegisterForm()
    print "sign up form"
    form = RegisterForm(request.POST or None)
    print form
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            print "form is register"
            email = register_form.cleaned_data.get("email")
            username = register_form.cleaned_data.get("username")
            password = register_form.cleaned_data.get("password")
            user = User.objects.create_user(username,email, password)
            print user
            user.save()
            print "register is success"

        else:
            print "form is not valid"
            raise Http404
    else:
        print "error in post"
    return render(request, 'follow_unfollow/signup.html', {'form':register_form})


def login_view(request):
    user = None
    form = LoginForm(request.POST or None)
    # print "start"
    # print form
    if request.method == "POST":
        user = LoginForm(request.POST)
        print "this is the post request"
        if form.is_valid():
            print "form is valid"
            l_username = form.cleaned_data.get("username")
            l_password = form.cleaned_data.get("password")
            user_login = authenticate(username=l_username, password=l_password)
            if user_login is not None:
                auth_login(request, user_login)
                user = request.user
                #return HttpResponseRedirect(reverse('all'))
                return redirect('postlist_view')
                #return render(request, 'profile.html', {'username': l_username })
            else:
                print "error"
    else:
        print "this is error in validation"
    return render(request, 'follow_unfollow/login.html', {'form': form, 'userobj':user} )


def logout_view(request):
    logout(request)
    print "you are logout"
    return HttpResponseRedirect(reverse('login_view'))



def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    #u = User.objects.get(username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    relation = RelationShip.objects.filter(follow=user).values_list('following',flat=True)
    #.exclude(follow = request.user)    # this query goes wrong because you have inserted the wrong data in the get_or_create
    #relation = RelationShip.objects.filter(following=u)
    print "profile",profile
    print  "relation", relation

    form = PostForm()
    print "request.method", request.method
    if request.method == "POST":
        print "this is request"
        form = PostForm(request.POST or None)
        if form.is_valid():
            print "this form is valid"
            post = form.save(commit=False)      #don't know why commit is false
            post.author = request.user
            text = form.cleaned_data.get("text")
            print "t:", text
            post.published_date = timezone.now()
            post.save()
            return redirect('postlist_view')
        else:
            print form.error


    return render(request, 'follow_unfollow/user_profile.html', {"relations": relation, "form":form })


@login_required
def all_view(request):
    u = User.objects.get(email__iexact=request.user.email)
    print "u:",u
    user = User.objects.all().exclude(email=request.user.email)
    relation = RelationShip.objects.filter(follow=u).values_list('following_id',flat=True)      #the following is list of users we are getting the ids by _id
    print "relation:", relation
    return render(request, 'follow_unfollow/profile.html', {"user": user, "relation":relation})


def follow_view(request, username):
    user = User.objects.all().exclude(email=request.user.email)
    follow_user = User.objects.get(username=username)
    print follow_user
    print request.user
    relation, created = RelationShip.objects.get_or_create(follow=request.user, following=follow_user)

    if created:
        print "created", created

    elif relation:
        relation.delete()
        print "relation delete"

    return HttpResponseRedirect('/all/')

def newpost_view(request):
    #post = Post()
    #print post
    #if request.POST:
    #post.author = request.user     #form is also not getting post in here
    ##if request.method == "POST":
    #text = request.POST.get("mytextarea")
    #post.text = text
    #print "this is text",text
    #post.save()
    #return redirect('/all/')
    #post.objects.create(author=post.author, text=text)
    form = PostForm()
    print "request.method", request.method
    if request.method == "POST":
        print "this is request"
        form = PostForm(request.POST or None)
        if form.is_valid():
            print "this form is valid"
            post = form.save(commit=False)      #don't know why commit is false
            post.author = request.user
            text = form.cleaned_data.get("text")
            print "t:", text
            post.published_date = timezone.now()
            post.save()
            return redirect('postlist_view')
        else:
            print form.error


    return render(request,'follow_unfollow/user_profile.html',{'form':form})

@login_required
def postlist_view(request):
    post = Post.objects.filter(published_date__lte = timezone.now()).order_by('published_date')
    #print post
    return render(request, 'follow_unfollow/post_list.html',{'posts':post})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk = pk)
    return render(request, 'follow_unfollow/post_detail.html', {'post':post})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)          #to avoid the failure i.e model doesn't allow the missing field in form to be empty & doesn't have the default values
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            print "this is the post edit"
            return redirect('follow_unfollow/post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
        print "this is the post edit else"
    return render(request, 'follow_unfollow/post_edit.html', {'form': form})


def following_userspost_view(request):

    pass


def follow_users_view(request, username):
    user = get_object_or_404(User, username=username)
    relation = RelationShip.objects.filter(following=user).values_list('follow_id', flat=True)
    posts = Post.objects.filter(author__in = relation)
    print "user",user
    print "relation",relation
    print "post", posts


    return render(request, 'follow_unfollow/followuser.html', {'user':user, 'relation': relation, 'post':posts})


def relationship_status_view(request, username):
    user = get_object_or_404(User, username=username)
    relation_status = RelationShip.objects.filter(following=user).values_list('follow', flat=True)
    mutual_relation_status = RelationShip.objects.filter(follow=user).values_list('following', flat=True)
    test_relation = RelationShip.objects.filter(following__in=relation_status).values_list('following_id', flat=True)

    #.values_list('following_id', flat=True)
    print "relation status", relation_status.username
    print "mutual relation", mutual_relation_status
    print "test relation", test_relation



    return render(request, 'follow_unfollow/relationstatus.html',{'relation_status':relation_status, 'mutualrelation_status':mutual_relation_status})






#social auth views
def home(request):

    if request.user.is_authenticated():
        return redirect('done')
    return render(request, 'home.html')

@login_required
def done(request):

    return render(request, "done.html", {})

def logout_view(request):
    logout(request)
    return redirect('test')

def test(request):
    # # profile = Profile.objects.all()
    # # profile_image = profile.profile_image
    # # context = {'profile_img': profile_image}
    # user  = request.user
    # if user.is_authenticated():
    #     print "user: ", user
    #     profile = Profile.objects.get(username=user)
    #     print "profile: ", profile.profile_image
    #
    #     context = {
    #         # 'image': profile.profile_image,
    #         # 'username': profile.username,
    #         'profile': profile,
    #     }
    #
    # else:
    #     print "user doesn't exist"
    #     context = {}
    # return render(request, 'practice.html', context)
    pass



from calendar import HTMLCalendar
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

class WorkoutCalendar(HTMLCalendar):

    def __init__(self, workouts):
        super(WorkoutCalendar, self).__init__()
        self.workouts = self.group_by_day(workouts)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.workouts:
                cssclass += ' filled'
                body = ['<ul>']
                for workout in self.workouts[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % workout.get_absolute_url())
                    body.append(esc(workout.title))
                    body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(WorkoutCalendar, self).formatmonth(year, month)

    def group_by_day(self, workouts):
        field = lambda workout: workout.performed_at.day
        return dict(
            [(day, list(items)) for day, items in groupby(workouts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)


from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe

def calendar(request):
  #my_workouts = Workouts.objects.order_by('my_date').filter(
  #  my_date__year=year, my_date__month=month
  #)
  cal = (2016, 04)
  states = [
      ['Alabama', 'AL'],
      ['Alaska', 'AK'],
      ['Arizona', 'AZ'],
      ['Arkansas', 'AR'],
      ['California', 'CA'],
      ['Colorado', 'CO'],
      ['Connecticut', 'CT'],
      ['Delaware', 'DE'],
      ['District of Columbia', 'DC'],
      ['Florida', 'FL'],
      ['Georgia', 'GA'],
      ['Hawaii', 'HI'],
      ['Idaho', 'ID'],
      ['Illinois', 'IL'],
      ['Indiana', 'IN'],
      ['Iowa', 'IA'],
      ['Kansas', 'KS'],
      ['Kentucky', 'KY'],
      ['Louisiana', 'LA'],
      ['Maine', 'ME'],
      ['Maryland', 'MD'],
      ['Massachusetts', 'MA'],
      ['Michigan', 'MI'],
      ['Minnesota', 'MN'],
      ['Mississippi', 'MS'],
      ['Missouri', 'MO'],
      ['Montana', 'MT'],
      ['Nebraska', 'NE'],
      ['Nevada', 'NV'],
      ['New Hampshire', 'NH'],
      ['New Jersey', 'NJ'],
      ['New Mexico', 'NM'],
      ['New York', 'NY'],
      ['North Carolina', 'NC'],
      ['North Dakota', 'ND'],
      ['Ohio', 'OH'],
      ['Oklahoma', 'OK'],
      ['Oregon', 'OR'],
      ['Pennsylvania', 'PA'],
      ['Rhode Island', 'RI'],
      ['South Carolina', 'SC'],
      ['South Dakota', 'SD'],
      ['Tennessee', 'TN'],
      ['Texas', 'TX'],
      ['Utah', 'UT'],
      ['Vermont', 'VT'],
      ['Virginia', 'VA'],
      ['Washington', 'WA'],
      ['West Virginia', 'WV'],
      ['Wisconsin', 'WI'],
      ['Wyoming', 'WY'],

  ]
  return render(request, 'follow_unfollow/calendar.html', {'calendar': mark_safe(cal),})





