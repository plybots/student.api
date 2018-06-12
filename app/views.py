from __future__ import print_function

import datetime
import json
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from app.models import Student, Tuition, Session, TermRegistration, Receipt, Exam, TextBooks, Others, Uniform, Misc, \
    TermClassAdditionalFees, ComputerPayableFees, TermPayableFees, Sponsor, SponsorReceipt, BalanceForwarded, About, \
    LicensedTo
from app.serializers import StudentSerializer, TuitionSerializer, SessionSerializer, \
    TermRegSerializer, ReceiptSerializer, ExamSerializer, TextBooksSerializer, OthersSerializer, UniformSerializer, \
    MiscSerializer, TermClassAdditionalFeesSerializer, ComputerPayableFeesSerializer, TermPayableFeesSerializer, \
    SponsorSerializer, SponsorReceiptSerializer, BalanceForwardedSerializer, AboutSerializer, LicencedToSerializer


def __active_session__():
    try:
        return Session.objects.filter(Is_active=True)[0]
    except IndexError:
        return None


def __get_term_payable_fees(session_id):
    term_fees = TermPayableFees.objects.get(Session_id=session_id)
    return term_fees


@csrf_exempt
def switch_sessions(request):
    if request.method == 'POST':
        session = json.loads(request.body)
        active_session = __active_session__()
        active_session.Is_active = False
        active_session.save()

        _session_to_activate = Session.objects.filter(Term=session["Term"], Year=session["Year"]).first()
        _session_to_activate.Is_active = True
        _session_to_activate.save()

        serializer = SessionSerializer(_session_to_activate, context={'request': request})
        json_result = JSONRenderer().render(serializer.data)

        response = HttpResponse(
            json_result,
            content_type="application/json"
        )
        return response


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def list(self, request, *args, **kwargs):
        queryset = Student.objects.all()
        for student in queryset:
            session = __active_session__()
            try:
                term_reg = TermRegistration.objects.get(Student=student.Id, Year=session.Year, Term=session.Term)
                if term_reg.Sponsor:
                    sponsor = get_object_or_404(Sponsor, pk=term_reg.Sponsor_id)
                    student.SponsorName = sponsor.Name
                else:
                    student.SponsorName = "NOT REGISTERED"
                student.Offering = term_reg.Offering
            except ObjectDoesNotExist:
                student.Offering = "NOT REGISTERED"
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Student.objects.all()
        _class = self.request.query_params.get('class', None)

        if _class is not None:
            session = __active_session__()
            term_reg = TermRegistration.objects.filter(Student_class=_class, Year=session.Year, Term=session.Term)
            queryset = Student.objects.filter(Id__in=term_reg.values("Student"))
        return queryset


@csrf_exempt
def search_all_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        name = body.get("Student_name")
        number = body.get("Student_no")
        _class = body.get("Student_class")
        subjects = body.get("Subjects")
        sponsor = body.get("Sponsor")
        offering = body.get("Offering")
        result = Student.objects.all()
        if _class is not None:
            try:
                _class = int(_class)
            except (TypeError, ValueError):
                _class = 0
        if number is not None:
            try:
                number = int(number)
            except (TypeError, ValueError):
                pass

        if name is not None:
            result = Student.objects.filter(Student_name__contains=name)
        if number > 0:
            result = result.filter(Student_no=number)
        if subjects is not None:
            result = result.filter(Subjects__contains=subjects)
        results = []
        for student in result:
            session = __active_session__()
            _sponsor = None
            _offering = None
            try:
                term_reg = TermRegistration.objects.get(Student=student.Id, Year=session.Year, Term=session.Term)
                if term_reg.Sponsor:
                    _sponsor = get_object_or_404(Sponsor, pk=term_reg.Sponsor_id)
                    student.SponsorName = _sponsor.Name
                else:
                    student.SponsorName = "NOT REGISTERED"
                student.Offering = term_reg.Offering
            except ObjectDoesNotExist:
                term_reg = None
                student.Offering = "NOT REGISTERED"
            if term_reg is not None:
                student.Student_class = term_reg.Student_class
                c, s, o = False, False, False
                if 0 < _class == int(term_reg.Student_class) and (student not in results):
                    c = True
                    results.append(student)
                if sponsor is not None and _sponsor is not None and _sponsor.Name == sponsor and student not in results:
                    s = True
                    results.append(student)
                if offering is not None and _offering is not None and _offering == offering and student not in results:
                    o = True
                    results.append(student)
                if not c and not s and not o:
                    results.append(student)
            elif name is not None or number != 0:
                results.append(student)

        serializer = StudentSerializer(results, many=True)
        json_result = JSONRenderer().render(serializer.data)
        return HttpResponse(json_result, content_type="application/json")


class TuitionViewSet(viewsets.ModelViewSet):
    queryset = Tuition.objects.all()
    serializer_class = TuitionSerializer

    def get_queryset(self):
        queryset = Tuition.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = Tuition.objects.filter(Student=student, Session=__active_session__().Id)
        if receipt is not None:
            queryset = Tuition.objects.filter(Receipt=receipt)
        return queryset

    @staticmethod
    def get_admission(request, pk=None):
        queryset = Tuition.objects.filter(Student=pk)
        total_admission = 0
        for tuition in queryset:
            total_admission += tuition.Admission
        json_result = JSONRenderer().render(total_admission)
        response = HttpResponse(
            json_result,
            content_type="application/json"
        )
        return response


def get_tuition_balance(request, pk=None):
    queryset = Tuition.objects.filter(Student=pk)
    student = get_object_or_404(Student, pk=pk)

    try:
        term_fees = __get_term_payable_fees(__active_session__().Id)
        offer = TermRegistration.objects.get(Student=student.Id, Term=__active_session__().Term,
                                             Year=__active_session__().Year)
        day_add_fees = get_class_additional_fees(offer.Student_class, False, term_fees)
        boarding_add_fees = get_class_additional_fees(offer.Student_class, True, term_fees)

        total_paid_tuition = 0
        for tuition in queryset:
            total_paid_tuition += tuition.Tuition

        sponsor = get_object_or_404(Sponsor, pk=student.Sponsor)

        if offer.Offering == 'BOARDING':
            balance = (total_paid_tuition + sponsor.Tuition + offer.Fees_offer + sponsor.Boarding) - (
                    term_fees.Global + day_add_fees + term_fees.Boarding + boarding_add_fees)
        else:
            balance = (total_paid_tuition + sponsor.Tuition + offer.Fees_offer) - (term_fees.Global + day_add_fees)
    except (IndexError, ObjectDoesNotExist):
        balance = -1

    json_result = JSONRenderer().render(balance)
    response = HttpResponse(
        json_result,
        content_type="application/json"
    )
    return response


def get_class_additional_fees(class_name, key, term_fees):
    try:
        additional_fees = []
        for ad in term_fees.TermClassAdditionalFees.all():
            additional_fees.append(ad.Id)
        if key:
            add_fees = TermClassAdditionalFees.objects.filter(Is_Boarding=True, Id__in=additional_fees).first()
        else:
            add_fees = TermClassAdditionalFees.objects.filter(Is_Boarding=False, Id__in=additional_fees).first()

        if class_name == 1:
            return add_fees.Class1
        if class_name == 2:
            return add_fees.Class2
        if class_name == 3:
            return add_fees.Class3
        if class_name == 4:
            return add_fees.Class4
        if class_name == 5:
            return add_fees.Class5
        if class_name == 6:
            return add_fees.Class6
        return 0
    except IndexError:
        return 0


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def get_queryset(self):
        queryset = Session.objects.all()
        term = self.request.query_params.get('term', None)
        year = self.request.query_params.get('year', None)
        current = self.request.query_params.get('now', None)
        if term is not None and year is not None:
            queryset = Session.objects.filter(Term=term, Year=year)

        if current == 'true':
            queryset = Session.objects.filter(Is_active=True)

        if current == 'false':
            queryset = Session.objects.filter(Is_active=False)
        return queryset

    @staticmethod
    def get_recent_session(request):
        session = Session.objects.latest('End')
        serializer = SessionSerializer(session, many=False, context={'request': request})
        json_result = JSONRenderer().render(serializer.data)

        response = HttpResponse(
            json_result,
            content_type="application/json"
        )
        return response


class TermRegViewSet(viewsets.ModelViewSet):
    queryset = TermRegistration.objects.all()
    serializer_class = TermRegSerializer

    def create(self, request, *args, **kwargs):
        request_body = json.loads(request.body)
        student = Student.objects.get(Id=request_body["Student"])
        request.data['Sponsor'] = student.Sponsor
        request.data['Student_class'] = student.Student_class
        request.data['Fees_offer'] = student.Fees_offer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = TermRegistration.objects.all()
        student = self.request.query_params.get('student', None)
        student_term = self.request.query_params.get('stud_term', None)
        if student is not None:
            queryset = TermRegistration.objects.filter(Student=student, Year=__active_session__().Year,
                                                       Term=__active_session__().Term)
        if student_term is not None:
            queryset = TermRegistration.objects.filter(Student=student_term)
        return queryset

    @staticmethod
    def get_student_previous_reg(request, student=None):
        serializer = TermRegSerializer(__student_last_reg__(student), many=False, context={'request': request})
        json_result = JSONRenderer().render(serializer.data)

        response = HttpResponse(
            json_result,
            content_type="application/json"
        )
        return response


def __student_last_reg__(student):
    recent_session = get_next_session(__active_session__(), reverse=True)
    print(recent_session)
    try:
        session = Session.objects.get(Id=recent_session.Id)
        term_reg = TermRegistration.objects.get(Student_id=student, Term=session.Term, Year=session.Year)
    except (AttributeError, ObjectDoesNotExist):
        term_reg = None

    return term_reg


def get_next_session(session, reverse=None):
    year_sessions = Session.objects.filter(Year=session.Year)
    next_session = None
    if len(year_sessions) > 1:
        try:
            if reverse:
                next_session = Session.objects.get(Year=session.Year, Term=session.Term - 1)
            else:
                next_session = Session.objects.get(Year=session.Year, Term=session.Term + 1)
        except ObjectDoesNotExist:
            if reverse:
                highest_term = 0
                n = Session.objects.filter(Year=session.Year - 1)
                if n.count() > 1:
                    for x in n:
                        if highest_term < x.Term:
                            highest_term = x.Term
                    next_session = Session.objects.get(Year=session.Year - 1, Term=highest_term)
                elif n.count() == 1:
                    next_session = Session.objects.get(Year=session.Year - 1, Term=n[0].Term)
            else:
                next_session = Session.objects.get(Year=session.Year + 1, Term=1)
    elif len(year_sessions) == 1:
        if reverse:
            highest_term = 0
            n = Session.objects.filter(Year=session.Year - 1)
            if n.count() > 1:
                for x in n:
                    if highest_term < x.Term:
                        highest_term = x.Term
                next_session = Session.objects.get(Year=session.Year - 1, Term=highest_term)
            elif n.count() == 1:
                next_session = Session.objects.get(Year=session.Year - 1, Term=n[0].Term)
        else:
            next_session = None

    return next_session


def get_earliest_session():
    return Session.objects.filter(Term=1).earliest("Year")


def __all_tuition_balances__(student_id, session_id=None):
    tut, adm, com, dev = 0, 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    session = Session.objects.get(Id=session_id)
    try:
        reg = TermRegistration.objects.get(Student_id=student_id, Year=session.Year, Term=session.Term)
        tuition_paid = Tuition.objects.filter(Student_id=student_id, Session=session)
        sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)
        payable_tuition = __student_payable_tuition__(student_id, session=session)
        term_fees = __get_term_payable_fees(session_id)
        if len(tuition_paid) > 0:
            for tuition in tuition_paid:
                tut += tuition.Tuition
                adm += tuition.Admission
                com += tuition.Computer
                dev += tuition.Development_fee
        return OrderedDict(Tuition=tut - payable_tuition,
                           Admission=(adm + sponsor.Admission) - term_fees.Admission,
                           Development_fee=(dev + sponsor.Development_fee) - term_fees.Development,
                           Computer=(com + sponsor.Computer) - term_fees.ComputerPayableFees.Fees,
                           Session=session_id, Student=student_id, Date_created=date_created)
    except ObjectDoesNotExist:
        return OrderedDict(Tuition=tut, Admission=adm, Development_fee=dev, Computer=com,
                           Session=session_id, Student=student_id, Date_created=date_created)


def __all_exam_balances__(student_id, session_id=None):
    uce, uace, mock = 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    session = Session.objects.get(Id=session_id)
    try:
        reg = TermRegistration.objects.get(Student_id=student_id, Year=session.Year, Term=session.Term)

        exam_paid = Exam.objects.filter(Student=student_id, Session=session)
        sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)

        regs46, s46_uce, s46_uace, s46_mock = None, 0, 0, 0
        if reg.Student_class == 4:
            regs46 = TermRegistration.objects.filter(Student_id=student_id, Student_class=4)
        elif reg.Student_class == 6:
            regs46 = TermRegistration.objects.filter(Student_id=student_id, Student_class=6)
        if regs46 and (reg.Student_class == 4 or reg.Student_class == 6):
            for reg46 in regs46:
                ses46 = Session.objects.get(Term=reg46.Term, Year=reg46.Year)
                tms46 = __get_term_payable_fees(ses46.Id)
                if reg.Student_class == 4:
                    s46_uce += tms46.Uce
                elif reg.Student_class == 6:
                    s46_uace += tms46.Uace
                s46_mock += tms46.Mock

        if len(exam_paid) > 0:
            for exam in exam_paid:
                uce += exam.Uce
                uace += exam.Uace
                mock += exam.Mock

        if reg.Student_class == 4:
            return OrderedDict(Uce=(uce + sponsor.Uce) - s46_uce, Uace=s46_uace,
                               Mock=(mock + sponsor.Mock) - s46_mock, Session=session_id,
                               Student=student_id, Date_created=date_created)

        elif reg.Student_class == 6:
            return OrderedDict(Uce=s46_uce, Uace=(uace + sponsor.Uace) - s46_uace,
                               Mock=(mock + sponsor.Mock) - s46_mock, Session=session_id,
                               Student=student_id, Date_created=date_created)
        else:
            return OrderedDict(Uce=uce, Uace=uace, Mock=mock, Session=session_id,
                               Student=student_id, Date_created=date_created)
    except ObjectDoesNotExist:
        return OrderedDict(Uce=uce, Uace=uace, Mock=mock, Session=session_id,
                           Student=student_id, Date_created=date_created)


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        queryset = Receipt.objects.all()
        student = self.request.query_params.get('student', None)
        if student is not None:
            queryset = Receipt.objects.filter(Student=student, Session=__active_session__().Id)
        return queryset


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def get_queryset(self):
        queryset = Exam.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = Exam.objects.filter(Student=student)
        if receipt is not None:
            queryset = Exam.objects.filter(Receipt=receipt)
        return queryset

    @staticmethod
    def dump_payments(request, pk=None):
        queryset = Exam.objects.filter(Student=pk)
        for exam in queryset:
            cost = exam.Uace + exam.Uce + exam.Mock
            misc = Misc(Role="exam_dump", Cost=cost, Student=exam.Student, Receipt=exam.Receipt, Session=exam.Session)
            misc.save()
            exam.delete()
        return HttpResponse(
            json.dumps({'status': True, 'msg': 'Success'}))


class TextBooksViewSet(viewsets.ModelViewSet):
    queryset = TextBooks.objects.all()
    serializer_class = TextBooksSerializer

    def get_queryset(self):
        queryset = TextBooks.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = TextBooks.objects.filter(Student=student, Session=__active_session__().Id)
        if receipt is not None:
            queryset = TextBooks.objects.filter(Receipt=receipt)
        return queryset


class OthersViewSet(viewsets.ModelViewSet):
    queryset = Others.objects.all()
    serializer_class = OthersSerializer

    def get_queryset(self):
        queryset = Others.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = Others.objects.filter(Student=student, Session=__active_session__().Id)
        if receipt is not None:
            queryset = Others.objects.filter(Receipt=receipt)
        return queryset


class MiscViewSet(viewsets.ModelViewSet):
    queryset = Misc.objects.all()
    serializer_class = MiscSerializer

    def get_queryset(self):
        queryset = Misc.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = Misc.objects.filter(Student=student, Session=__active_session__().Id)
        if receipt is not None:
            queryset = Misc.objects.filter(Receipt=receipt)
        return queryset


class UniformViewSet(viewsets.ModelViewSet):
    queryset = Uniform.objects.all()
    serializer_class = UniformSerializer

    def get_queryset(self):
        queryset = Uniform.objects.all()
        student = self.request.query_params.get('student', None)
        receipt = self.request.query_params.get('receipt', None)
        if student is not None:
            queryset = Uniform.objects.filter(Student=student, Session=__active_session__().Id)
        if receipt is not None:
            queryset = Uniform.objects.filter(Receipt=receipt)
        return queryset


class TermClassAdditionalFeesViewSet(viewsets.ModelViewSet):
    queryset = TermClassAdditionalFees.objects.all()
    serializer_class = TermClassAdditionalFeesSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        offering = self.request.query_params.get('offering', None)
        term_fees = self.request.query_params.get('term_fees', None)
        if offering is not None and term_fees is not None:
            tm = TermPayableFees.objects.get(Id=term_fees)
            if offering == "true" or offering == "True":
                for ad in tm.TermClassAdditionalFees.all():
                    if ad.Is_Boarding:
                        return TermClassAdditionalFees.objects.filter(Id=ad.Id)
            else:
                for ad in tm.TermClassAdditionalFees.all():
                    if not ad.Is_Boarding:
                        return TermClassAdditionalFees.objects.filter(Id=ad.Id)
            return queryset.none()
        return queryset


class ComputerPayableFeesViewSet(viewsets.ModelViewSet):
    queryset = ComputerPayableFees.objects.all()
    serializer_class = ComputerPayableFeesSerializer


class TermPayableFeesViewSet(viewsets.ModelViewSet):
    queryset = TermPayableFees.objects.all()
    serializer_class = TermPayableFeesSerializer

    def get_queryset(self):
        queryset = self.queryset
        session = self.request.query_params.get('session', None)
        if session is not None:
            queryset = queryset.filter(Session=session)
        return queryset


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer


@csrf_exempt
def get_payments_export_data(request):
    response_data = []
    if request.method == 'POST':
        student_list = json.loads(request.body)
        active_session = __active_session__()
        for student in student_list:
            try:
                reg = TermRegistration.objects.get(Student_id=student['Id'], Year=active_session.Year,
                                                   Term=active_session.Term)
                student_id = student['Id']
                data_list = []
                _student = OrderedDict(Id=student_id, Student_no=student['Student_no'],
                                       Student_name=student['Student_name'], Student_class=reg.Student_class,
                                       Subjects=student['Subjects'], Sponsor=reg.Sponsor_id,
                                       Fees_offer=reg.Fees_offer, Date_created=student['Date_created'],
                                       Last_created=student['Last_modified'])
                data_list.append(_student)
                tuition = get_tuition_totals(Tuition.objects.filter(Student=student_id, Session=active_session.Id),
                                             student_id, active_session.Id, reg)
                data_list.append(tuition)
                exam = get_exam_totals(Exam.objects.filter(Student=student_id),
                                       student_id, active_session.Id, reg)
                data_list.append(exam)
                response_data.append(data_list)
            except ObjectDoesNotExist:
                pass
    response = HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
    return response


def get_tuition_totals(queryset, student_id, session_id, reg):
    tut, adm, com, dev = 0, 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)
    if len(queryset) > 0:
        for tuition in queryset:
            tut += tuition.Tuition
            adm += tuition.Admission
            com += tuition.Computer
            dev += tuition.Development_fee

    return OrderedDict(Tuition=tut + sponsor.Tuition, Admission=adm + sponsor.Admission,
                       Development_fee=dev + sponsor.Development_fee, Computer=com + sponsor.Computer,
                       Session=session_id, Student=student_id, Date_created=date_created)


def get_uniform_totals(queryset, student_id, session_id, reg):
    cw, sw, caw, swe, jog, ts, ba = 0, 0, 0, 0, 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)
    if len(queryset) > 0:
        for uniform in queryset:
            cw += uniform.Class_wear
            sw += uniform.Sports_wear
            caw += uniform.Casual_wear
            swe += uniform.Sweater
            jog += uniform.Jogging
            ts += uniform.School_t_shirt
            ba += uniform.Badge

    return OrderedDict(Class_wear=cw + sponsor.Class_wear, Sports_wear=sw + sponsor.Sports_wear,
                       Casual_wear=caw + sponsor.Casual_wear,
                       Sweater=swe + sponsor.Sweater, Jogging=jog + sponsor.Jogging,
                       School_t_shirt=ts + sponsor.School_t_shirt,
                       Badge=ba + sponsor.Badge, Session=session_id, Student=student_id, Date_created=date_created)


def get_others_totals(queryset, student_id, session_id, reg):
    id, pp, hr, lib, med, sc = 0, 0, 0, 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")

    student = get_object_or_404(Student, pk=student_id)
    sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)

    if len(queryset) > 0:
        for others in queryset:
            id += others.Identity_card
            pp += others.Passport_photos
            hr += others.Hair_cutting
            lib += others.Library
            med += others.Medical
            sc += others.Scouts

    return OrderedDict(Identity_card=id + sponsor.Identity_card, Passport_photos=pp + sponsor.Passport_photos,
                       Hair_cutting=hr + sponsor.Hair_cutting, Library=lib + sponsor.Library,
                       Scouts=sc + sponsor.Scouts,
                       Session=session_id, Student=student_id, Date_created=date_created)


def get_misc_totals(queryset, student_id, session_id):
    roles = ""
    cost = 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    if len(queryset) > 0:
        for misc in queryset:
            roles += misc.Role
            cost += misc.Cost

    return OrderedDict(Role=roles, Cost=cost, Session=session_id, Student=student_id,
                       Date_created=date_created)


def get_textbooks_totals(queryset, student_id, session_id):
    nm, rol = "", ""
    cost = 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")

    if len(queryset) > 0:
        for textbooks in queryset:
            nm += textbooks.Name
            rol += textbooks.Role
            cost += textbooks.Cost

    return OrderedDict(Name=nm, Role=rol, Cost=cost, Session=session_id, Student=student_id,
                       Date_created=date_created)


def get_exam_totals(queryset, student_id, session_id, reg):
    uce, uace, mock = 0, 0, 0
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")
    sponsor = get_object_or_404(Sponsor, pk=reg.Sponsor_id)
    if len(queryset) > 0:
        for exam in queryset:
            uce += exam.Uce
            uace += exam.Uace
            mock += exam.Mock

    return OrderedDict(Uce=uce + sponsor.Uce, Uace=uace + sponsor.Uace, Mock=mock + sponsor.Mock, Session=session_id,
                       Student=student_id, Date_created=date_created)


@csrf_exempt
def get_balances_export_data(request):
    response_data = []
    if request.method == 'POST':
        student_list = json.loads(request.body)
        active_session = __active_session__()
        for student in student_list:
            student_id = student['Id']
            try:
                reg = TermRegistration.objects.get(Student_id=student_id, Year=active_session.Year,
                                                   Term=active_session.Term)
                data_list = []
                _student = OrderedDict(Id=student_id, Student_no=student['Student_no'],
                                       Student_name=student['Student_name'], Student_class=reg.Student_class,
                                       Subjects=student['Subjects'], Sponsor=reg.Sponsor_id,
                                       Fees_offer=reg.Fees_offer, Date_created=student['Date_created'],
                                       Last_created=student['Last_modified'])
                data_list.append(_student)
                tuition = __all_tuition_balances__(student_id, session_id=active_session.Id)
                data_list.append(tuition)
                exam = __all_exam_balances__(student_id, session_id=active_session.Id)
                data_list.append(exam)
                try:
                    balance_forwarded = __get_student_bf(student_id)
                    data_list.append(OrderedDict(Id=balance_forwarded.Id, Tuition=balance_forwarded.Tuition,
                                                 Admission=balance_forwarded.Admission,
                                                 Computer=balance_forwarded.Computer, Student=student_id,
                                                 Development_fee=balance_forwarded.Development_fee,
                                                 Uce=balance_forwarded.Uce, Uace=balance_forwarded.Uace,
                                                 Mock=balance_forwarded.Mock, Session=active_session.Id))
                except ObjectDoesNotExist:
                    data_list.append(
                        OrderedDict(Id=0, Tuition=0, Admission=0, Computer=0, Student=student_id, Development_fee=0,
                                    Uce=0, Uace=0, Mock=0, Session=active_session.Id))
                response_data.append(data_list)
            except ObjectDoesNotExist:
                pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def generate_student_number(request):
    latest = Student.objects.all().order_by('Id').last()

    if latest is not None:
        new_number = latest.Student_no + 1
    else:
        new_number = datetime.datetime.now().strftime("%Y") + "0001"
    response = HttpResponse(
        json.dumps(new_number),
        content_type="application/json"
    )
    return response


def get_student_payable_tuition(request, pk=None):
    total_tuition = -1
    if request.method == 'GET':
        total_tuition = __student_payable_tuition__(pk)

    response = HttpResponse(
        json.dumps(total_tuition),
        content_type="application/json"
    )
    return response


def get_sponsor_additional_fees(_class, sponsor_id, key):
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    if _class == 1:
        if key:
            return sponsor.BAdditionalClass1Fees
        else:
            return sponsor.AdditionalClass1Fees
    if _class == 2:
        if key:
            return sponsor.BAdditionalClass2Fees
        else:
            return sponsor.AdditionalClass2Fees
    if _class == 3:
        if key:
            return sponsor.BAdditionalClass3Fees
        else:
            return sponsor.AdditionalClass3Fees
    if _class == 4:
        if key:
            return sponsor.BAdditionalClass4Fees
        else:
            return sponsor.AdditionalClass4Fees
    if _class == 5:
        if key:
            return sponsor.BAdditionalClass5Fees
        else:
            return sponsor.AdditionalClass5Fees
    if _class == 6:
        if key:
            return sponsor.BAdditionalClass6Fees
        else:
            return sponsor.AdditionalClass6Fees


def __student_payable_tuition__(pk, session=__active_session__()):
    total_tuition = 0
    student = get_object_or_404(Student, pk=pk)
    term_fees = __get_term_payable_fees(session.Id)
    offer = TermRegistration.objects.get(Student=student.Id, Term=session.Term, Year=session.Year)
    day_add_fees = get_class_additional_fees(offer.Student_class, False, term_fees)
    boarding_add_fees = get_class_additional_fees(offer.Student_class, True, term_fees)
    sponsor = get_object_or_404(Sponsor, pk=offer.Sponsor_id)
    sponsor_day_add_fees = get_sponsor_additional_fees(offer.Student_class, sponsor.Id, False)
    sponsor_boarding_add_fees = get_sponsor_additional_fees(offer.Student_class, sponsor.Id, True)
    total_tuition += (term_fees.Global - sponsor.Tuition)
    if offer is not None:
        if offer.Offering == 'BOARDING':
            total_tuition += (term_fees.Boarding + boarding_add_fees - (sponsor.Boarding + sponsor_boarding_add_fees))
    else:
        total_tuition += (term_fees.Boarding + boarding_add_fees - sponsor.Boarding)

    total_tuition += (day_add_fees - sponsor_day_add_fees)

    if student.Subjects == 'SCIENCES':
        total_tuition += (term_fees.Sciences - sponsor.Sciences)
    elif student.Subjects == 'ARTS':
        total_tuition += (term_fees.Arts - sponsor.Arts)

    total_tuition -= offer.Fees_offer
    total_tuition -= sponsor.Discount

    return total_tuition


class SponsorReceiptViewSet(viewsets.ModelViewSet):
    queryset = SponsorReceipt.objects.all()
    serializer_class = SponsorReceiptSerializer

    def get_queryset(self):
        queryset = SponsorReceipt.objects.all()
        sponsor = self.request.query_params.get('sponsor', None)
        if sponsor is not None:
            queryset = SponsorReceipt.objects.filter(Sponsor=sponsor, Session=__active_session__().Id)
        return queryset


def get_balance_forwarded(pk):
    return __get_student_bf(pk)


def get_admission_bal(student_id):
    regs = TermRegistration.objects.filter(Student_id=student_id)
    lowest_year = min([p for p in regs if p.Year], key=lambda x: x.Year)
    init = None
    i_reg = None
    for reg in regs.filter(Year=lowest_year.Year):
        if init is None:
            init = reg.Term
            i_reg = reg
        elif reg.Term < init:
            init = reg.Term
            i_reg = reg
    session = __active_session__()
    if init is not None:
        session = Session.objects.get(Term=i_reg.Term, Year=i_reg.Year)
    print(session.Id)
    bal = TermPayableFees.objects.get(Session_id=session.Id).Admission
    for t in Tuition.objects.filter(Student_id=student_id):
        bal -= t.Admission

    return bal


def __get_student_bf(student_id):
    tt, adm, cop, dev, uce, uace, mock = 0, 0, 0, 0, 0, 0, 0
    start_session = __active_session__()
    while 1:
        prev_session = get_next_session(start_session, reverse=True)
        start_session = prev_session
        if prev_session:
            bal = __all_tuition_balances__(student_id, session_id=prev_session.Id)
            exam_bal = __all_exam_balances__(student_id, session_id=prev_session.Id)
            try:
                bf = BalanceForwarded.objects.get(Student_id=student_id, Session__Id=prev_session.Id)
                tt += (bal['Tuition'] - bf.Tuition)
                adm += (bal['Admission'] - bf.Admission)
                cop += (bal['Computer'] - bf.Computer)
                dev += (bal['Development_fee'] - bf.Development_fee)
                uce += (exam_bal['Uce'] - bf.Uce)
                uace += (exam_bal['Uace'] - bf.Uace)
                mock += (exam_bal['Mock'] - bf.Mock)
            except ObjectDoesNotExist:
                tt += (bal['Tuition'])
                adm += (bal['Admission'])
                cop += (bal['Computer'])
                dev += (bal['Development_fee'])
                uce += (exam_bal['Uce'])
                uace += (exam_bal['Uace'])
                mock += (exam_bal['Mock'])
        else:
            break
    try:
        bf = BalanceForwarded.objects.get(Student_id=student_id, Session__Id=__active_session__().Id)
        tt = (-bf.Tuition + tt)
        adm = (-bf.Admission + adm)
        cop = (-bf.Computer + cop)
        dev = (-bf.Development_fee + dev)
        uce = (-bf.Uce + uce)
        uace = (-bf.Uace + uace)
        mock = (-bf.Mock + mock)
    except ObjectDoesNotExist:
        pass
    response_data = BalanceForwarded(Tuition=tt * -1, Admission=get_admission_bal(student_id), Computer=cop * -1, Development_fee=dev * -1,
                                     Uce=uce * -1, Uace=uace * -1, Mock=mock * -1, Student_id=student_id,
                                     Session_id=__active_session__().Id, Manual=False)
    return response_data


def get_student_bf(request, student_id=None):
    response_data = __get_student_bf(student_id)
    return HttpResponse(json.dumps(
        BalanceForwardedSerializer(response_data, many=False, context={'request': request}).data
    ), content_type="application/json")


class BalanceForwardedViewSet(viewsets.ModelViewSet):
    queryset = BalanceForwarded.objects.all()
    serializer_class = BalanceForwardedSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.__get_queryset__())
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        student_id = self.request.query_params.get('student', None)
        if student_id is not None:
            return get_balance_forwarded(student_id)
        else:
            return get_balance_forwarded(obj.Student)

    def get_queryset(self):
        all_data = BalanceForwarded.objects.all()
        queryset = []
        for balance_forwarded in all_data:
            queryset.append(get_balance_forwarded(balance_forwarded.Student))
        return queryset

    def __get_queryset__(self):
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        pass


class BalanceForwardedUpdateViewSet(viewsets.ModelViewSet):
    queryset = BalanceForwarded.objects.all()
    serializer_class = BalanceForwardedSerializer

    def get_object(self):

        student_id = self.request.query_params.get('student', None)
        if student_id is not None:
            return BalanceForwarded.objects.filter(Student=student_id, Session=__active_session__().Id).first()
        else:
            queryset = self.filter_queryset(self.get_queryset())

            # Perform the lookup filtering.
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(queryset, **filter_kwargs)

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)
            return obj

    def get_queryset(self):
        return BalanceForwarded.objects.filter(Session=__active_session__().Id)


class AboutViewSet(viewsets.ModelViewSet):
    queryset = About.objects.all()
    serializer_class = AboutSerializer


class LicensedToViewSet(viewsets.ModelViewSet):
    queryset = LicensedTo.objects.all()
    serializer_class = LicencedToSerializer


def clean(request):
    for term_reg in TermRegistration.objects.all():
        student = Student.objects.get(Id=term_reg.Student_id)
        term_reg.Fees_offer = student.Fees_offer
        term_reg.Student_class = student.Student_class
        term_reg.Sponsor_id = student.Sponsor
        term_reg.save()


def forward_registration(request, student_id):
    last_reg = __student_last_reg__(student_id)
    json_result = 0
    if last_reg:
        try:
            c_session = __active_session__()
            reg = TermRegistration.objects.get(Student_id=student_id, Term=c_session.Term, Year=c_session.Year)
        except ObjectDoesNotExist:
            n_class, n_term, n_year = None, None, None
            if last_reg.Term == 3:
                n_class = last_reg.Student_class + 1
                n_term = 1
                n_year = last_reg.Year + 1
            elif 0 < last_reg.Term < 3:
                n_term = last_reg.Term + 1
                n_class = last_reg.Student_class
                n_year = last_reg.Year
            if n_class <= 6:
                reg = TermRegistration(Student_id=student_id, Offering=last_reg.Offering, Sponsor=last_reg.Sponsor,
                                       Fees_offer=last_reg.Fees_offer, Year=n_year,
                                       Student_class=n_class, Term=n_term)
                reg.save()
                serializer = TermRegSerializer(reg, many=False, context={'request': request})
                json_result = JSONRenderer().render(serializer.data)
            else:
                json_result = 1
        return HttpResponse(json_result, content_type="application/json")
    else:
        return HttpResponse(json_result, content_type="application/json")
