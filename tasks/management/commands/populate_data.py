from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, Category, SubTask, Note, Priority

class Command(BaseCommand):
    help = 'Populates the Hangarin database with sample tasks, categories, subtasks, and notes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating data... Please wait.")

        # 1. Create Default Categories
        cat_school, _ = Category.objects.get_or_create(name="School")
        cat_work, _ = Category.objects.get_or_create(name="Work")
        cat_personal, _ = Category.objects.get_or_create(name="Personal")
        cat_health, _ = Category.objects.get_or_create(name="Health")

        # 2. Create Default Priorities
        high_pri, _ = Priority.objects.get_or_create(name="High")
        med_pri, _ = Priority.objects.get_or_create(name="Medium")
        low_pri, _ = Priority.objects.get_or_create(name="Low")

        # 3. Create Sample Task 1 (School Project)
        task1, created1 = Task.objects.get_or_create(
            title="Application Development Laboratory",
            defaults={
                'description': 'Midterm laboratory project for App Dev. Needs to be responsive and use Bootstrap 5 components.',
                'deadline': timezone.now() + timedelta(days=5),
                'status': 'In Progress',
                'category': cat_school,
                'priority': high_pri,  # Fixed: Priority added directly into defaults
            }
        )
        if created1:
            # Add Subtasks and Notes
            SubTask.objects.create(parent_task=task1, title="Setup Django environment", is_completed=True)
            SubTask.objects.create(parent_task=task1, title="Create models and apply migrations", is_completed=True)
            SubTask.objects.create(parent_task=task1, title="Build custom Bootstrap 5 delete modals", is_completed=False)
            SubTask.objects.create(parent_task=task1, title="Write populate_data script", is_completed=False)
            
            Note.objects.create(task=task1, content="Don't forget to double-check that the minus (-) symbol for deleting subtasks looks clean!")
            Note.objects.create(task=task1, content="Make sure to test the toggle logic on the server.")

        # 4. Create Sample Task 2 (Personal Errands)
        task2, created2 = Task.objects.get_or_create(
            title="Weekly Groceries & Meal Prep",
            defaults={
                'description': 'Stock up the fridge for the week and prepare lunches.',
                'deadline': timezone.now() + timedelta(days=1),
                'status': 'Pending',
                'category': cat_personal,
                'priority': med_pri,  # Fixed: Priority added directly into defaults
            }
        )
        if created2:
            # Add Subtasks
            SubTask.objects.create(parent_task=task2, title="Buy milk, eggs, and bread", is_completed=False)
            SubTask.objects.create(parent_task=task2, title="Get fresh vegetables", is_completed=False)
            SubTask.objects.create(parent_task=task2, title="Cook chicken and rice for Monday", is_completed=False)

        # Output Success Message:)
        self.stdout.write(self.style.SUCCESS("Successfully populated database with sample data!"))