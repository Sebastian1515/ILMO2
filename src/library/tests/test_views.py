from django.test import Client
from django.test import TestCase
from django.urls import reverse
from library.models import *
from django.utils import timezone
import datetime
from django.contrib.auth.models import Permission
import uuid


# Tests the view of library/my-loans/
class MyLoansView(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Jane", last_name="Doe")
        test_book = Book.objects.create(title="How to Test genres",
                author=Author.objects.create(first_name="Jane", last_name="Doe"),
                summary="Book to test genres",
                isbn="1234567890124")
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            b = BookInstance.objects.create(
                book=test_book,
                label=f'A {book_copy}',
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('library:my-loans'))
        self.assertRedirects(response, '/accounts/login/?next=/library/my-loans/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('library:my-loans'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/list_loans_user.html')

    # Tests if the borrowed items of the user are really shown, only shown when on loan and not anymore books
    def test_content(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('library:my-loans'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        borrower = Member.objects.get(user=User.objects.get(username="testuser1"))
        for book in books:
            book.borrow(borrower=borrower)

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('library:my-loans'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)
        #Check that all books are in context
        self.assertEqual(len(response.context['bookinstance_list']), 10)
        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(bookitem.status, 'o')

class LoanDetailView(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Jane", last_name="Doe")
        test_book = Book.objects.create(title="How to Test genres",
                author=Author.objects.create(first_name="Jane", last_name="Doe"),
                summary="Book to test genres",
                isbn="1234567890124")
        # User to borrow the book
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        # User without permission to see borrower
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        # User with permission to see borrower
        test_user3 = User.objects.create_user(username='testuser3', password='12345')
        permission = Permission.objects.get(name='Can see who borrowed an item')
        test_user3.user_permissions.add(permission)

        b = BookInstance.objects.create(
            book=test_book,
            label=f'A 1 a',
            status="a",
        )
        b.borrow(Member.objects.get(user=test_user1))
        b.save()
        cls.loan1 = Loan.objects.filter(item=b)[0]

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('library:loan-detail', kwargs={'pk': self.loan1.pk}))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/loan-detail.html')

    def test_info_without_login(self):
        response = self.client.get(reverse('library:loan-detail', kwargs={'pk': self.loan1.pk}))
        # Check that we got a response "success" and use correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/loan-detail.html')

        # Check that general loan info but not information on borrower is shown
        self.assertContains(response, f"{self.loan1.pk}")
        self.assertContains(response, str(self.loan1.item.label))
        self.assertNotContains(response, str(self.loan1.borrower))

    def test_info_with_login_no_permission(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('library:loan-detail', kwargs={'pk': self.loan1.pk}))
        # Check that we got a response "success" and use correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/loan-detail.html')

        # Check that general loan info but not information on borrower is shown
        self.assertContains(response, f"{self.loan1.pk}")
        self.assertContains(response, str(self.loan1.item.label))
        self.assertNotContains(response, str(self.loan1.borrower))

    def test_info_with_see_permission(self):
        login = self.client.login(username='testuser3', password='12345')
        response = self.client.get(reverse('library:loan-detail', kwargs={'pk': self.loan1.pk}))
        # Check that we got a response "success" and use correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/loan-detail.html')

        # Check that general loan info but not information on borrower is shown
        self.assertContains(response, f"{self.loan1.pk}")
        self.assertContains(response, str(self.loan1.item.label))
        self.assertContains(response, str(self.loan1.borrower))

class AllLoandBooksView(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Jane", last_name="Doe")
        test_book = Book.objects.create(title="How to Test genres",
                author=Author.objects.create(first_name="Jane", last_name="Doe"),
                summary="Book to test genres",
                isbn="1234567890124")
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        permission = Permission.objects.get(name="See all borrowed items")
        test_user2.user_permissions.add(permission)
        test_user2.save()
        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                label=f'A {book_copy}',
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('library:loaned-items'))
        self.assertRedirects(response, '/accounts/login/?next=/library/loaned-items/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('library:loaned-items'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('library:loaned-items'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/list_loans_all.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('library:loaned-items'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('library:loaned-items'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(bookitem.status, 'o')

class AuthorViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = Author.objects.create(first_name="Jane", last_name="Doe")
        cls.test_author1.save()
        cls.test_author2 = Author.objects.create(first_name="Jim", last_name="Butch")
        cls.test_author2.save()
        cls.test_book = Book.objects.create(title="How to Test views",
                author=cls.test_author1,
                summary="Book to test views",
                isbn="1234567890124")
        cls.test_book.save()

    def test_use_of_correct_template(self):
        response = self.client.get(self.test_author1.get_absolute_url())
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/author.html')

    def test_book_list(self):
        response = self.client.get(self.test_author1.get_absolute_url())

        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that a book by this author is displayed
        self.assertContains(response, "How to Test views")
        self.assertNotContains(response, "No books by this author.")

        response = self.client.get(self.test_author2.get_absolute_url())

        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that a author without books is correctly displayed
        self.assertNotContains(response, "How to Test views")
        self.assertContains(response, "No books by this author.")

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/library/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('library:authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('library:authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/authors.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('library:authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('library:authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)

class BookInstancesDetailViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give test_user1 permission to see borrower books.
        permission_see= Permission.objects.get(name="See all borrowed items")
        test_user1.user_permissions.add(permission_see)
        test_user1.save()

        # Give test_user2 permission to renew books.
        permission_return = Permission.objects.get(name='Set item as returned')
        test_user2.user_permissions.add(permission_return)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        test_book.save()

        # Create a BookInstance object for test_user1
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "1",
        )

        # Create a BookInstance object for test_user2
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "2",
        )

    def test_logged_in_with_permission_see_borrower(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('library:bookInstance-detail', kwargs={'pk': self.test_bookinstance2.pk}))
        # Check that site access is permitted
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')

        #Check that view contains borrower
        self.assertContains(response, "Borrowed by:")

    def test_logged_in_with_permission_to_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:bookInstance-detail', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that user has permission to access site
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that view doesn't contain borrower (user 2 does not have this permission)
        self.assertNotContains(response, "Borrowed by:")
        self.assertContains(response, "Renew")


class MaterialInstancesDetailViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give test_user1 permission to see borrower books.
        permission_see= Permission.objects.get(name="See all borrowed items")
        test_user1.user_permissions.add(permission_see)
        test_user1.save()

        # Give test_user2 permission to renew books.
        permission_return = Permission.objects.get(name='Set item as returned')
        test_user2.user_permissions.add(permission_return)
        test_user2.save()

        # Create a material
        test_material = Material.objects.create(name = "Lab coat")
        test_material.save()

        # Create a MaterialInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_materialinstance1 = MaterialInstance.objects.create(
            material=test_material,
            status = 'o',
            label = "1",
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_materialinstance2 = MaterialInstance.objects.create(
            material=test_material,
            status='o',
            label = "2",
        )

    def test_logged_in_with_permission_see_borrower(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('library:materialInstance-detail', kwargs={'pk': self.test_materialinstance2.pk}))
        # Check that site access is permitted
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')

        #Check that view contains borrower
        self.assertContains(response, "Borrowed by:")
        self.assertNotContains(response, "Renew")

    def test_logged_in_with_permission_to_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:materialInstance-detail', kwargs={'pk': self.test_materialinstance2.pk}))

        # Check that user has permission to access site
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that view doesn't contain borrower (user 2 does not have this permission)
        self.assertNotContains(response, "Borrowed by:")
        self.assertContains(response, "Renew")

class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        # Give test_user2 permission to renew materials.
        permission = Permission.objects.get(name='Set item as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_user3 = User.objects.create_user(username='testuser3', password='12345678')
        # Give test_user3 permission to renew materials and see.
        permission_return = Permission.objects.get(name='Set item as returned')
        permission_see= Permission.objects.get(name="See all borrowed items")
        test_user3.user_permissions.add(permission_return)
        test_user3.user_permissions.add(permission_see)
        test_user3.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "1",
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "2",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/item_renew_librarian.html')

    def test_valid_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('library:renew-item-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}),
                                    {'renewal_date': datetime.date.today()+datetime.timedelta(days=20)}
        )
        # Successful request should redirect
        self.assertRedirects(response, '/library/')

    def test_invalid_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('library:renew-item-librarian',
                                            kwargs={'pk': self.test_bookinstance1.pk}),
                                    {'renewal_date': datetime.date.today() - datetime.timedelta(days=3)},
        )
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')

        # Unsuccessful request should not redirect, but show the form again
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/item_renew_librarian.html')

        # Check response shows error message
        self.assertContains(response, "Invalid date - renewal in past")


class RenewMaterialInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        # Give test_user2 permission to renew materials.
        permission = Permission.objects.get(name='Set item as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_user3 = User.objects.create_user(username='testuser3', password='12345678')
        # Give test_user3 permission to renew materials and see.
        permission_return = Permission.objects.get(name='Set item as returned')
        permission_see= Permission.objects.get(name="See all borrowed items")
        test_user3.user_permissions.add(permission_return)
        test_user3.user_permissions.add(permission_see)
        test_user3.save()

        # Create a material
        test_material = Material.objects.create(
            name='Lab Coat',
        )
        test_material.save()

        # Create a MaterialInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_materialinstance1 = MaterialInstance.objects.create(
            material=test_material,
            status='o',
            label = "1",
        )

        # Create a MaterialInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_materialinstance2 = MaterialInstance.objects.create(
            material=test_material,
            status='o',
            label = "2",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_materialinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_materialinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_material(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_materialinstance2.pk}))

        # Check that it lets us login - this is our material and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_material(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_materialinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users material
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_material_if_logged_in(self):
        # unlikely UID to match our materialinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('library:renew-item-librarian', kwargs={'pk': self.test_materialinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/item_renew_librarian.html')

    def test_valid_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('library:renew-item-librarian',
                                           kwargs={'pk': self.test_materialinstance1.pk}),
                                    {'renewal_date': datetime.date.today()+datetime.timedelta(days=20)}
        )
        # Successful request should redirect
        self.assertRedirects(response, '/library/')

    def test_invalid_renew(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('library:renew-item-librarian',
                                            kwargs={'pk': self.test_materialinstance1.pk}),
                                    {'renewal_date': datetime.date.today() - datetime.timedelta(days=3)},
        )

        # Unsuccessful request should not redirect, but show the form again
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/item_renew_librarian.html')

        # Check response shows error message
        self.assertContains(response, "Invalid date - renewal in past")


"""
Test the view of the index page
"""
class IndexViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_author = Author.objects.create(first_name='Jim', last_name='Knopf')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )
        
        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='a',
            label = "0",
        )

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "1",
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            status='o',
            label = "2",
        )

    # Test if the correct template is used for the library index
    def test_uses_correct_template(self):
        response = self.client.get(reverse('library:index'))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/index.html')

        response = self.client.get('/library/')
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'library/index.html')

    # Test that the site root redirects to the library index
    def test_index_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/library/', status_code=301)

    def test_index_content(self):
        response = self.client.get(reverse('library:index'))

        self.assertEqual(response.status_code, 200)
        # Check that statistics numbers match
        self.assertEqual(response.context['num_books'], 1)
        self.assertEqual(response.context['num_instances'], 3)
        self.assertEqual(response.context['num_instances_available'], 1)
        self.assertEqual(response.context['num_authors'], 2)

class OpeningHoursCreateViewTest(TestCase):
    """Tests the create view for opening hours"""
    def setUp(self):
        # Normal user
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        # User with permission to create opening hours
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        create_permission = Permission.objects.get(codename='change_opening_hours')
        test_user2.user_permissions.add(create_permission)
        test_user1.save()
        test_user2.save()

    def test_without_login(self):
        response = self.client.get(reverse('library:openinghour-create'))
        self.assertRedirects(response, '/accounts/login/?next=/library/openinghour/create')

    def test_with_login(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('library:openinghour-create'))
        self.assertEqual(response.status_code, 403)

    def test_with_permission(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('library:openinghour-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/openinghours_form.html")