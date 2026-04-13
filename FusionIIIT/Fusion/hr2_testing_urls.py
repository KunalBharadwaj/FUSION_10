from django.urls import include, path

urlpatterns = [
    path("hr2/api/", include("applications.hr2.api.urls")),
]
