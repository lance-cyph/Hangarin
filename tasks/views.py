from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Task, Category, STATUS_CHOICES, SubTask, Note
from .forms import TaskForm, NoteForm, SubTaskForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages

@login_required
def task_list(request):
    # Only fetch tasks belonging to the logged-in user
    tasks = Task.objects.filter(user=request.user).select_related('category', 'priority').prefetch_related('subtask_set', 'note_set').order_by('deadline')
    
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


@login_required
def task_detail(request, pk):
    # Ensure they can only view their own task
    task = get_object_or_404(Task, pk=pk, user=request.user)
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


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Pause save to assign the logged-in user
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    # Ensure they can only edit their own task
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task})


@login_required
def complete_task(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.status = "Completed"
        task.save()
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


@login_required
def undo_complete_task(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.status = "Pending"
        task.save()
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


@login_required
def task_delete(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.delete()
    return redirect('task_list')


@login_required
def note_delete(request, pk):
    if request.method == 'POST':
        # Ensure the note belongs to a task owned by the user
        note = get_object_or_404(Note, pk=pk, task__user=request.user)
        task_pk = note.task.pk
        note.delete()
        return redirect('task_detail', pk=task_pk)
    return redirect('task_list')


@login_required
def subtask_delete(request, pk):
    if request.method == 'POST':
        # Ensure the subtask belongs to a task owned by the user
        subtask = get_object_or_404(SubTask, pk=pk, parent_task__user=request.user)
        task_pk = subtask.parent_task.pk  
        subtask.delete()
        return redirect('task_detail', pk=task_pk)
    return redirect('task_list')


@login_required
def toggle_subtask(request, pk):
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, pk=pk, parent_task__user=request.user)
        
        subtask.is_completed = not subtask.is_completed
        subtask.save()
        
        return redirect('task_detail', pk=subtask.parent_task.pk)
        
    return redirect('task_list')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('task_list')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        remember = request.POST.get('rememberMe')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            return redirect('task_list')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
            
    return render(request, 'tasks/login.html')