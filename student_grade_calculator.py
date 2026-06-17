#!/usr/bin/env python3
"""Student Grade Calculator

Stores student records, calculates averages and letter grades,
and saves/loads records from a pipe-delimited file.
"""
from dataclasses import dataclass, field
import os
import sys
from typing import List, Optional


def getch():
    try:
        # Windows
        import msvcrt

        ch = msvcrt.getch()
        try:
            return ch.decode('utf-8')
        except Exception:
            return chr(ch[0])
    except ImportError:
        # Unix
        import tty
        import termios

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch


@dataclass
class Student:
    name: str
    id: str
    test1: float
    test2: float
    test3: float
    average: float = field(init=False)
    grade: str = field(init=False)

    def __post_init__(self):
        self.update()

    def update(self):
        self.average = calculate_average([self.test1, self.test2, self.test3])
        self.grade = calculate_grade(self.average)


def calculate_average(scores: List[float]) -> float:
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def calculate_grade(avg: float) -> str:
    if avg >= 90:
        return 'A'
    if avg >= 80:
        return 'B'
    if avg >= 70:
        return 'C'
    if avg >= 60:
        return 'D'
    return 'F'


FILENAME = 'student_grades.txt'


def load_records(filename: str = FILENAME) -> List[Student]:
    students: List[Student] = []
    if not os.path.exists(filename):
        return students
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 7:
                    # skip malformed lines
                    continue
                name, sid, t1, t2, t3, avg, grade = parts
                try:
                    s = Student(
                        name=name,
                        id=sid,
                        test1=float(t1),
                        test2=float(t2),
                        test3=float(t3),
                    )
                    # use stored average/grade if present (keeps consistency)
                    s.average = float(avg)
                    s.grade = grade
                    students.append(s)
                except ValueError:
                    # skip lines with conversion errors
                    continue
    except Exception as e:
        print(f"Error loading records from {filename}: {e}")
    return students


def save_records(students: List[Student], filename: str = FILENAME) -> None:
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for s in students:
                line = '|'.join([
                    s.name,
                    s.id,
                    f"{s.test1:.2f}",
                    f"{s.test2:.2f}",
                    f"{s.test3:.2f}",
                    f"{s.average:.2f}",
                    s.grade,
                ])
                f.write(line + '\n')
        print(f"Saved {len(students)} record(s) to {filename}.")
    except Exception as e:
        print(f"Error saving records to {filename}: {e}")


def prompt_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        if raw == '\x1b':
            raise KeyboardInterrupt
        try:
            val = float(raw)
            return val
        except ValueError:
            print('Please enter a valid number (e.g., 85.5).')


def add_student_interactive() -> Optional[Student]:
    try:
        name = input('Student name: ').strip()
        if name == '':
            print('Name cannot be empty.')
            return None
        sid = input('Student ID: ').strip()
        if sid == '':
            print('ID cannot be empty.')
            return None
        t1 = prompt_float('Test 1 score: ')
        t2 = prompt_float('Test 2 score: ')
        t3 = prompt_float('Test 3 score: ')
        s = Student(name=name, id=sid, test1=t1, test2=t2, test3=t3)
        print(f"Added {s.name} with average {s.average:.2f} and grade {s.grade}.")
        return s
    except KeyboardInterrupt:
        print('\nInput cancelled.')
        return None


def display_students(students: List[Student]) -> None:
    if not students:
        print('No student records to display.')
        return
    header = f"{'Name':25} | {'ID':10} | {'T1':6} | {'T2':6} | {'T3':6} | {'Avg':6} | Grade"
    print(header)
    print('-' * len(header))
    for s in students:
        print(f"{s.name:25} | {s.id:10} | {s.test1:6.2f} | {s.test2:6.2f} | {s.test3:6.2f} | {s.average:6.2f} | {s.grade}")


def class_statistics(students: List[Student]) -> None:
    if not students:
        print('No records to compute statistics.')
        return
    averages = [s.average for s in students]
    highest = max(averages)
    lowest = min(averages)
    class_avg = sum(averages) / len(averages)
    # find student(s) with highest/lowest
    highest_students = [s.name for s in students if abs(s.average - highest) < 1e-6]
    lowest_students = [s.name for s in students if abs(s.average - lowest) < 1e-6]
    print(f"Highest average: {highest:.2f} ({', '.join(highest_students)})")
    print(f"Lowest average:  {lowest:.2f} ({', '.join(lowest_students)})")
    print(f"Class average:   {class_avg:.2f}")


def search_by_name(students: List[Student], query: str) -> List[Student]:
    q = query.lower()
    return [s for s in students if q in s.name.lower()]


def main():
    print('Student Grade Calculator')
    print('Loading records...')
    students = load_records()
    print(f'Loaded {len(students)} record(s).')

    while True:
        print('\nMenu:')
        print('1) Add new student')
        print('2) Display all students')
        print('3) Class statistics')
        print('4) Search by name')
        print('5) Save records now')
        print('Press ESC to exit the program')
        print('Choose option (press key): ', end='', flush=True)
        ch = getch()
        print(ch)
        if ch == '\x1b':
            print('Exiting and saving records...')
            save_records(students)
            break
        if ch == '1':
            s = add_student_interactive()
            if s:
                students.append(s)
        elif ch == '2':
            display_students(students)
        elif ch == '3':
            class_statistics(students)
        elif ch == '4':
            name = input('Enter name to search (case-insensitive): ').strip()
            results = search_by_name(students, name)
            if not results:
                print('No matching students found.')
            else:
                display_students(results)
        elif ch == '5':
            save_records(students)
        else:
            print('Unknown option. Please choose 1-5 or press ESC.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted. Saving records before exit...')
        # attempt to save on interrupt
        try:
            # try to load the current students variable if present
            save_records(globals().get('students', []))
        except Exception:
            pass
        print('Goodbye.')
