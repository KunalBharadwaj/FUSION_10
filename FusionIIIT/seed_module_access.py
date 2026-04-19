import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

from applications.globals.models import ModuleAccess

HR_DESIGNATIONS = [
    "faculty",
    "staff",
    "Professor",
    "Assistant Professor",
    "Associate Professor",
    "Employee",
    "Dean Academic",
    "HOD",
    "Director",
    "Registrar",
    "HR Admin",
    "HR Administrator",
    "Accountant",
    "Finance",
    "acadadmin",
    "studentacadadmin",
]

for designation in HR_DESIGNATIONS:
    obj, created = ModuleAccess.objects.get_or_create(designation=designation)
    if not obj.hr:
        obj.hr = True
        obj.save()
        print(f"Granted HR access to: {designation}")
    else:
        print(f"HR access already set for: {designation}")

print("Done seeding ModuleAccess.")
