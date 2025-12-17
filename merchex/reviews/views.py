from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Ticket, Review
from .forms import TicketForm, ReviewForm
from itertools import chain
from accounts.models import UserFollows


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("home")  # plus tard tu pourras rediriger vers le feed
    else:
        form = TicketForm()
    return render(
        request, "reviews/ticket_form.html", {"form": form, "title": "Créer un ticket"}
    )


@login_required
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = TicketForm(instance=ticket)

    return render(
        request,
        "reviews/ticket_form.html",
        {"form": form, "title": "Modifier le ticket"},
    )


@login_required
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == "POST":
        ticket.delete()
        return redirect("home")

    return render(
        request,
        "reviews/ticket_confirm_delete.html",
        {
            "ticket": ticket,
        },
    )


@login_required
def review_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect("home")
    else:
        form = ReviewForm()

    return render(
        request,
        "reviews/review_form.html",
        {"form": form, "ticket": ticket, "title": "Créer une critique"},
    )


@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "reviews/review_form.html",
        {"form": form, "ticket": review.ticket, "title": "Modifier la critique"},
    )


@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        review.delete()
        return redirect("home")

    return render(
        request,
        "reviews/review_confirm_delete.html",
        {
            "review": review,
            "ticket": review.ticket,
            "title": "Supprimer la critique",
        },
    )


@login_required
def feed(request):
    user = request.user

    followed_users_ids = UserFollows.objects.filter(user=user).values_list(
        "followed_user_id", flat=True
    )

    # Tickets : mes tickets OU tickets des gens que je suis
    tickets = Ticket.objects.filter(Q(user=user) | Q(user__in=followed_users_ids))

    # Reviews : mes reviews OU reviews des gens que je suis OU reviews sur mes tickets
    reviews = Review.objects.filter(
        Q(user=user) | Q(user__in=followed_users_ids) | Q(ticket__user=user)
    ).distinct()  # ✅ ici c’est OK car pas de union()

    ticket_items = [
        {"type": "TICKET", "object": ticket, "time_created": ticket.time_created}
        for ticket in tickets
    ]
    review_items = [
        {"type": "REVIEW", "object": review, "time_created": review.time_created}
        for review in reviews
    ]

    feed_items = sorted(
        chain(ticket_items, review_items),
        key=lambda item: item["time_created"],
        reverse=True,
    )

    return render(request, "reviews/feed.html", {"feed_items": feed_items})
