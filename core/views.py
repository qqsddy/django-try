from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
import logging
from storages.backends.gcloud import GoogleCloudStorage
from google.cloud import storage

bucket_name = 'try-deploy-django-bucket'

logging.basicConfig(filename='/demo/var/logs/debug.log', level=logging.DEBUG)

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []
    
    user_following = FollowersCount.objects.filter(follower=user_object.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_list = Post.objects.filter(user=usernames)
        feed.append(feed_list)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_following_all.append(User.objects.get(username=user.user))

    new_suggestions_list = [x for x in list(all_users) if x not in list(user_following_all)]
    current_user = User.objects.first()
    final_suggestions_list = [x for x in list(new_suggestions_list) if x != current_user]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        username_profile_list.append(Profile.objects.filter(id_user=ids))

    suggestions_profile_list = list(chain(*username_profile_list))


    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_profile_list':suggestions_profile_list[:4] })

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
            
        # Upload the image to Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        # Set the URL link as the content to upload
        url_link = f'https://storage.cloud.google.com/{bucket_name}/posts/{image.name}'
        blob.upload_from_string(url_link)

        # Get the public URL for the blob
        image_url = blob.public_url

        #blob = bucket.blob('posts/' + image.name)
        #blob.upload_from_filename(image)
        #image_url = blob.public_url
        
        # Create a new post object and save the public URL to the database
        post = Post.objects.create(user=user.username, image=image_url, caption=caption)
        post.save()

        return redirect('/')

    return redirect('/')
  
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(user=pk, follower=follower):
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    num_user_follower = len(FollowersCount.objects.filter(user=pk))
    num_user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'num_user_follower': num_user_follower,
        'num_user_following': num_user_following,

    }

    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.num_of_likes = post.num_of_likes + 1
        post.save()

    else:
        like_filter.delete()

        post.num_of_likes = post.num_of_likes - 1
        post.save()

    return redirect('/')

@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()

        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()

        return redirect('/profile/' + user)    

    return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        search_username = request.POST['search']
        username_object = User.objects.filter(username__icontains=search_username)

        username_profile = []
        username_profile_list = []

        for user in username_object:
            username_profile.append(user.id)
        
        for id in username_profile:
            username_profile_list.append(Profile.objects.filter(id_user=id))

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {
        'user_profile': user_profile,
        'username_profile_list': username_profile_list
    })
    
@login_required(login_url='signin')
def settings(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        logging.debug('profile doesnot exist')
    except:
        logging.debug('error.....')

    
    if request.method == 'POST':
        bio = request.POST['bio']
        location = request.POST['location']
        if request.FILES.get('profile_img') == None:
            image = user_profile.profileimg
        if request.FILES.get('profile_img') != None:
            image = request.FILES.get('profile_img')
            
        # Upload the image to Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob('profiles/' + image.name)
        blob.upload_from_filename(image)
        image_url = blob.public_url
        logging.debug(f'image url -----------------------------------: {image_url}-----------------------------')
        
        user_profile.profileimg = image_url
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()


        return redirect('/')

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN', None)
        if not csrf_token:
            csrf_token = request.POST.get('csrfmiddlewaretoken', None)
        if not csrf_token:
            logging.debug("error---------------------------")

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
                user_model = User.objects.get(username=username)
                profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    
    return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invaild')
            return redirect('signin')

    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


