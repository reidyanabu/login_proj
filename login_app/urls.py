from django.urls import path
from django.conf.urls import url
from . import views
                    
urlpatterns = [
    path('', views.show_login),
    path('login', views.show_login),
    path('register_user',views.register_user),
    path('process_login', views.process_login),
    path('success', views.show_success),
    path('logout',views.logout),
    path('email_exists',views.email_exists),
    path('ajax/validate_email',views.email_exists,name='validate_email'),
    path('wall',views.wall),
    path('wall/post_message', views.post_message),
    path('wall/post_comment', views.post_comment),
    path('wall/delete_comment', views.delete_comment),
    path('wall/delete_message', views.delete_message),
    path('books', views.books),
    path('books/add_book', views.add_book),
    path('books/<int:book_id>', views.show_book),
    path('books/update', views.update_book),
    path('books/delete_book/<int:book_id>', views.delete_book),
    path('books/like/<int:book_id>', views.like_book),
    path('books/remove_like/<int:book_id>', views.remove_like_book)
]