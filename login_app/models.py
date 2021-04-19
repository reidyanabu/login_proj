from django.db import models
from datetime import datetime
from datetime import timedelta
import re

class UserManager(models.Manager):

    # form validation for user login
    def user_login_validator(self,post_data):

        EMAIL_REGEX     = re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        LOGIN_ERROR_MSG = "Login: "

        errors = {}
        if 'login_email' in post_data:
            login_email = post_data['login_email']
            if not EMAIL_REGEX.match(login_email):
                errors["login_email"] = LOGIN_ERROR_MSG + "Invalid email address entered"
        else:
            errors['login_email'] = LOGIN_ERROR_MSG + 'No email address entered. Please enter a password.'

        if 'login_password' in post_data:
            password = post_data['login_password']
            if (len(password)<8):
                errors['login_password'] = LOGIN_ERROR_MSG + "Invalid password entered, must be at least 8 characters"
        else:
            errors['login_password'] = LOGIN_ERROR_MSG + 'No password entered. Please enter a password.'
        
        return errors


    # form validation for user account creation
    def create_user_data_validator(self,post_data):

        DATE_REGEX  = re.compile('(\d{4})[/.-](\d{2})[/.-](\d{2})$')
        EMAIL_REGEX = re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        CHARS_ONLY  = re.compile(r'^[a-zA-Z]+$')
        REG_ERROR_MSG = "Registration: "

        errors = {}
        
        # first and last name
        first_name = post_data['first_name']
        last_name  = post_data['last_name']
        if (len(first_name) < 3):
            errors["first_name"] = REG_ERROR_MSG + "First name should be at least 2 characters"
        # last_name
        if (len(last_name) < 3):
            errors["last_name"] = REG_ERROR_MSG + "Last name should be at least 2 characters"
        if (not CHARS_ONLY.match(first_name)) or (not CHARS_ONLY.match(last_name)):
            errors["first_name"] = "Names should contain characters only"
        # email
        if ('email' in post_data):
            email_in = post_data['email']
            if not EMAIL_REGEX.match(email_in):
                errors["email"] = REG_ERROR_MSG + "Invalid email address entered"
            else:
                # format was valid .. now we check to see if value already exists ..
                # if inserting/updating to new value check might not 
                # need to be here .. but in the views logic
                email_exists = User.objects.filter(email=email_in).count()
                if email_exists > 0:
                    errors['email'] = REG_ERROR_MSG + "Email already exists in system, use another one"
        else:
            # we should not get here due to front end validation .. but check anyways
            errors['email'] = REG_ERROR_MSG + 'No email address entered'

        password = post_data['password']
        confirm_password = post_data['confirm_password']

        if (len(password)>8) and (len(confirm_password)>8):
            
            # both were entered .. check to see if they match
            if (password != confirm_password):
                errors['password'] = REG_ERROR_MSG + 'Password and confirmation passwords need to match'
        else:
            errors['password'] = REG_ERROR_MSG + 'Password and confirmation passwords need to be at least 8 characters long'

        # birthday
        if not DATE_REGEX.match(post_data['birthday']):
            errors["birthday"] = REG_ERROR_MSG + "Invalid birthday entered"
        else:
            birthday = datetime.strptime(post_data['birthday'], "%Y-%m-%d")
            # CHECK TO SEE IF BIRTHDAY IS AT LEAST 13 YEARS PRIOR TO TODAY
            date_today = datetime.today().date()
            thirteen_years = timedelta(13 * 365)
            thirteen_years_ago = date_today - thirteen_years

            if birthday.date() > thirteen_years_ago:
                errors["birthday"] = REG_ERROR_MSG + "You must be at least 13 years old to sign up"

        return errors

    # validates the data necessary to create a book
    def create_book_data_validator(self, post_data):
        errors = {}

        # title and desc
        title = post_data['title'] + ''
        desc  = post_data['desc'] + ''
        if (len(title) < 1):
            errors["title"] = "Book title is required"
        # desc
        if (len(desc) < 5):
            errors["desc"] = "Description should be at least 5 characters"

        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    email      = models.CharField(max_length=255)
    password   = models.CharField(max_length=255)
    birthday   = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # messages = Message[] .. a User may have many Messages
    # comments = Comment[] .. a User may have many Comments
    # books_uploaded = Book[] .. a User may upload books
    # liked_books = Book[] .. a User may like any number of different Books
    # adding manager to handle validation
    objects = UserManager()

class Message(models.Model):
    message = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE) # a User can have many messages
    # comments = Comment[] .. a Message may have many Comments

class Comment(models.Model):
    comment = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) # a User can have many comments
    message = models.ForeignKey(Message, related_name='comments', on_delete=models.CASCADE) # a Message can have many comments


class Book(models.Model):
    title      = models.CharField(max_length=255)
    desc       = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, related_name="books_uploaded", on_delete=models.CASCADE)
    users_who_likes = models.ManyToManyField(User, related_name="liked_books") 