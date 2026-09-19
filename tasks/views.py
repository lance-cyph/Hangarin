from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Task, Category, STATUS_CHOICES
from .forms import TaskForm, NoteForm

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
        current_category_id = int(category_filter)

    # 6. Pass everything, including current selections, to the template
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
    
    # Process the new note if the user submits the form
    if request.method == 'POST':
        note_form = NoteForm(request.POST)
        if note_form.is_valid():
            new_note = note_form.save(commit=False) # Pause saving
            new_note.task = task # Link the note to this specific task
            new_note.save() # Now save to the database
            return redirect('task_detail', pk=task.pk) # Refresh the page
    else:
        note_form = NoteForm() # Show an empty form

    context = {
        'task': task,
        'subtasks': task.subtask_set.all(),
        'notes': task.note_set.all().order_by('-created_at'),
        'note_form': note_form,
    }
    return render(request, 'tasks/task_detail.html', context)


def task_create(request):
    # Process the new task if the form is submitted
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form})


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        # instance=task tells Django to update the existing record
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        # Pre-fill the form with the existing task data
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task})


def complete_task(request, pk):
    # Ensure this is a secure POST request before modifying the database
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.status = "Completed"
        task.save()
    
    # Redirect the user back to whatever page they clicked the button from
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


def task_delete(request, pk):
    # Secure POST-only delete to prevent accidental deletions via URL
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        task.delete()
    return redirect('task_list')

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        # instance=task tells Django to update the existing record, not create a new one
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        # Pre-fill the form with the existing task data
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task})

def note_delete(request, pk):
    # Secure POST-only delete to prevent accidental deletions via URL
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=pk)
        task_pk = note.task.pk  # Save parent task ID so we know where to redirect
        note.delete()
        # Redirect back to the specific task's detail page
        return redirect('task_detail', pk=task_pk)
    
    return redirect('task_list') # Fallback if someone tries to access via GET