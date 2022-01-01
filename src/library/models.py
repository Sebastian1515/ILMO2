from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from datetime import date
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta


class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text=_('Enter a book genre (e.g. Science Fiction)'))

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Material(models.Model):
    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('library:material-detail', args=[str(self.id)])

    name = models.CharField(max_length=200)


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_modify_author", _("Can add, update or delete an author")),)

    def __str__(self):
        """String for representing the Model object."""
        if self.first_name != "":
            return f'{self.last_name}, {self.first_name}'
        else:
            return self.last_name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('library:author-detail', args=[str(self.id)])


class Book(models.Model):
    def __str__(self):
        by = _("by")
        return f"{self.title} {by} {self.author}"

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('library:book-detail', args=[str(self.id)])

    title = models.CharField(max_length=200)
    author = models.ManyToManyField(Author, help_text=_('Select the autor(s) of this book'))
    genre = models.ManyToManyField(Genre, help_text=_('Select a genre for this book'))
    summary = models.TextField(max_length=1000, help_text=_('Enter a brief description of the book'))
    isbn = models.CharField('ISBN', max_length=13, null=True, help_text=_('ISBN number (13 Characters)'))
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text=_("Enter a natural languages name (e.g. English, French, Japanese etc.)"),
                            unique=True)

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True)
    UID = models.CharField(max_length=50, blank=True, help_text=_("The UID of a NFC chip (e.g. in a student id)"))

    @receiver(post_save, sender=User)
    def add_member(sender, instance, created, raw, using, **kwargs):
        if len(Member.objects.filter(user=instance)) != 1:
            Member.objects.create(user=instance)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("library:user-detail", args=[str(self.user.id)])


class Item(models.Model):
    """Represents an item that is physically in the library"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text=_('Unique ID for this particular item across whole library'))
    label = models.CharField(max_length=20, unique=True)

    LOAN_STATUS = (
        ('m', _('Maintenance')),
        ('o', _('On loan')),
        ('a', _('Available')),
        ('r', _('Reserved')),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text=_('Item availability'),
    )

    class Meta:
        permissions = (("can_mark_returned", _("Set item as returned")),
                       ("can_see_borrowed", _("See all borrowed items")))

    def __str__(self):
        return str(f"[{self.label}]")

    def borrow(self,
               borrower: Member,
               due_back=timezone.now() + timezone.timedelta(days=28),
               lent_on=timezone.now()):
        """
        Borrows the item by marking it as on loan and creating a loan

        Parameters
        ----------
        borrower:User The user that borrows the item
        due_back:datetime When the item has to be returned, default is one month later
        lent_on:datetime When the item was lent. Parameter most useful for testing

        Returns
        -------
        None
        """
        l = Loan.objects.create(
            item=self,
            lent_on=lent_on,
            due_back=due_back,
            borrower=borrower,
        )
        l.save()
        # Set status to on loan
        self.status = "o"
        self.save()

    def return_item(self,
                    return_date=timezone.now()) -> bool:
        """
        Sets the item as available and mark the loan as returned

        The st
        Parameters
        ----------
        return_date:datetime=timezone.now()
            Defaults to now, but it is possible to use a custom return date (e.g. to avoid late fees when returned over weekend)

        Returns
        -------
        bool True if successful, else false
        """
        try:
            unreturned_loan_of_item = Loan.objects.filter(item=self,
                                                          returned_on=None)[0]
        except IndexError:
            return False
        unreturned_loan_of_item.returned_on = return_date
        unreturned_loan_of_item.save()
        # Set status to available
        self.status = "a"
        self.save()
        return True

    @property
    def borrower(self):
        """ Returns the current borrower or 'Not borrowed'"""
        try:
            last_loan = Loan.objects.filter(item=self).latest("lent_on")
            if last_loan.returned:
                raise Loan.DoesNotExist
            else:
                return last_loan.borrower
        except Loan.DoesNotExist:
            # Translators: Is shown instead of a person that borrowed the item
            return _("Not borrowed")


class BookInstance(Item):
    """Represents a copy of a book that is physically in the library"""

    def __str__(self):
        by = _("by")
        return f"[{self.label}] {self.book.title} {by} {self.book.author}"

    def get_absolute_url(self):
        """Returns the url to access a detail record for this bookInstance."""
        return reverse('library:bookInstance-detail', args=[str(self.id)])

    book = models.ForeignKey('Book', on_delete=models.RESTRICT)
    imprint = models.CharField(max_length=200, null=True, blank=True)


class MaterialInstance(Item):
    """Represents a instance of a material that is physically in the library"""

    def __str__(self):
        return f"[{self.label}] {self.material.name}"

    def get_absolute_url(self):
        """Returns the url to access a detail record for this materialInstance."""
        return reverse('library:materialInstance-detail', args=[str(self.id)])

    material = models.ForeignKey('Material', on_delete=models.RESTRICT, null=True)


class Loan(models.Model):
    borrower = models.ForeignKey(Member, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    lent_on = models.DateField()
    due_back = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    def __str__(self):
        """String representation."""
        return f"{self.item} _(borrowed until) {self.due_back}"

    def get_absolute_url(self):
        """Returns the url to access a detail record for this loan."""
        return reverse('library:loan-detail', args=[str(self.id)])

    def remind(self):
        LoanReminder.objects.create(loan=self, sent_on=timezone.now().date())

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    @property
    def returned(self):
        if self.returned_on:
            return True
        else:
            return False

    @property
    def last_reminder(self):
        try:
            return LoanReminder.objects.filter(loan=self).latest("sent_on").sent_on
        except LoanReminder.DoesNotExist:
            return self.lent_on

    @property
    def reminder_due(self):
        """True if a reminder is due, else false."""
        reminder_interval = 28
        days_since_last_reminder = datetime.now().date() - self.last_reminder
        return days_since_last_reminder >= timedelta(days=reminder_interval)

    class Meta:
        permissions = (('can_add_loan', _('Can add a loan for all user')),)


WEEKDAYS = [
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
]


class OpeningHours(models.Model):
    weekday = models.IntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    comment = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ('weekday', 'from_hour')
        unique_together = ('weekday', 'from_hour', 'to_hour')
        permissions = (('change_opening_hours', _('Can change opening hours')),)

    def __str__(self):
        return f"{self.get_weekday_display()} {self.from_hour:%H:%M}-{self.to_hour:%H:%M}"


class LoanReminder(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    sent_on = models.DateField()


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for this room'))
    name = models.CharField(max_length=200, unique=True)
    allowed_user = models.ManyToManyField(User, help_text=_("Users that are allowed to access this room"))

    def __str__(self):
        return f"Room: {self.name}"

    def check_access(self, user):
        """ Check if the given user is allowed in the room"""
        return (user in self.allowed_user.all())
