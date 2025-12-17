from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm, FollowUserForm
from .models import User, UserFollows
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def follows(request):
    if request.method == "POST":
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]

            try:
                user_to_follow = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "cet utilisateur n'existe pas.")
            else:
                if user_to_follow == request.user:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-meme.")
                elif UserFollows.objects.filter(
                    user=request.user, followed_user=user_to_follow
                ).exists():
                    messages.error(request, "Vous suivez déja cet utilisateur.")
                else:
                    UserFollows.objects.create(
                        user=request.user, followed_user=user_to_follow
                    )
                    messages.success(
                        request, f"Vous suivez maintenant {user_to_follow.username}."
                    )

    else:
        form = FollowUserForm()

    following = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    return render(
        request,
        "accounts/follows.html",
        {
            "form": form,
            "following": following,
            "followers": followers,
        },
    )


@login_required
def unfollow(request, follow_id):

    follow = get_object_or_404(
        UserFollows,
        id=follow_id,
        user=request.user,  # sécurité : je ne peux supprimer que MES suivis
    )

    if request.method == "POST":
        follow.delete()
        messages.success(request, "Vous ne suivez plus cet utilisateur.")
        return redirect("follows")

    return render(request, "accounts/unfollow_confirm.html", {"follow": follow})
