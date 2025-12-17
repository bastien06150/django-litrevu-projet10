from django.urls import path
from . import views


urlpatterns = [
    path("feed/", views.feed, name="feed"),
    # Tickets
    path("tickets/create/", views.ticket_create, name="ticket_create"),
    path("tickets/<int:ticket_id>/edit/", views.ticket_edit, name="ticket_edit"),
    path("tickets/<int:ticket_id>/delete/", views.ticket_delete, name="ticket_delete"),
    # Reviews
    path(
        "tickets/<int:ticket_id>/review/create/",
        views.review_create,
        name="review_create",
    ),
    path("reviews/<int:review_id>/edit/", views.review_edit, name="review_edit"),
    path("reviews/<int:review_id>/delete/", views.review_delete, name="review_delete"),
]
