from abc import ABC, abstractmethod


class Record(ABC):
    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def list(self):
        pass


class Student(Record):
    def __init__(self):
        self.__student_id = ""
        self.__name = ""
        self.__dob = ""

    @property
    def student_id(self):
        return self.__student_id

    @property
    def name(self):
        return self.__name

    @property
    def dob(self):
        return self.__dob

    def input(self):
        self.__student_id = input("  ID: ")
        self.__name = input("  Name: ")
        self.__dob = input("  Date of birth (dd/mm/yyyy): ")

    def list(self):
        print(self.student_id, "-", self.name, "-", self.dob)


class Course(Record):
    def __init__(self):
        self.__course_id = ""
        self.__name = ""

    @property
    def course_id(self):
        return self.__course_id

    @property
    def name(self):
        return self.__name

    def input(self):
        self.__course_id = input("  ID: ")
        self.__name = input("  Name: ")

    def list(self):
        print(self.course_id, "-", self.name)


class Mark:
    def __init__(self, student_id, course_id, value):
        self.__student_id = student_id
        self.__course_id = course_id
        self.__value = value

    @property
    def student_id(self):
        return self.__student_id

    @property
    def course_id(self):
        return self.__course_id

    @property
    def value(self):
        return self.__value


class StudentMarkManager:
    def __init__(self):
        self.__students = []
        self.__courses = []
        self.__marks = []

    def __input_records(self, records, count_prompt, item_name, record_type):
        number = int(input(count_prompt))
        for index in range(number):
            print(item_name, index + 1, ":")
            record = record_type()
            record.input()
            records.append(record)

    def __list_records(self, records):
        for record in records:
            record.list()

    def input_students(self):
        self.__input_records(self.__students, "Number of students: ", "Student", Student)

    def input_courses(self):
        self.__input_records(self.__courses, "Number of courses: ", "Course", Course)

    def input_marks(self):
        self.list_courses()
        course_id = input("Enter course ID to input marks for: ")

        for student in self.__students:
            value = float(input("  Mark for " + student.name + " (" + student.student_id + "): "))
            self.__marks.append(Mark(student.student_id, course_id, value))

    def list_courses(self):
        print()
        print("-- Courses --")
        self.__list_records(self.__courses)

    def list_students(self):
        print()
        print("-- Students --")
        self.__list_records(self.__students)

    def show_marks_for_course(self):
        self.list_courses()
        course_id = input("Enter course ID: ")

        print()
        print("-- Marks for course", course_id, "--")
        for student in self.__students:
            mark_found = False
            for mark in self.__marks:
                if mark.student_id == student.student_id and mark.course_id == course_id:
                    print(student.student_id, "-", student.name, "-", mark.value)
                    mark_found = True
            if not mark_found:
                print(student.student_id, "-", student.name, "-", "no mark yet")

    def run(self):
        while True:
            print()
            print("1. Input students")
            print("2. Input courses")
            print("3. Input marks for a course")
            print("4. List courses")
            print("5. List students")
            print("6. Show marks for a course")
            print("0. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                self.input_students()
            elif choice == "2":
                self.input_courses()
            elif choice == "3":
                self.input_marks()
            elif choice == "4":
                self.list_courses()
            elif choice == "5":
                self.list_students()
            elif choice == "6":
                self.show_marks_for_course()
            elif choice == "0":
                break
            else:
                print("Invalid option.")


if __name__ == "__main__":
    StudentMarkManager().run()
