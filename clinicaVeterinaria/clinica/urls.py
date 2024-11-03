from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('custom_admin/', views.custom_admin, name='custom_admin'),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("registerClient/", views.registerClient, name="registerClient"),
    path("registerVet/", views.registerVet, name="registerVet"),
    path("calendar/", views.calendar, name="calendar"),
    path("addEvent/", views.addEvent, name="addEvent"),
    path("editEvent/", views.editEvent, name="editEvent"),
    path("deleteEvent/", views.deleteEvent, name="deleteEvent"),
    path("myPets/", views.myPets, name="myPets"),
    path("addPet/", views.addPet, name="addPet"),
    path('deletePet/<int:id>/', views.deletePet, name='deletePet'),
    path("profile/", views.profile, name="profile"),
    path("editProfile/", views.editProfile, name="editProfile"),
    path("changePassword/", views.changePassword, name="changePassword"),
    path("myAppointments/", views.myAppointments, name="myAppointments"),
    path("myRequests/", views.myRequests, name="myRequests"),
    path("acceptRequest/<int:id>/", views.acceptRequest, name="acceptRequest"),
    path("rejectRequest/", views.rejectRequest, name="rejectRequest"),
    path("historialMedico/<int:id>", views.historialMedico, name="historialMedico"),
    path("modificarHistorial/", views.modificarHistorial, name="modificarHistorial"),
]
