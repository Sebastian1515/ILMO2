from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Book
from django.contrib.auth.decorators import login_required, permission_required


from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.all().count()

    # Available books
    num_instances_available = BookInstance.objects.filter(available=True).count()

    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    return render(request, 'library/index.html', context=context)

@login_required
@permission_required('library.show_books', raise_exception=True)
def book_list(request):
    book_list = Book.objects.all()[:5]
    context = {'book_list': book_list}
    return render(request, 'library/books.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'library/book.html', {'book': book})

def loans_of_book(request, book_id):
    response = "You're looking at the loans of book %s."
    return HttpResponse(response % book_id)

def lend_book(request, book_id):
    return HttpResponse("You're lending book %s." % book_id)
