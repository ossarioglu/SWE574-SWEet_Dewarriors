from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DeleteView, ListView, DetailView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .forms import UserMessageModelForm
from .models import UserMessage, UserInbox

# Create your views here.
class SendMessageView(LoginRequiredMixin, CreateView):
    form_class = UserMessageModelForm
    model = UserMessage
    template_name = 'usermessages/send_message.html'

    def form_valid(self, form):
        if self.request.POST.get('child_id'):
            child_msg = UserMessage.objects.get(id=self.request.POST.get('child_id'))
        else:
            child_msg = None

        to_list = form.cleaned_data.get('to')
        form.instance.message_from = self.request.user.profile
        form.instance.child = child_msg
        form.instance.save()
        form.instance.message_to.add(*to_list)

        msg = form.save()
        # add this UserMessage object to all included users' UserInbox
        included_users = to_list.copy()
        included_users.append(self.request.user.profile)
        for u in included_users:
            inbox = UserInbox.objects.get(owner=u)
            inbox.content.add(msg)

        return super().form_valid(form)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('child_id'):
            context['child'] = UserMessage.objects.get(id=self.request.GET.get('child_id'))
        return context
    
    def get_success_url(self):
        return reverse('usermessages.main')


class UserMessageReadUpdateView(LoginRequiredMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('id')
        obj = UserMessage.objects.get(id=id_)
        obj.is_read_by.add(request.user.profile)
        obj.save()
        return JsonResponse({'update': 'done'}, status=200)

class UserMessagesMainView(LoginRequiredMixin, TemplateView):
    template_name = 'usermessages/messages_main.html'


class InboxView(LoginRequiredMixin, ListView):
    model = UserMessage
    template_name = 'usermessages/inbox.html'
    paginate_by = 5

    def get_queryset(self):
        # return UserMessage.objects.filter(message_to=self.request.user.profile).order_by('-sent_at')
        inbox = UserInbox.objects.get(owner=self.request.user.profile)
        inbox_content = inbox.content.all()
        return inbox_content.filter(message_to=self.request.user.profile).order_by('-sent_at')


class SentMessagesView(LoginRequiredMixin, ListView):
    model = UserMessage
    template_name = 'usermessages/sent_messages.html'
    paginate_by = 5

    def get_queryset(self):
        inbox = UserInbox.objects.get(owner=self.request.user.profile)
        inbox_content = inbox.content.all()
        # return UserMessage.objects.filter(message_from=self.request.user.profile).order_by('-sent_at')
        return inbox_content.filter(message_from=self.request.user.profile).order_by('-sent_at')

class DeletedMessagesView(LoginRequiredMixin, ListView):
    model = UserMessage
    template_name = 'usermessages/deleted_messages.html'
    paginate_by = 5

    def get_queryset(self):
        all_msgs = UserMessage.objects.filter(Q(message_to=self.request.user.profile) | Q(message_from=self.request.user.profile)).order_by('-sent_at')
        inbox = UserInbox.objects.get(owner=self.request.user.profile)
        deleted_msgs = [msg for msg in all_msgs if msg not in inbox.content.all()]
        return deleted_msgs


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = UserMessage
    template_name = 'usermessages/message_detail.html'

    def get_object(self):
        id_ = self.request.GET.get('id')
        return get_object_or_404(UserMessage, id=id_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('sent_messages'):
            context['sent_messages'] = True
        elif self.request.GET.get('deleted_messages'):
            context['deleted_messages'] = True
        obj = self.get_object()
        children = obj.get_all_children()
        context['children'] = children
        return context

# class MessageDeleteView(LoginRequiredMixin, DeleteView):
#     template_name = 'usermessages/message_delete.html'
#     model = UserMessage

#     def get(self, request, *args, **kwargs):
#         id_ = request.GET.get('id')
#         obj = UserMessage.objects.get(id=id_)
#         return render(request, self.template_name, {'object': obj})

#     def get_object(self):
#         id_ = self.request.POST.get('id')
#         return get_object_or_404(UserMessage, id=id_)

#     def get_success_url(self):
#         return reverse('usermessages.main')

class MessageDeleteView(LoginRequiredMixin, View):
    template_name = 'usermessages/message_delete.html'

    def get(self, request, *args, **kwargs):
        msg = UserMessage.objects.get(id=request.GET.get('id'))
        return render(request, self.template_name, {'object': msg})

    def post(self, request, *args, **kwargs):
        msg = UserMessage.objects.get(id=request.POST.get('id'))
        inbox = UserInbox.objects.get(owner=request.user.profile)
        inbox.content.remove(msg)
        return JsonResponse({'update': 'done'}, status=200)


class GetNumOfUnreadMailsAjaxView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        seen_msgs = request.user.profile.seen.all()
        all_msgs = request.user.profile.recipients.all()
        num_of_unread = len(all_msgs) - len(seen_msgs)
        return JsonResponse({'num_of_unread': num_of_unread}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class RestoreDeletedMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        obj = UserMessage.objects.get(id=request.POST.get('id'))
        inbox = UserInbox.objects.get(owner=request.user.profile)
        inbox.content.add(obj)
        return JsonResponse({'restore': 'done'}, status=200)