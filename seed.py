"""One-off seed script.

Run after migrations are applied:

    python seed.py

Creates:
  - A super administrator account (email/password printed to the console)
  - A starter set of departments and programs matching the Flutter app's
    mock data, so the admin screens have something real to show immediately.
"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.academic import Department, Program
from app.models.user import User, UserRole

SUPER_ADMIN_EMAIL = "superadmin@example.edu"
SUPER_ADMIN_PASSWORD = "ChangeMe123!"


def seed():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first():
            db.add(
                User(
                    email=SUPER_ADMIN_EMAIL,
                    full_name="Grace Mwangi",
                    password_hash=hash_password(SUPER_ADMIN_PASSWORD),
                    role=UserRole.SUPER_ADMINISTRATOR,
                )
            )
            print(f"Created super admin: {SUPER_ADMIN_EMAIL} / {SUPER_ADMIN_PASSWORD}")
        else:
            print("Super admin already exists, skipping.")

        if db.query(Department).count() == 0:
            departments = [
                Department(name="School of Computing & Informatics", code="SCI", description="Computing, IT and informatics programs"),
                Department(name="School of Business", code="SOB", description="Business, commerce and management programs"),
                Department(name="School of Education", code="SOE", description="Teacher education programs"),
                Department(name="School of Law", code="SOL", description="Legal studies programs"),
            ]
            db.add_all(departments)
            db.flush()

            dept_by_code = {d.code: d for d in departments}
            programs = [
                Program(name="BSc. Computer Science", code="BCS", department_id=dept_by_code["SCI"].id, description="Undergraduate computer science degree"),
                Program(name="BSc. Information Technology", code="BIT", department_id=dept_by_code["SCI"].id, description="Undergraduate IT degree"),
                Program(name="Bachelor of Commerce", code="BCOM", department_id=dept_by_code["SOB"].id, description="Undergraduate commerce degree"),
                Program(name="Bachelor of Education", code="BED", department_id=dept_by_code["SOE"].id, description="Undergraduate education degree"),
                Program(name="Bachelor of Laws", code="LLB", department_id=dept_by_code["SOL"].id, description="Undergraduate law degree"),
            ]
            db.add_all(programs)
            print(f"Seeded {len(departments)} departments and {len(programs)} programs.")
        else:
            print("Departments already exist, skipping.")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
