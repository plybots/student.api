from __future__ import unicode_literals

import datetime
from django.db import models
from django.shortcuts import get_object_or_404


class Sponsor(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=25, unique=True)
    Discount = models.IntegerField(default=0)
    Tuition = models.IntegerField(default=0)
    Boarding = models.IntegerField(default=0)
    Admission = models.IntegerField(default=0)
    Computer = models.IntegerField(default=0)
    Development_fee = models.IntegerField(default=0)
    Class_wear = models.IntegerField(default=0)
    Sports_wear = models.IntegerField(default=0)
    Casual_wear = models.IntegerField(default=0)
    Sweater = models.IntegerField(default=0)
    Jogging = models.IntegerField(default=0)
    School_t_shirt = models.IntegerField(default=0)
    Badge = models.IntegerField(default=0)
    Identity_card = models.IntegerField(default=0)
    Passport_photos = models.IntegerField(default=0)
    Hair_cutting = models.IntegerField(default=0)
    Library = models.IntegerField(default=0)
    Medical = models.IntegerField(default=0)
    Scouts = models.IntegerField(default=0)
    Uce = models.IntegerField(default=0)
    Uace = models.IntegerField(default=0)
    Mock = models.IntegerField(default=0)
    AdditionalClass1Fees = models.IntegerField()
    AdditionalClass2Fees = models.IntegerField()
    AdditionalClass3Fees = models.IntegerField()
    AdditionalClass4Fees = models.IntegerField()
    AdditionalClass5Fees = models.IntegerField()
    AdditionalClass6Fees = models.IntegerField()
    BAdditionalClass1Fees = models.IntegerField()
    BAdditionalClass2Fees = models.IntegerField()
    BAdditionalClass3Fees = models.IntegerField()
    BAdditionalClass4Fees = models.IntegerField()
    BAdditionalClass5Fees = models.IntegerField()
    BAdditionalClass6Fees = models.IntegerField()
    Sciences = models.IntegerField()
    Arts = models.IntegerField()


class Student(models.Model):
    Id = models.AutoField(primary_key=True)
    Student_no = models.IntegerField(unique=True)
    Student_name = models.CharField(max_length=35)
    Student_class = models.IntegerField(range(1, 7))
    Subjects = models.CharField(max_length=20)
    Sponsor = models.IntegerField()
    SponsorName = models.CharField(max_length=45, default="NONE", null=True)
    Offering = models.CharField(max_length=45, default="NONE", null=True)
    Fees_offer = models.IntegerField(default=0)
    Date_created = models.DateField(auto_now_add=True)
    Last_modified = models.DateField(auto_now=True)

    class Meta:
        ordering = ('Student_name',)

    def __str__(self):
        return "{}({})".format(self.Student_name, self.Student_no)


class TermRegistration(models.Model):
    Id = models.AutoField(primary_key=True)
    Student = models.ForeignKey(Student)
    Offering = models.CharField(max_length=20)
    Term = models.IntegerField()
    Year = models.IntegerField()
    Sponsor = models.ForeignKey(Sponsor, null=True, default=None)
    Fees_offer = models.IntegerField(default=0)
    Student_class = models.IntegerField(default=0)

    @property
    def default_sponsor(self):
        return Student.objects.get(Id=self.Student.Id).Sponsor

    class Meta:
        unique_together = ('Student', 'Term', 'Year',)


class Session(models.Model):
    Id = models.AutoField(primary_key=True)
    Start = models.DateField()
    End = models.DateField()
    Term = models.IntegerField()
    Year = models.IntegerField()
    Is_active = models.BooleanField()

    def __unicode__(self):
        return '{}-{}-{}'.format(self.Start, self.End, self.Year)


    class Meta:
        unique_together = ('Term', 'Year',)


class TermClassAdditionalFees(models.Model):
    Id = models.AutoField(primary_key=True)
    Class1 = models.IntegerField()
    Class2 = models.IntegerField()
    Class3 = models.IntegerField()
    Class4 = models.IntegerField()
    Class5 = models.IntegerField()
    Class6 = models.IntegerField()
    Is_Boarding = models.BooleanField(default=False)


class ComputerPayableFees(models.Model):
    Id = models.AutoField(primary_key=True)
    Fees = models.IntegerField()
    IsClass1_applicable = models.BooleanField()
    IsClass2_applicable = models.BooleanField()
    IsClass3_applicable = models.BooleanField()
    IsClass4_applicable = models.BooleanField()
    IsClass5_applicable = models.BooleanField()
    IsClass6_applicable = models.BooleanField()


class TermPayableFees(models.Model):
    Id = models.AutoField(primary_key=True)
    Global = models.IntegerField()
    Boarding = models.IntegerField(default=0)
    Uce = models.IntegerField()
    Uace = models.IntegerField()
    Mock = models.IntegerField()
    Sciences = models.IntegerField()
    Arts = models.IntegerField()
    Admission = models.IntegerField()
    Development = models.IntegerField()
    TermClassAdditionalFees = models.ManyToManyField(TermClassAdditionalFees)
    ComputerPayableFees = models.ForeignKey(ComputerPayableFees, null=True)
    Session = models.OneToOneField(Session, null=True, default=None)


class Receipt(models.Model):
    Id = models.AutoField(primary_key=True)
    Amount_paid = models.IntegerField()
    Receipt_date = models.DateField()
    Receipt_number = models.CharField(max_length=8, default='0000', unique=True)
    Student = models.ForeignKey(Student)
    Session = models.ForeignKey(Session)
    Date_created = models.DateField(auto_now_add=True)
    Last_modified = models.DateField(auto_now=True)


class Uniform(models.Model):
    Id = models.AutoField(primary_key=True)
    Class_wear = models.IntegerField()
    Sports_wear = models.IntegerField()
    Casual_wear = models.IntegerField()
    Sweater = models.IntegerField()
    Jogging = models.IntegerField()
    School_t_shirt = models.IntegerField()
    Badge = models.IntegerField()
    Student = models.ForeignKey(Student)
    Receipt = models.ForeignKey(Receipt, null=True)
    Session = models.ForeignKey(Session)


class Others(models.Model):
    Id = models.AutoField(primary_key=True)
    Identity_card = models.IntegerField()
    Passport_photos = models.IntegerField()
    Hair_cutting = models.IntegerField()
    Library = models.IntegerField()
    Medical = models.IntegerField()
    Scouts = models.IntegerField()
    Student = models.ForeignKey(Student)
    Receipt = models.ForeignKey(Receipt)
    Session = models.ForeignKey(Session)


class Misc(models.Model):
    Id = models.AutoField(primary_key=True)
    Role = models.TextField()
    Cost = models.IntegerField()
    Student = models.ForeignKey(Student)
    Receipt = models.ForeignKey(Receipt)
    Session = models.ForeignKey(Session)


class TextBooks(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Role = models.TextField()
    Cost = models.IntegerField()
    Student = models.ForeignKey(Student)
    Receipt = models.ForeignKey(Receipt)
    Session = models.ForeignKey(Session)


class Exam(models.Model):
    Id = models.AutoField(primary_key=True)
    Uce = models.IntegerField()
    Uace = models.IntegerField()
    Mock = models.IntegerField()
    Student = models.ForeignKey(Student)
    Receipt = models.ForeignKey(Receipt)
    Session = models.ForeignKey(Session)


class Tuition(models.Model):
    Id = models.AutoField(primary_key=True)
    Tuition = models.IntegerField()
    Admission = models.IntegerField()
    Computer = models.IntegerField()
    Development_fee = models.IntegerField()
    Student = models.ForeignKey(Student)
    Date_created = models.DateField(auto_now_add=True)
    Last_modified = models.DateField(auto_now=True, blank=True)
    Receipt = models.ForeignKey(Receipt)
    Session = models.ForeignKey(Session)


class SponsorReceipt(models.Model):
    Id = models.AutoField(primary_key=True)
    Payment = models.IntegerField(default=0)
    Receipt_number = models.CharField(max_length=5, default="XXXX", unique=True)
    Receipt_date = models.DateField(default=datetime.datetime.now().strftime("%Y-%m-%d"))
    Sponsor = models.ForeignKey(Sponsor)
    Session = models.ForeignKey(Session)
    Date_created = models.DateField(auto_now_add=True)
    Last_modified = models.DateField(auto_now=True, blank=True)


class BalanceForwarded(models.Model):
    Id = models.AutoField(primary_key=True)
    Tuition = models.IntegerField(default=0)
    Admission = models.IntegerField(default=0)
    Computer = models.IntegerField(default=0)
    Student = models.ForeignKey(Student)
    Development_fee = models.IntegerField(default=0)
    Uce = models.IntegerField(default=0)
    Uace = models.IntegerField(default=0)
    Mock = models.IntegerField(default=0)
    Session = models.ForeignKey(Session, default=None)
    Manual = models.BooleanField(default=False)
    Date_created = models.DateField(auto_now_add=True)
    Last_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('Student', 'Session',)


class About(models.Model):
    Id = models.AutoField(primary_key=True)
    Sandstorm = models.TextField()
    Product_description = models.TextField()
    Version = models.CharField(max_length=30)


class LicensedTo(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Location = models.TextField()
    Address = models.TextField()
    Telephone = models.IntegerField()
    Email = models.EmailField()

