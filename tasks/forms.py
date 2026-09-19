from django import forms
from .models import Task, Note, SubTask

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'priority', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter task title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 4, 'placeholder': 'Describe the task...'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select mb-3'}),
            'priority': forms.Select(attrs={'class': 'form-select mb-3'}),
            'category': forms.Select(attrs={'class': 'form-select mb-3'}),
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