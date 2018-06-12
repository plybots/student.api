from rest_framework import serializers

from app.models import Student, Tuition, Session, TermRegistration, Receipt, Exam, TextBooks, Others, Uniform, Misc, \
    TermClassAdditionalFees, ComputerPayableFees, TermPayableFees, Sponsor, SponsorReceipt, BalanceForwarded, About, \
    LicensedTo


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = (
            'Id', 'Student_no', 'Student_name', 'Student_class', 'Subjects', 'Sponsor', 'SponsorName', 'Offering',
            'Fees_offer', 'Date_created', 'Last_modified')


# noinspection PyAbstractClass
class CustomStudentSerializer(serializers.Serializer):
    Id = serializers.IntegerField()
    Student_no = serializers.IntegerField()
    Student_name = serializers.CharField(max_length=35)
    Student_class = serializers.IntegerField()
    Subjects = serializers.CharField(max_length=20)
    Sponsor = serializers.CharField(max_length=25)
    Date_created = serializers.DateField()
    Last_modified = serializers.DateField()


class TuitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tuition
        fields = (
            'Id', 'Tuition', 'Admission', 'Computer', 'Development_fee', 'Student', 'Receipt', 'Session',
            'Date_created', 'Last_modified')


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('url', 'Id', 'Start', 'End', 'Term', 'Year', 'Is_active')


class TermRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermRegistration
        fields = ('url', 'Id', 'Student', 'Offering', 'Sponsor', 'Fees_offer', 'Student_class', 'Term', 'Year')


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('url', 'Id', 'Receipt_number', 'Amount_paid', 'Receipt_date', 'Student', 'Session', 'Date_created',
                  'Last_modified')


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('url', 'Id', 'Uce', 'Uace', 'Mock', 'Student', 'Session', 'Receipt')


class TextBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBooks
        fields = ('url', 'Id', 'Name', 'Role', 'Cost', 'Student', 'Session', 'Receipt')


class OthersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Others
        fields = (
            'url', 'Id', 'Identity_card', 'Passport_photos', 'Hair_cutting', 'Library', 'Medical', 'Scouts', 'Student',
            'Session', 'Receipt')


class MiscSerializer(serializers.ModelSerializer):
    class Meta:
        model = Misc
        fields = ('url', 'Id', 'Role', 'Cost', 'Student', 'Session', 'Receipt')


class UniformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uniform
        fields = (
            'url', 'Id', 'Class_wear', 'Sports_wear', 'Casual_wear', 'Sweater', 'Jogging', 'School_t_shirt', 'Badge',
            'Student', 'Session', 'Receipt')


class TermClassAdditionalFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermClassAdditionalFees
        fields = ('url', 'Id', 'Class1', 'Class2', 'Class3', 'Class4', 'Class5', 'Class6', 'Is_Boarding')


class ComputerPayableFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerPayableFees
        fields = (
            'url', 'Id', 'Fees', 'IsClass1_applicable', 'IsClass2_applicable', 'IsClass3_applicable',
            'IsClass4_applicable',
            'IsClass5_applicable', 'IsClass6_applicable')


class TermPayableFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermPayableFees
        fields = (
            'url', 'Id', 'Global', 'Boarding', 'Uce', 'Uace', 'Mock', 'Sciences', 'Arts', 'Admission', 'Development',
            'TermClassAdditionalFees', 'ComputerPayableFees', 'Session')


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = (
            'url', 'Id', 'Name', 'Discount', 'Tuition', 'Boarding', 'Admission', 'Computer', 'Development_fee',
            'Class_wear', 'Sports_wear', 'Casual_wear', 'Sweater', 'Jogging', 'School_t_shirt', 'Badge',
            'Identity_card', 'Passport_photos', 'Hair_cutting', 'Library',
            'Medical', 'Scouts', 'Uce', 'Uace', 'Mock', 'AdditionalClass1Fees', 'AdditionalClass2Fees',
            'AdditionalClass3Fees', 'AdditionalClass4Fees', 'AdditionalClass5Fees', 'AdditionalClass6Fees',
            'BAdditionalClass1Fees', 'BAdditionalClass2Fees',
            'BAdditionalClass3Fees', 'BAdditionalClass4Fees', 'BAdditionalClass5Fees', 'BAdditionalClass6Fees',
            'Sciences', 'Arts'
        )


class SponsorReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorReceipt
        fields = (
            'url', 'Id', 'Payment', 'Sponsor', 'Session', 'Receipt_number', 'Receipt_date', 'Date_created',
            'Last_modified')


class BalanceForwardedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceForwarded
        fields = (
            'url', 'Id', 'Student', 'Tuition', 'Admission', 'Computer', 'Development_fee', 'Uce', 'Uace', 'Mock',
            'Session', 'Manual', 'Date_created', 'Last_modified')


class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = ('url', 'Id', 'Sandstorm', 'Product_description', 'Version')


class LicencedToSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicensedTo
        fields = ('url', 'Id', 'Name', 'Location', 'Address', 'Telephone', 'Email')
