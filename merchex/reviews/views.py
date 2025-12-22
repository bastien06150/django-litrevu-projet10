from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


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
        request, "reviews/ticket_form.html", {"form": form, "title": "Créer un billet"}
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
        {"form": form, "title": "Modifier le billet"},
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

    # --------------------
    # TICKETS (union)
    # --------------------
    tickets_own = Ticket.objects.filter(user=user)
    tickets_followed = Ticket.objects.filter(user__in=followed_users_ids)
    tickets = tickets_own.union(tickets_followed)

    # --------------------
    # REVIEWS (union)
    # --------------------
    reviews_own = Review.objects.filter(user=user)
    reviews_followed = Review.objects.filter(user__in=followed_users_ids)
    reviews_on_my_tickets = Review.objects.filter(ticket__user=user)

    reviews = reviews_own.union(
        reviews_followed,
        reviews_on_my_tickets,
    )

    # --------------------
    # REGROUPEMENT reviews par ticket
    # --------------------
    reviews_by_ticket_id = {}
    for review in reviews:
        reviews_by_ticket_id.setdefault(review.ticket_id, []).append(review)

    # --------------------
    # Création des groupes (ticket + reviews)
    # --------------------
    feed_groups = []
    for ticket in tickets:
        ticket_reviews = reviews_by_ticket_id.get(ticket.id, [])

        # Trier les reviews du ticket (la plus récente en premier)
        ticket_reviews.sort(key=lambda r: r.time_created, reverse=True)

        latest_review = ticket_reviews[0] if ticket_reviews else None

        # Date d’activité : si une review existe, on prend la plus récente
        activity_time = ticket.time_created
        if latest_review and latest_review.time_created > activity_time:
            activity_time = latest_review.time_created

        feed_groups.append(
            {
                "ticket": ticket,
                "reviews": ticket_reviews,  # toutes les reviews visibles liées à ce ticket
                "latest_review": latest_review,  # la plus récente
                "activity_time": activity_time,  # sert au tri du flux
            }
        )

    # Trier les tickets selon l’activité (plus récent d’abord)
    feed_groups.sort(key=lambda g: g["activity_time"], reverse=True)

    return render(
        request,
        "reviews/feed.html",
        {"feed_groups": feed_groups},
    )
