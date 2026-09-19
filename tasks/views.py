from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Task, Category, STATUS_CHOICES, SubTask, Note
from .forms import TaskForm, NoteForm, SubTaskForm

def task_list(request):
    tasks = Task.objects.select_related('category', 'priority').prefetch_related('subtask_set', 'note_set').order_by('deadline')
    
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    current_category_id = None
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
        current_category_id = int(category_filter)

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
    note_form = NoteForm()
    subtask_form = SubTaskForm()
    
    if request.method == 'POST':
        if 'add_note' in request.POST:
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                new_note = note_form.save(commit=False)
                new_note.task = task
                new_note.save()
                return redirect('task_detail', pk=task.pk)
                
        elif 'add_subtask' in request.POST:
            subtask_form = SubTaskForm(request.POST)
            if subtask_form.is_valid():
                new_subtask = subtask_form.save(commit=False)
                # FIXED: Changed from new_subtask.task to new_subtask.parent_task
                new_subtask.parent_task = task 
                new_subtask.save()
                return redirect('task_detail', pk=task.pk)

    context = {
        'task': task,
        'subtasks': task.subtask_set.all(),
        'notes': task.note_set.all().order_by('-created_at'),
        'note_form': note_form,
        'subtask_form': subtask_form,
    }
    return render(request, 'tasks/task_detail.html', context)


def task_create(request):
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
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task})


def complete_task(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.status = "Completed"
        task.save()
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


def undo_complete_task(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.status = "Pending"
        task.save()
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


def task_delete(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        task.delete()
    return redirect('task_list')


def note_delete(request, pk):
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=pk)
        task_pk = note.task.pk
        note.delete()
        return redirect('task_detail', pk=task_pk)
    return redirect('task_list')


def subtask_delete(request, pk):
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, pk=pk)
        task_pk = subtask.parent_task.pk  
        subtask.delete()
        return redirect('task_detail', pk=task_pk)
    return redirect('task_list')


def toggle_subtask(request, pk):
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, pk=pk)
        subtask.completed = not subtask.is_completed
        subtask.save()
        return redirect('task_detail', pk=subtask.parent_task.pk)
    return redirect('task_list')