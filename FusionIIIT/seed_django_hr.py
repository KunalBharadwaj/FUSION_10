import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

from django.contrib.auth.models import User
from applications.globals.models import ExtraInfo, DepartmentInfo, Designation, HoldsDesignation
from applications.hr2.models import Employee, Constants
import datetime

def seed():
    # Departments
    dept_cse, _ = DepartmentInfo.objects.get_or_create(name="Computer Science and Engineering")
    dept_admin, _ = DepartmentInfo.objects.get_or_create(name="Administration")
    dept_finance, _ = DepartmentInfo.objects.get_or_create(name="Finance")
    dept_director, _ = DepartmentInfo.objects.get_or_create(name="Director Office")

    # Designations
    desig_employee, _ = Designation.objects.get_or_create(name="Employee")
    desig_hod, _ = Designation.objects.get_or_create(name="HOD")
    desig_director, _ = Designation.objects.get_or_create(name="Director")
    desig_registrar, _ = Designation.objects.get_or_create(name="Registrar")
    desig_hradmin, _ = Designation.objects.get_or_create(name="HR Admin")
    desig_accountant, _ = Designation.objects.get_or_create(name="Accountant")

    users_data = [
        {
            "emp_id": "EMP1003", "username": "director1003", "password": "director123",
            "name": "Dr. Meena Verma", "email": "director@iiitdmj.ac.in",
            "dept": dept_director, "desig_obj": desig_director, "desig_str": "Director",
            "user_type": "faculty", "emp_type": Constants.EmployeeType.FACULTY
        },
        {
            "emp_id": "EMP1002", "username": "hod1002", "password": "hod123",
            "name": "Dr. Anil Kumar", "email": "anil.kumar@iiitdmj.ac.in",
            "dept": dept_cse, "desig_obj": desig_hod, "desig_str": "Professor and HOD",
            "user_type": "faculty", "emp_type": Constants.EmployeeType.FACULTY
        },
        {
            "emp_id": "EMP1004", "username": "registrar1004", "password": "registrar123",
            "name": "Suresh Verma", "email": "registrar@iiitdmj.ac.in",
            "dept": dept_admin, "desig_obj": desig_registrar, "desig_str": "Registrar",
            "user_type": "staff", "emp_type": Constants.EmployeeType.STAFF
        },
        {
            "emp_id": "EMP1005", "username": "hradmin1005", "password": "hradmin123",
            "name": "Priya Nair", "email": "hr.admin@iiitdmj.ac.in",
            "dept": dept_admin, "desig_obj": desig_hradmin, "desig_str": "HR Administrator",
            "user_type": "staff", "emp_type": Constants.EmployeeType.STAFF
        },
        {
            "emp_id": "EMP1006", "username": "accountant1006", "password": "accountant123",
            "name": "Arun Joshi", "email": "accountant@iiitdmj.ac.in",
            "dept": dept_finance, "desig_obj": desig_accountant, "desig_str": "Accountant",
            "user_type": "staff", "emp_type": Constants.EmployeeType.STAFF
        },
        {
            "emp_id": "EMP1001", "username": "rahul1001", "password": "rahul123",
            "name": "Rahul Sharma", "email": "rahul.sharma@iiitdmj.ac.in",
            "dept": dept_cse, "desig_obj": desig_employee, "desig_str": "Assistant Professor",
            "user_type": "faculty", "emp_type": Constants.EmployeeType.FACULTY
        }
    ]

    for data in users_data:
        try:
            # Create User
            user = User.objects.filter(username=data["username"]).first()
            if not user:
                user = User.objects.create_user(
                    username=data["username"],
                    password=data["password"],
                    email=data["email"],
                    first_name=data["name"].split()[0],
                    last_name=" ".join(data["name"].split()[1:])
                )
            else:
                user.set_password(data["password"])
                user.save()

            # Create ExtraInfo
            extra, created = ExtraInfo.objects.get_or_create(
                user=user,
                defaults={
                    "id": data["emp_id"],
                    "user_type": data["user_type"],
                    "department": data["dept"],
                    "sex": "M" if "Dr." not in data["name"] else "F", # Rough guess
                    "title": "Dr." if "Dr." in data["name"] else "Mr.",
                }
            )

            # Assign HoldsDesignation
            HoldsDesignation.objects.get_or_create(
                user=user,
                working=user,
                designation=data["desig_obj"]
            )

            # Create Employee
            if not Employee.objects.filter(extra_info=extra).exists():
                Employee.objects.create(
                    extra_info=extra,
                    employee_type=data["emp_type"],
                    designation=data["desig_str"],
                    category=Constants.Category.GENERAL,
                    blood_group=Constants.BloodGroup.O_POS
                )
            print(f"Successfully seeded {data['username']}")
        except Exception as e:
            print(f"Error seeding {data['username']}: {e}")

if __name__ == '__main__':
    seed()
