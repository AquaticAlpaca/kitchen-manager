# Kitchen Manager - Knowledge Base Document

**Last Updated:** 2026-09-29

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Locations](#file-locations)
3. [Database Models](#database-models)
4. [URL Patterns](#url-patterns)
5. [Django Settings Summary](#django-settings-summary)
6. [Project Structure Tree](#project-structure-tree)
7. [Running Commands](#running-commands)

---
## Project Overview

| Property | Value |
|----------|-------|
| **Project Name** | `kitchen_management` |
| **Framework** | Django 6.1.1 |
| **Database** | SQLite3 (`db.sqlite3`) |
| **Source Code Location** | `kitchen_management/` |


---
## File Locations Quick Reference

| Resource | Path | Description |
|----------|------|-------------|
| Database | `kitchen-management/db.sqlite3` | SQLite database |
| Main Settings | `kitchen_management/settings.py` | Django configuration |
| URL Patterns | `kitchen_management/urls.py` | Root URLs |
| Pantry Models | `kitchen_management/pantry/models.py` | PantryItem, PantryImage models |

---
## Database Models

### PantryItem Model (lines 3-12)

| Field | Type | Default | Max Length |
|-------|------|---------|------------|
| `name` | CharField | - | 256 |
| `category` | CharField | - | 100 |
| `quantity` | DecimalField | - | unlimited |
| `unit` | CharField | - | 50 |
| `added_date` | DateTimeField | auto_now_add | - |

### PantryImage Model (lines 14-20)

| Field | Type | Description |
|-------|------|-------------|
| `item` | ForeignKey | Reference to PantryItem |
| `file` | FileField | upload_to="pantry_images/" |

---
## URL Patterns

### ROOT_URLCONF Setting (settings.py line 57)
ROOT_URLCONF = 'kitchen_management.urls'

### URL Configuration (urls.py lines 20-22)
urlpatterns = [
    path("admin/", admin.site.urls),
]

---
## Django Settings Summary

| Setting | Value |
|---------|-------|
| DEBUG | True |
| DATABASE_ENGINE | django.db.backends.sqlite3 |
| DB_PATH | `./kitchen_management/db.sqlite3` |

### Installed Apps (settings.py lines 33-45)
INSTALLED_APPS = [
    "django.contrib.admin",
    "pantry",           # Pantry app
    "meal_plans",      # Meal plans app
    "shopping_list",   # Shopping list app
]

---
## Project Structure Tree

/Users/psquared/Code/kitchen-manager/
 ├──docs/
 ├──.venv/
 ├──README.MD
 ├──ARCHITECTURE.md
 ├──CONTRIBUTING.md
 ├──GLOSSARY.md
 ├──SECURITY.md
 ├──kitchen_management/
 │  ├──kitchen_management/
 │  │  ├──urls.py (ROOT_URLCONF)
 │  │  ├──settings.py
 │  ├──pantry/models.py (PantryItem, PantryImage)
 │  ├──db.sqlite3

---
## Running Commands
Change to the kithen_management/ directory before running these commands:

| Command | Purpose |
|---------|--------|
| python manage.py runserver | Start dev server |
| python manage.py migrate | Apply migrations |
| python manage.py shell | Django shell |
| python manage.py test | Run Django tests |

---
## Quick Reference

### How to find URL patterns:
1. Check ROOT_URLCONF in settings.py (line 57)
2. View: kitchen_management/urls.py
3. Admin URLs at /admin/

### How to find models:
1. Check INSTALLED_APPS in settings.py (lines 33-45)
2. Models are at <app>/models.py
3. Example: PantryItem = kitchen_management/pantry/models.py

---
*Document created for AI assistant reference.*
