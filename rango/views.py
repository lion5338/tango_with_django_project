from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]

    context_dict={}
    context_dict['boldmessage'] = 'Chunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    request.session.set_test_cookie()

    return render(request, 'rango/index.html', context=context_dict)
    
def about(request):
    #context_dict = {'boldmessage':'This tutorial has been put together by HsinCheng Hsieh! '}
    print(request.method)
    print(request.user)
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    context_dict={}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
        
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=True)
            return redirect('/rango')
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
    # Attempt to grab information from the raw form information.
    # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
    # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
        # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
    
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

    # Now we save the UserProfile model instance.
            profile.save()

    # Update our variable to indicate that the template
    # registration was successful.
            registered = True
        else:
        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
        'rango/register.html',
        context = {'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered})
def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
        # Is the account active? It could have been disabled.
            if user.is_active:
            # If the account is valid and active, we can log the user in.
            # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
            # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
        # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    # The request is not a HTTP POST, so display the login form.

    # This scenario would most likely be a HTTP GET.
    else:
    # No context variables to pass to the template system, hence the
    # blank dictionary object...
        return render(request, 'rango/login.html')

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")


def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))


def visitor_cookie_handler(request, response):
        # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(request.COOKIES.get('visits', '1'))
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
    '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        response.set_cookie('last_visit', str(datetime.now()))
    else:
        # Set the last visit cookie
        response.set_cookie('last_visit', last_visit_cookie)
        # Update/set the visits cookie
    response.set_cookie('visits', visits)