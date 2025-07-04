# Scheduler App

This Django app provides an admin interface for controlling Celery scheduled tasks. It allows you to create, edit, and delete scheduled tasks through the Django admin interface, without having to restart the Celery beat process.

## Features

- Create, edit, and delete scheduled tasks through the Django admin interface
- Support for both interval-based and crontab-based schedules
- Enable/disable tasks without deleting them
- Track when tasks were last run and how many times they've run

## Installation

1. Add `'scheduler'` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    # ...
    'scheduler',
    # ...
]
```

2. Run migrations to create the scheduler models:

```bash
python manage.py migrate scheduler
```

3. Initialize the scheduler with default tasks:

```bash
python manage.py init_scheduler
```

4. Configure Celery to use the database scheduler:

```python
# In your celery.py file
app.conf.beat_scheduler = 'scheduler.scheduler.DatabaseScheduler'
```

## Usage

1. Go to the Django admin interface
2. Navigate to the "Scheduler" section
3. Click on "Scheduled Tasks"
4. Create, edit, or delete tasks as needed

### Creating a New Task

1. Click "Add Scheduled Task"
2. Enter a name for the task
3. Select the task to run from the dropdown
4. Choose the schedule type (interval or crontab)
5. Fill in the schedule details
6. Click "Save"

### Editing a Task

1. Click on the task name in the list
2. Edit the task details
3. Click "Save"

### Disabling a Task

1. Click on the task name in the list
2. Uncheck the "Enabled" checkbox
3. Click "Save"

## Schedule Types

### Interval

An interval schedule runs the task at a fixed interval. You can specify the interval in days, hours, minutes, and seconds.

### Crontab

A crontab schedule runs the task according to a crontab expression. You can specify the minute, hour, day of week, day of month, and month of year.

## Task Status

The admin interface shows the following information for each task:

- **Last Run At**: When the task was last run
- **Total Run Count**: How many times the task has run
- **Date Created**: When the task was created
- **Date Changed**: When the task was last modified