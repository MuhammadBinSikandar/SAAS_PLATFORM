from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def profile_list_view(request):
    context = {
        "object_list": User.objects.filter(is_active=True)
    }
    return render(request, "profiles/list.html", context)

@login_required
def profile_view(request,username=None, *args, **kwargs):
    user = request.user
    profile_user_object = get_object_or_404(User, username=username)
    is_me = profile_user_object == user
    if is_me:
        if user.has_perm("visits.view_pagevisit"):
            pass
    return HttpResponse(f"Hello {username} - {profile_user_object.id} - {user.id} - {is_me}")

@login_required
def profile_detail_view(request,username=None, *args, **kwargs):
    user = request.user
    print(
        user.has_perm("subscriptions.basic"),
        user.has_perm("subscriptions.basic_ai"),
        user.has_perm("subscriptions.standard"),
        user.has_perm("subscriptions.pro"),
    )
    # user_groups = user.groups.all()
    # print("User groups:", user_groups)
    # if user_groups.filter(name__icontains="Plan").exists():
    #     return HttpResponse("Congratulations! You have a basic account.")
    profile_user_object = get_object_or_404(User, username=username)
    is_me = profile_user_object == user
    context = {
        "object" : profile_user_object,
        "owner" : is_me,
        # "user_groups" : user_groups,
        "instance" : profile_user_object
    }
    return render(request, "profiles/detail.html", context)