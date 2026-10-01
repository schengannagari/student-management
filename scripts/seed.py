"""Seed an admin user and (optionally) bulk-generate students for load testing.

python -m scripts.seed --admin-password 'S3cret!pass'
python -m scripts.seed --admin-password 'S3cret!pass' --students 200000
"""

import argparse
import random
import time
from datetime import date, timedelta

from sqlalchemy import insert, select, text

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Classroom, Student, User
from app.models.enums import Gender, Role

FIRST = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Ananya",
    "Diya",
    "Isha",
    "Kabir",
    "Meera",
    "Rohan",
    "Saanvi",
    "Arjun",
    "Priya",
    "Neha",
    "Rahul",
    "Sneha",
    "Vikram",
    "Pooja",
    "Karan",
    "Riya",
    "Aman",
]
LAST = [
    "Sharma",
    "Verma",
    "Gupta",
    "Singh",
    "Kumar",
    "Patel",
    "Reddy",
    "Iyer",
    "Nair",
    "Mehta",
    "Joshi",
    "Khan",
    "Das",
    "Bose",
    "Chopra",
    "Malhotra",
    "Bhatia",
    "Saxena",
    "Jain",
    "Rao",
]
BATCH = 10_000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--admin-username", default="admin")
    ap.add_argument("--admin-password", required=True)
    ap.add_argument("--students", type=int, default=0)
    args = ap.parse_args()

    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == args.admin_username)):
            db.add(
                User(
                    username=args.admin_username,
                    full_name="Administrator",
                    password_hash=hash_password(args.admin_password),
                    role=Role.ADMIN,
                )
            )
            db.commit()
            print(f"created admin user '{args.admin_username}'")

        if args.students:
            year = "2025-2026"
            if not db.scalars(select(Classroom)).first():
                db.add_all(
                    [Classroom(grade=g, section=s, academic_year=year) for g in range(1, 13) for s in "ABCDEFGHIJ"]
                )
                db.commit()
            class_ids = list(db.scalars(select(Classroom.id)))
            start = db.scalar(select(Student.id).order_by(Student.id.desc())) or 0
            t0 = time.perf_counter()
            for off in range(0, args.students, BATCH):
                rows = []
                for i in range(off, min(off + BATCH, args.students)):
                    n = start + i + 1
                    rows.append(
                        {
                            "admission_number": f"ADM-{n:08d}",
                            "first_name": random.choice(FIRST),
                            "last_name": random.choice(LAST),
                            "date_of_birth": date(2008, 1, 1) + timedelta(days=random.randint(0, 3650)),
                            "gender": random.choice(list(Gender)).value,
                            "guardian_name": f"{random.choice(FIRST)} {random.choice(LAST)}",
                            "guardian_phone": f"9{random.randint(10**8, 10**9 - 1)}",
                            "status": "active",
                            "classroom_id": random.choice(class_ids),
                            "version": 1,
                        }
                    )
                db.execute(insert(Student), rows)  # bulk insert bypasses ORM overhead
                db.commit()
            db.execute(text("ANALYZE"))  # refresh planner statistics after bulk load
            db.commit()
            print(f"inserted {args.students:,} students in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
