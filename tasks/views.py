from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Task, Category, STATUS_CHOICES
from .forms import TaskForm

def task_list(request):
    # 1. Fetch the base query (all tasks)
    tasks = Task.objects.select_related('category', 'priority').prefetch_related('subtask_set', 'note_set').order_by('deadline')
    
    # 2. Grab the requested filters from the URL (if they exist)
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    # 3. Apply the Search Bar filter (searches titles OR descriptions)
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # 4. Apply the Status dropdown filter
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # 5. Apply the Category dropdown filter
    current_category_id = None
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
        current_category_id = int(category_filter) # Convert to int so the HTML template can read it properly

    # 6. Pass everything, including the current selections, to the template
    context = {
        'tasks': tasks,
        'categories': Category.objects.all(),
        'statuses': [choice[0] for choice in STATUS_CHOICES],
        'current_search': search_query,
        'current_status': status_filter,
        'current_category': current_category_id,
    }
    return render(request, 'tasks/task_list.html', context)

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    context = {
        'task': task,
        'subtasks': task.subtask_set.all(),
        'notes': task.note_set.all().order_by('-created_at')
    }
    return render(request, 'tasks/task_detail.html', context)

def complete_task(request, pk):
    # Ensure this is a secure POST request before modifying the database
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.status = "Completed"
        task.save()
    
    # Redirect the user back to whatever page they clicked the button from
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))

from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'priority', 'status', 'deadline']
        # The widgets dictionary applies Bootstrap CSS classes so the form looks professional
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save() # Saves the new task to the database
            return redirect('task_list') # Sends user back to dashboard
    else:
        form = TaskForm() # Shows an empty form
    
    return render(request, 'tasks/task_form.html', {'form': form})

def task_delete(request, pk):
    # Secure POST-only delete to prevent accidental deletions via URL
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        task.delete()
    return redirect('task_list')