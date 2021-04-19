from django.shortcuts import render, redirect
from .models import User, Message, Comment, Book
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
import bcrypt

def show_login(request):
    # remove previous session .. this is my prerogative :)
    if 'user_first_name' in request.session:
        del request.session['user_first_name']

    return render(request, "login.html")


def register_user(request):

    # remove previous session .. this is my prerogative :)
    if 'user_first_name' in request.session:
        del request.session['user_first_name']

    post_data = request.POST

    # validate users input
    errors = User.objects.create_user_data_validator(post_data)

    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        return redirect('/')
    else:
        # register the new user
        first_name_in = post_data['first_name']
        last_name_in  = post_data['last_name']
        email_in      = post_data['email']
        birthday_in   = datetime.strptime(post_data['birthday'], "%Y-%m-%d")
        password_in   = post_data['password']
        pw_hash       = bcrypt.hashpw(password_in.encode(), bcrypt.gensalt()).decode() 
        # we use bcryot to generate a salt, and use it to bcrypt hash the password, which is stored in the db
        
        user = User.objects.create(first_name=first_name_in,last_name=last_name_in,email=email_in,birthday=birthday_in,password=pw_hash)

        # create a user session and place user in it
        request.session['user_first_name'] = user.first_name
        request.session['user_id'] = user.id
    
        return redirect("/success")


def process_login(request):
    # remove previous session .. this is my prerogative :)
    if 'user_first_name' in request.session:
        del request.session['user_first_name']
    post_data = request.POST
    errors = User.objects.user_login_validator(post_data)

    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        # we had errors .. set values BACK to context so we can re-populate the page
        #context = {
        #    "login_email": post_data['login_email'],
        #    "login_password": post_data['login_password']
        #}
        return redirect('/')
    else:
        # no validation errors, proceed to get the user
        email_in    = post_data['login_email']
        password_in = post_data['login_password']
        try:
            user = User.objects.get(email=email_in)
            
            if bcrypt.checkpw(password_in.encode(), user.password.encode()):

                # create a user session and place user in it
                request.session['user_first_name'] = user.first_name
                request.session['user_id'] = user.id
                
                return redirect("/success")
            else:
                # passwords did not match!
                errors['login_password'] = "Incorrect password entered"
                # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
                for key, value in errors.items():
                    messages.error(request, value)

                return redirect('/')

        except Exception as e:
            print(f"exception logging in user: {e}")
            errors['General'] = f"Error logging in user: {e}"
            # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
            for key, value in errors.items():
                messages.error(request, value)

            return redirect('/')


def show_success(request):
    # get the user from the session and pass to view
    if 'user_first_name' in request.session:
        
        return render(request, "success.html")
    else:
        # not logged in
        return redirect("/")


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_first_name']
        del request.session['user_id']
    return redirect("/")

# AJAX call which takes an email string and compares it to values in the database and returns a JsonResponse object
def email_exists(request):

    email = request.GET['email']

    email_exists = User.objects.filter(email=email).exists()
    data = {
        'email_exists': email_exists
    }
    return JsonResponse(data)

def wall(request):
    if 'user_id' not in request.session or 'user_first_name' not in request.session:
        return redirect("/")
    # get user
    #user_id = request.session['user_id']

    # get messages
    messages = Message.objects.all()

    context = {
        "messages": messages
    }

    return render(request, "wall.html", context)


def post_message(request):
    # get user
    user_id = int(request.session['user_id'])
    user    = User.objects.get(id=user_id)
    message_txt = request.POST['message']
    # create message for given user with entered text .. VALIDATE TEXT ?????????
    message = Message.objects.create(message=message_txt,user=user)

    print(f"created message with id = {message.id}")

    return redirect('/wall')


def post_comment(request):
    # get user and message
    user_id    = int(request.session['user_id'])
    message_id = int(request.POST['message_id'])

    user       = User.objects.get(id=user_id)
    message    = Message.objects.get(id=message_id)

    comment_txt = request.POST['comment']

    # create comment for given user with entered text .. VALIDATE TEXT ??????????
    comment = Comment.objects.create(comment=comment_txt,user=user,message=message)

    return redirect('/wall')

def delete_message(request):
    # get message
    message_id = int(request.GET['message_id'])


    Message.objects.get(id=message_id).delete()

    return redirect('/wall')

def delete_comment(request):
    # get comment
    comment_id = int(request.GET['comment_id'])

    Comment.objects.get(id=comment_id).delete()

    return redirect('/wall')

def books(request):

    books = Book.objects.all()
    context = {
        "books": books
    }
    return render(request, "books.html", context)

def add_book(request):

    post_data = request.POST

    errors = User.objects.create_book_data_validator(post_data)

    if (len(errors)>0):

        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        
        return redirect('/books')
    else:
        # no validation errors, create the book
        title = post_data['title']
        desc  = post_data['desc']
        user_id = int(request.session['user_id'])
        user = User.objects.get(id=user_id)

        book = Book.objects.create(title=title,desc=desc,uploaded_by=user)
        book.users_who_likes.add(user)
        book.save()

        return redirect('/books')


def update_book(request):

    post_data = request.POST
    book_id = int(post_data['book_id'])

    errors = User.objects.create_book_data_validator(post_data)

    if (len(errors)>0):

        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

    else:
        # no validation errors, update the book
        title = post_data['title']
        desc  = post_data['desc']
        
        book = Book.objects.get(id=book_id)
        book.desc = desc
        book.title = title
        #book.users_who_likes.add(user)
        book.save()

    return redirect(f'/books/{book_id}')


def delete_book(request,book_id):

    Book.objects.get(id=book_id).delete()

    return redirect('/books')


def show_book(request,book_id):

    book = Book.objects.get(id=book_id)
    # store flag whether user has favorited this book
    user_id = int(request.session['user_id'])
    user = User.objects.get(id=user_id)
    is_favorite = False
    users_who_like_book = book.users_who_likes
    for current_user in book.users_who_likes.all():
        if current_user == user:
            is_favorite = True

    context = {
        "book": book,
        "is_favorite": is_favorite
    }

    return render(request, "book.html", context)


def like_book(request,book_id):
    user_id = int(request.session['user_id'])

    user = User.objects.get(id=user_id)
    # get the book and add user as a favorite
    book = Book.objects.get(id=book_id)
    user_who_likes_this_book = book.users_who_likes
    user_who_likes_this_book.add(user)

    return redirect(f"/books/{book_id}")

def remove_like_book(request,book_id):

    user_id = int(request.session['user_id'])

    user = User.objects.get(id=user_id)
    # get the book and add remove user from the list of favorites
    book = Book.objects.get(id=book_id)
    user_who_likes_this_book = book.users_who_likes
    user_who_likes_this_book.remove(user)

    return redirect(f"/books/{book_id}")