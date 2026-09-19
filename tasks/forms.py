from django import forms
from .models import Task, Note, SubTask

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'priority', 'category']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Type your note here...'}),
        }

class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'New subtask...'}),
        }