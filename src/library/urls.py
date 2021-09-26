from django.urls import path, include

from . import views
app_name = "library"
urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    # ex: /books/
    path('books/', views.BookListView.as_view(), name='books'),
    # ex: /library/books/5/
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    # ex: /library/books/5/loans/
    path('books/<int:pk>/loans/', views.loans_of_book),
    # ex: /library/books/5/lend/
    path('books/<int:pk>/lend/', views.lend_book),

    # ex: /library/author/5/
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
]

urlpatterns += [
    # ex: /material/
    path('materials/', views.MaterialListView.as_view(), name='materials'),
    # ex: /library/material/5/
    path('material/<int:pk>', views.MaterialDetailView.as_view(), name='material-detail'),
]

urlpatterns += [
    # ex: /library/mybooks/
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-books'),
     # ex: /library/loaned-books/
    path('loaned-books/', views.LoanedBooksAllListView.as_view(), name='loaned-books'),
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    # ex: /library/authors/
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    # ex: /library/author/create/
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]