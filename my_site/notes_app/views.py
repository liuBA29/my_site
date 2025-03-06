# notes_app/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Note
from .forms import NoteForm


def main_page(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'notes/index.html')


class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'

class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

class NoteCreateView(CreateView):
    model = Note
    template_name = 'notes/note_form.html'
    form_class = NoteForm

    def form_valid(self, form):
        # После того как форма валидирована, мы можем редиректить на страницу заметки
        new_note = form.save()
        return redirect(new_note.get_absolute_url())

class NoteUpdateView(UpdateView):
    model = Note
    template_name = 'notes/note_form.html'
    form_class = NoteForm

    def form_valid(self, form):
        # После того как форма валидирована, мы сохраняем изменения
        updated_note = form.save()
        return redirect(updated_note.get_absolute_url())

class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('note_list')


