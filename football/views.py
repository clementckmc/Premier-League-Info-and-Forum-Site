from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Thread, Reply, ThreadForm, ReplyForm
from django.db.models import Max

import os
import requests
import json
import html2text
from dotenv import load_dotenv
load_dotenv()  # loads the configs from .env

url_teams = "http://api.football-data.org/v4/competitions/PL/teams"
url_standings = "http://api.football-data.org/v4/competitions/PL/standings"

headers = {
    'X-Auth-Token': str(os.getenv('FOOTBALL_KEY'))
}

response_teams = requests.request("GET", url_teams, headers=headers)
response_standings = requests.request("GET", url_standings, headers=headers)
current_matchday = response_standings.json()["season"]["currentMatchday"]
current_season_tmp = response_standings.json()["filters"]["season"]
current_season = current_season_tmp + "-" + str(int(current_season_tmp) + 1)

PLteams = {}
for team in response_teams.json()["teams"]:
    PLteams[team["id"]] = {
    "name": team["name"],
    "shortName": team["shortName"],
    "crestUrl": team["crest"],
    "tla": team["tla"]
    }


def index(request):
    table = response_standings.json()["standings"][0]["table"]
    first = table[0]["team"]["name"]
    return render(request, "football/index.html", {
        "teams": response_teams.json()["teams"],
        "current_matchday": str(current_matchday),
        "first": first,
        "current_season": current_season
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "football/login.html", {
                "message": "Invalid username and/or password.",
                "teams": response_teams.json()["teams"],
                "current_matchday": str(current_matchday)
            })
    else:
        return render(request, "football/login.html", {
            "teams": response_teams.json()["teams"],
            "current_matchday": str(current_matchday)
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "football/register.html", {
                "message": "Passwords must match.",
                "teams": response_teams.json()["teams"],
                "current_matchday": str(current_matchday)
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "football/register.html", {
                "message": "Username already taken.",
                "teams": response_teams.json()["teams"],
                "current_matchday": str(current_matchday)
            })
        login(request, user)

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "football/register.html", {
            "teams": response_teams.json()["teams"],
            "current_matchday": str(current_matchday)
        })

# get upvote for threads
def get_upvote_t(id):
    voted = []
    vote_id = Thread.upvote.through.objects.filter(user_id=id).values('thread_id')
    for vote in vote_id:
        voted.append(vote['thread_id'])
    return voted

# get downvote for threads
def get_downvote_t(id):
    voted = []
    vote_id = Thread.downvote.through.objects.filter(user_id=id).values('thread_id')
    for vote in vote_id:
        voted.append(vote['thread_id'])
    return voted

# get upvote for replies
def get_upvote_r(id):
    voted = []
    vote_id = Reply.upvote.through.objects.filter(user_id=id).values('reply_id')
    for vote in vote_id:
        voted.append(vote['reply_id'])
    return voted

# get downvote for replies
def get_downvote_r(id):
    voted = []
    vote_id = Reply.downvote.through.objects.filter(user_id=id).values('reply_id')
    for vote in vote_id:
        voted.append(vote['reply_id'])
    return voted


@login_required
@csrf_exempt
def vote_post(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        vote = json_data['ud'] # up or down vote?
        tr = json_data['tr'] # thread or reply?

        # create vote objects and response
        if tr == "t": # for threads
            if vote == "u":
                add_upvote = Thread.upvote.through.objects.create(thread_id=json_data['vote_id'], user_id=request.user.id)
                add_upvote.save()
                vote_count = Thread.upvote.through.objects.filter(thread_id=json_data['vote_id']).count()
            else:
                add_downvote = Thread.downvote.through.objects.create(thread_id=json_data['vote_id'], user_id=request.user.id)
                add_downvote.save()
                vote_count = Thread.downvote.through.objects.filter(thread_id=json_data['vote_id']).count()
        else: # for replies
            if vote == "u":
                add_upvote = Reply.upvote.through.objects.create(reply_id=json_data['vote_id'], user_id=request.user.id)
                add_upvote.save()
                vote_count = Reply.upvote.through.objects.filter(reply_id=json_data['vote_id']).count()
            else:
                add_downvote = Reply.downvote.through.objects.create(reply_id=json_data['vote_id'], user_id=request.user.id)
                add_downvote.save()
                vote_count = Reply.downvote.through.objects.filter(reply_id=json_data['vote_id']).count()

        return JsonResponse({"vote": vote, "vote_count": vote_count, "status": 201})
    return JsonResponse({}, status=400)


def teamInfo(request, tla):
    teams = response_teams.json()["teams"]
    selected_team = next((team for team in teams if team['tla'] == tla), None)

    url_matches = "http://api.football-data.org/v2/teams/"+ str(selected_team["id"]) + "/matches" + "?status=FINISHED"
    response_matches = requests.request("GET", url_matches, headers=headers)

    table = response_standings.json()["standings"][0]["table"]
    pos = next((pos for pos in table if pos['team']["id"] == selected_team["id"]), None)

    return render(request, "football/teamInfo.html", {
        "teams": teams,
        "team": selected_team,
        "tla": tla,
        "current_matchday": str(current_matchday),
        "previous": response_matches.json()["matches"][-1],
        "pos": pos
    })

def table(request):
    return render(request, "football/table.html", {
        "table": response_standings.json()["standings"][0]["table"],
        "teams": response_teams.json()["teams"],
        "current_matchday": str(current_matchday)
    })

def fixtures(request, matchday=str(current_matchday)):
    if request.method == "POST":
        selected_matchday = request.POST.get("selected_matchday")
        return redirect("fixtures", selected_matchday)

    else:
        url_fixtures = "http://api.football-data.org/v2/competitions/2021/matches?matchday=" + matchday
        response_fixtures = requests.request("GET", url_fixtures, headers=headers)
        matches = []
        for match in response_fixtures.json()["matches"]:
            homeCrest = PLteams[match["homeTeam"]["id"]]["crestUrl"]
            awayCrest = PLteams[match["awayTeam"]["id"]]["crestUrl"]
            home = PLteams[match["homeTeam"]["id"]]["shortName"]
            away = PLteams[match["awayTeam"]["id"]]["shortName"]
            if match["status"] == "FINISHED" or match["status"] == "IN_PLAY" or match["status"] == "PAUSED":
                matches.append({
                    "homeCrest": homeCrest,
                    "home": home,
                    "score": str(match["score"]["fullTime"]["homeTeam"]) + " - " + str(match["score"]["fullTime"]["awayTeam"]),
                    "awayCrest": awayCrest,
                    "away": away,
                    "matchID": match["id"],
                    "status": match["status"]
                })
            elif match["status"] == "POSTPONED":
                matches.append({
                    "homeCrest": homeCrest,
                    "home": home,
                    "score": "P - P",
                    "awayCrest": awayCrest,
                    "away": away,
                    "matchID": match["id"],
                    "status": match["status"]
                })
            elif match["status"] == "SCHEDULED":
                matches.append({
                    "homeCrest": homeCrest,
                    "home": home,
                    "score": "-",
                    "awayCrest": awayCrest,
                    "away": away,
                    "matchID": match["id"],
                    "status": match["status"]
                })

    return render(request, "football/fixtures.html", {
        "fixtures": matches,
        "teams": response_teams.json()["teams"],
        "PLteams": PLteams,
        "numberMD": list(range(1, 39)),
        "MD": matchday,
        "current_matchday": str(current_matchday),
        "current_int": current_matchday
    })

@login_required
def forum(request):
    teams = response_teams.json()["teams"]

    # thread count for teams' forum
    for team in teams:
        team["count"] = Thread.objects.filter(forum=team["tla"]).count() # add thread count to teams

    # thread count for general discussion
    gen_count = Thread.objects.filter(forum="GEN").count()

    return render(request, "football/forum.html", {
        "teams": teams,
        "current_matchday": str(current_matchday),
        "gen_count": gen_count
    })

@login_required
def teamForum(request, tla="general"):
    teams = response_teams.json()["teams"]
    selected_team = next((team for team in teams if team['tla'] == tla), None)
    if tla != "general":
        threads = Thread.objects.filter(forum=tla).annotate(Max("reply__time"), Max("time")).order_by('-reply__time__max', '-time__max')
    else:
        threads = Thread.objects.filter(forum="GEN").annotate(Max("reply__time"), Max("time")).order_by('-reply__time__max', '-time__max')
    return render(request, "football/teamForum.html", {
        "teams": response_teams.json()["teams"],
        "current_matchday": str(current_matchday),
        "selected_team": selected_team,
        "threads": threads
    })

@login_required
def newPost(request, tla="general"):
    teams = response_teams.json()["teams"]
    selected_team = next((team for team in teams if team['tla'] == tla), None)

    if request.method == "POST":
        form = ThreadForm(request.POST)

        if form.is_valid():
            newthread = form.save(commit=False)
            newthread.content = newthread.content.replace('\n', '<br>')
            newthread.content = html2text.html2text(newthread.content) # turn html into text to store in database
            newthread.op = User.objects.get(pk=request.user.id)
            newthread.forum = tla
            newthread.slug = slugify(newthread.topic)
            newthread.save()
            return HttpResponseRedirect(reverse("teamForum", args=(tla,)))
    else:
        form = ThreadForm()

    return render(request, "football/newPost.html", {
        "teams": response_teams.json()["teams"],
        "current_matchday": str(current_matchday),
        "tla": tla,
        "form": form,
        "selected_team": selected_team
    })

@login_required
def thread(request, slug):
    selected_thread = Thread.objects.get(slug=slug)
    replies = Reply.objects.filter(thread_id=selected_thread.id)

    # Paginator
    p = Paginator(replies, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    if request.method == "POST":
        form = ReplyForm(request.POST)

        if form.is_valid():
            newReply = form.save(commit=False)
            newReply.content = newReply.content.replace('\n', '<br>')
            newReply.content = html2text.html2text(newReply.content) # turn html into text to store in database
            newReply.poster = User.objects.get(pk=request.user.id)
            newReply.thread = selected_thread
            newReply.save()
            return HttpResponseRedirect(reverse("thread", args=(slug,)))
    else:
        form = ReplyForm()

    teams = response_teams.json()["teams"]
    selected_team = next((team for team in teams if team['tla'] == selected_thread.forum), None)

    upvote_t = get_upvote_t(request.user.id)
    downvote_t = get_downvote_t(request.user.id)

    upvote_r = get_upvote_r(request.user.id)
    downvote_r = get_downvote_r(request.user.id)

    return render(request, "football/thread.html", {
        "teams": teams,
        "current_matchday": str(current_matchday),
        "thread": selected_thread,
        "replies": page_obj,
        "form": form,
        "slug": slug,
        "selected_team": selected_team,
        "upvote_t": upvote_t,
        "downvote_t": downvote_t,
        "upvote_r": upvote_r,
        "downvote_r": downvote_r
    })

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
