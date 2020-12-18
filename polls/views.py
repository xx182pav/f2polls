import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .models import Choice, Poll, Vote

from .forms import PollForm, EditPollForm, ChoiceForm


# Create your views here.
@login_required
def polls_list(request):
    polls = Poll.objects.all()
    search_term = ''

    if 'text' in request.GET:
        polls = polls.order_by('text')

    if 'pub_date' in request.GET:
        polls = polls.order_by('-pub_date')

    if 'num_votes' in request.GET:
        polls = polls.annotate(Count('vote')).order_by('-vote__count')

    if 'search' in request.GET:
        search_term = request.GET['search']
        polls = polls.filter(text__icontains=search_term)

    paginator = Paginator(polls, 5)

    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    context = {'polls': polls, 'params': params, 'search_term': search_term}
    return render(request, 'polls/polls_list.html', context)


@login_required
def add_poll(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            new_poll = form.save(commit=False)
            new_poll.pub_date = datetime.datetime.now()
            new_poll.owner = request.user
            new_poll.save()
            new_choice1 = Choice(
                poll=new_poll,
                choice_text=form.cleaned_data['choice1']
            ).save()
            new_choice2 = Choice(
                poll=new_poll,
                choice_text=form.cleaned_data['choice2']
            ).save()
            new_choice3 = Choice(
                poll=new_poll,
                choice_text=form.cleaned_data['choice3']
            ).save()
            new_choice4 = Choice(
                poll=new_poll,
                choice_text=form.cleaned_data['choice4']
            ).save()
            messages.success(
                request,
                'Опрос был добавлен!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('polls:list')
    else:
        form = PollForm()
    context = {'form': form}
    return render(request, 'polls/add_poll.html', context)


@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.user != poll.owner:
        return redirect('/')

    if request.method == "POST":
        poll.delete()
        messages.success(
            request,
            'Опрос успешно удалён',
            extra_tags='alert alert-success alert-dismissible fade show'
        )
        return redirect('polls:list')

    return render(request, 'polls/delete_poll_confirm.html', {'poll': poll})


@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.user != poll.owner:
        return redirect('/')

    if request.method == "POST":
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Опрос изменён',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('polls:list')
    else:
        form = EditPollForm(instance=poll)

    return render(request, 'polls/edit_poll.html', {'form': form, 'poll': poll})


@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.user != poll.owner:
        return redirect('/')

    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request,
                'Добавлен вариант ответа',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('polls:list')
    else:
        form = ChoiceForm()
    return render(request, 'polls/add_choice.html', {'form': form})


@login_required
def edit_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    poll = get_object_or_404(Poll, id=choice.poll.id)
    if request.user != poll.owner:
        return redirect('/')

    if request.method == "POST":
        form = ChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Вариант успешно изменён',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('polls:list')
    else:
        form = ChoiceForm(instance=choice)
    return render(request, 'polls/add_choice.html', {'form': form, 'edit_mode': True, 'choice': choice})


@login_required
def delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    poll = get_object_or_404(Poll, id=choice.poll.id)
    if request.user != poll.owner:
        return redirect('/')

    if request.method == "POST":
        choice.delete()
        messages.success(
            request,
            'Вариант успешно удалён',
            extra_tags='alert alert-success alert-dismissible fade show'
        )
        return redirect('polls:list')

    return render(request, 'polls/delete_choice_confirm.html', {'choice': choice})


@login_required
def poll_detail(request, poll_id):
    
    poll = get_object_or_404(Poll, id=poll_id)
    user_can_vote = poll.user_can_vote(request.user)
    results = poll.get_results_dict()
    context = {'poll': poll, 'user_can_vote': user_can_vote, 'results': results}
    return render(request, 'polls/poll_detail.html', context)


@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.user_can_vote(request.user):
        messages.error(request, 'Извините, но вы уже голосовали')
        return redirect('polls:detail', poll_id=poll_id)

    choice_id = request.POST.get('choice')
    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        new_vote = Vote(user=request.user, poll=poll, choice=choice)
        new_vote.save()
    else:
        messages.error(request, 'Не выбран ни один из вариантов!')
        return redirect('polls:detail', poll_id=poll_id)
    return redirect('polls:detail', poll_id=poll_id)
