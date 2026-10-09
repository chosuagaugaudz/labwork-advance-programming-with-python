import ast
import math
from pathlib import Path
import re

import numpy as np
import pandas as pd
import curses


DATA_DIR = Path(__file__).resolve().parent / "student_system_data"

student_ids = []
student_names = []
student_dobs = []

course_ids = []
course_names = []
course_credits = []

mark_student_ids = []
mark_course_ids = []
mark_values = []


def input_students():
	n = int(input("Number of students: "))
	for i in range(n):
		print("Student", i + 1, ":")
		sid = input("  ID: ")
		name = input("  Name: ")
		dob = input("  Date of birth (dd/mm/yyyy): ")
		student_ids.append(sid)
		student_names.append(name)
		student_dobs.append(dob)


def input_courses():
	n = int(input("Number of courses: "))
	for i in range(n):
		print("Course", i + 1, ":")
		cid = input("  ID: ")
		name = input("  Name: ")
		credit = int(input("  Credits: "))
		course_ids.append(cid)
		course_names.append(name)
		course_credits.append(credit)


def input_marks():
	list_courses()
	cid = input("Enter course ID to input marks for: ")

	for i in range(len(student_ids)):
		sid = student_ids[i]
		name = student_names[i]
		raw_mark = float(input("  Mark for " + name + " (" + sid + "): "))
		mark = math.floor(raw_mark * 10) / 10
		mark_student_ids.append(sid)
		mark_course_ids.append(cid)
		mark_values.append(mark)


def list_courses():
	print()
	print("-- Courses --")
	for i in range(len(course_ids)):
		print(course_ids[i], "-", course_names[i], "-", course_credits[i], "credits")


def list_students():
	print()
	print("-- Students --")
	for i in range(len(student_ids)):
		print(student_ids[i], "-", student_names[i], "-", student_dobs[i])


def show_marks_for_course():
	list_courses()
	cid = input("Enter course ID: ")

	print()
	print("-- Marks for course", cid, "--")
	for i in range(len(student_ids)):
		sid = student_ids[i]
		name = student_names[i]
		mark_found = False
		for j in range(len(mark_student_ids)):
			if mark_student_ids[j] == sid and mark_course_ids[j] == cid:
				print(sid, "-", name, "-", mark_values[j])
				mark_found = True
		if not mark_found:
			print(sid, "-", name, "-", "no mark yet")


def calculate_gpa(student_id):
	marks_list = []
	credits_list = []

	for i in range(len(mark_student_ids)):
		if mark_student_ids[i] == student_id:
			cid = mark_course_ids[i]
			course_index = course_ids.index(cid)
			credits_list.append(course_credits[course_index])
			marks_list.append(mark_values[i])

	if len(marks_list) == 0:
		return None

	marks_array = np.array(marks_list)
	credits_array = np.array(credits_list)
	return np.sum(marks_array * credits_array) / np.sum(credits_array)


def list_students_by_gpa():
	results = []
	for i in range(len(student_ids)):
		gpa = calculate_gpa(student_ids[i])
		results.append((student_names[i], student_ids[i], gpa))
	results.sort(key=lambda result: (result[2] is None, -(result[2] or 0)))
	return results


def show_gpa_ranking_curses(stdscr):
	stdscr.clear()
	results = list_students_by_gpa()
	stdscr.addstr(0, 2, "GPA RANKING (descending)", curses.A_BOLD)
	stdscr.addstr(1, 2, "-" * 40)

	row = 3
	for rank, (name, student_id, gpa) in enumerate(results, start=1):
		if gpa is None:
			line = f"{rank:>2}. {name} ({student_id}) - no marks yet"
		else:
			line = f"{rank:>2}. {name} ({student_id}) - GPA: {gpa:.2f}"
		stdscr.addstr(row, 2, line)
		row += 1

	stdscr.addstr(row + 1, 2, "Press any key to return to menu...")
	stdscr.refresh()
	stdscr.getch()


def show_gpa_ranking():
	curses.wrapper(show_gpa_ranking_curses)


def load_csv_frames():
	students = pd.read_csv(DATA_DIR / "students.csv")
	courses = pd.read_csv(DATA_DIR / "courses.csv")
	marks = pd.read_csv(DATA_DIR / "marks.csv")
	return students, courses, marks


def export_data_to_csv():
	DATA_DIR.mkdir(parents=True, exist_ok=True)
	students = pd.DataFrame({
		"student_id": student_ids,
		"name": student_names,
		"dob": student_dobs,
	})
	courses = pd.DataFrame({
		"course_id": course_ids,
		"course_name": course_names,
		"credits": course_credits,
	})
	marks = pd.DataFrame({
		"student_id": mark_student_ids,
		"course_id": mark_course_ids,
		"mark": mark_values,
	})

	students.to_csv(DATA_DIR / "students.csv", index=False)
	courses.to_csv(DATA_DIR / "courses.csv", index=False)
	marks.to_csv(DATA_DIR / "marks.csv", index=False)

	students_frame, courses_frame, marks_frame = load_csv_frames()
	print(f"\nExported and loaded CSV data in {DATA_DIR}:")
	print("students.csv:", len(students_frame), "rows")
	print("courses.csv:", len(courses_frame), "rows")
	print("marks.csv:", len(marks_frame), "rows")


def validate_query_expression(expression, columns):
	allowed_nodes = (
		ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.Compare,
		ast.Name, ast.Load, ast.Constant, ast.UnaryOp, ast.Not,
		ast.USub, ast.UAdd, ast.List, ast.Tuple, ast.Set,
		ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
		ast.In, ast.NotIn,
	)
	tree = ast.parse(expression, mode="eval")
	for node in ast.walk(tree):
		if not isinstance(node, allowed_nodes):
			raise ValueError("Use column comparisons combined with and/or.")
		if isinstance(node, ast.Name) and node.id not in columns:
			raise ValueError(f"Unknown student column: {node.id}")


def query_students():
	if not all((DATA_DIR / filename).is_file()
			   for filename in ("students.csv", "courses.csv", "marks.csv")):
		print("CSV files are missing. Export the data first using option 8.")
		return

	students, _, _ = load_csv_frames()
	condition = input(
		'Enter a condition (for example, name = "Mr. Volunteers"): '
	).strip()
	equality = re.fullmatch(
		r"\s*([A-Za-z_]\w*)\s*(?<![<>=!])=(?!=)\s*(.+?)\s*",
		condition,
	)
	if equality:
		condition = f"{equality.group(1)} == {equality.group(2)}"

	try:
		validate_query_expression(condition, students.columns)
		matches = students.query(condition)
	except (SyntaxError, TypeError, ValueError) as error:
		print("Invalid query:", error)
		return

	if matches.empty:
		print("No students matched that condition.")
	else:
		print(matches.to_string(index=False))


def menu():
	while True:
		print()
		print("1. Input students")
		print("2. Input courses")
		print("3. Input marks for a course")
		print("4. List courses")
		print("5. List students")
		print("6. Show marks for a course")
		print("7. Show GPA ranking (curses)")
		print("8. Export data to CSV and load DataFrames")
		print("9. Query students from CSV")
		print("0. Exit")

		choice = input("Choose an option: ")

		if choice == "1":
			input_students()
		elif choice == "2":
			input_courses()
		elif choice == "3":
			input_marks()
		elif choice == "4":
			list_courses()
		elif choice == "5":
			list_students()
		elif choice == "6":
			show_marks_for_course()
		elif choice == "7":
			show_gpa_ranking()
		elif choice == "8":
			export_data_to_csv()
		elif choice == "9":
			query_students()
		elif choice == "0":
			break
		else:
			print("Invalid option.")


if __name__ == "__main__":
	menu()
