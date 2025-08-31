from django.urls import path
from accounts.views import ProfileDetailView, ProfileEditView


urlpatterns = [
    path("me/",      ProfileDetailView.as_view(), name="me"),
    path("me/edit/", ProfileEditView.as_view(),   name="edit"),
]