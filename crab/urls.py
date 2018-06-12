"""crab URL Configuration
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from app import views
from app.auth import auth_mobile_admin, register, check_username
from crab import settings

router = DefaultRouter()
router.register(r'about', views.AboutViewSet)
router.register(r'license', views.LicensedToViewSet)
router.register(r'student', views.StudentViewSet)
router.register(r'tuition', views.TuitionViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'terms', views.TermRegViewSet)
router.register(r'receipts', views.ReceiptViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'textbooks', views.TextBooksViewSet)
router.register(r'others', views.OthersViewSet)
router.register(r'uniforms', views.UniformViewSet)
router.register(r'misc', views.MiscViewSet)
router.register(r'term_class_additional_fees', views.TermClassAdditionalFeesViewSet)
router.register(r'computer', views.ComputerPayableFeesViewSet)
router.register(r'term_payable_fees', views.TermPayableFeesViewSet)
router.register(r'sponsor', views.SponsorViewSet)
router.register(r'sponsor_receipts', views.SponsorReceiptViewSet)
router.register(r'bal_forwarded', views.BalanceForwardedViewSet,)
router.register(r'bf_original', views.BalanceForwardedUpdateViewSet, base_name='BalanceForwardedUpdateViewSet')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^get_admission/(?P<pk>[0-9]+)/$', views.TuitionViewSet.as_view({'get': 'get_admission'})),
    url(r'^get_tuition_balance/(?P<pk>[0-9]+)/$', views.get_tuition_balance),
    url(r'^export_payments/', views.get_payments_export_data, name='get_payments_export_data'),
    url(r'^export_balances/', views.get_balances_export_data, name='get_balances_export_data'),
    url(r'^student_number/', views.generate_student_number, name='generate_student_number'),
    url(r'^recent_session/', views.SessionViewSet.as_view({'get': 'get_recent_session'})),
    url(r'^student_last_reg/(?P<student>[0-9]+)/$', views.TermRegViewSet.as_view({'get': 'get_student_previous_reg'})),
    url(r'^payable_tuition/(?P<pk>[0-9]+)/$', views.get_student_payable_tuition, name='get_student_payable_tuition'),
    url(r'^dump_exams/(?P<pk>[0-9]+)/$', views.ExamViewSet.as_view({'get': 'dump_payments'})),
    url(r'^switch_sessions/$', views.switch_sessions, name='switch_sessions'),
    url(r'^forward_reg/(?P<student_id>[0-9]+)/$', views.forward_registration, name='fw_reg'),
    url(r'clean', views.clean, name='clean'),
    url(r'^auth$', auth_mobile_admin, name='auth'),
    url(r'^register$', register, name='register'),
    url(r'^check_username', check_username, name='check_username'),
    url(r'^search', views.search_all_view, name='search_all_view'),
    url(r'^student_bf/(?P<student_id>[0-9]+)/$', views.get_student_bf, name='student_bf')
]
