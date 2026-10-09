from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent


def main():
    students = pd.read_csv(DATA_DIR / "students.csv")
    scores = pd.read_csv(DATA_DIR / "scores.csv")

    print("STUDENT DATA")
    print("\nFirst five rows:")
    print(students.head())
    print(f"\nRows: {students.shape[0]}, columns: {students.shape[1]}")

    print("\nNames and GPA:")
    print(students[["name", "GPA"]].to_string(index=False))

    print("\nStudents with GPA >= 3.5:")
    print(
        students.loc[students["GPA"] >= 3.5, ["name", "GPA"]]
        .sort_values("GPA", ascending=False)
        .to_string(index=False)
    )

    print("\nStudents sorted by GPA (highest first):")
    print(
        students.sort_values("GPA", ascending=False)[["name", "GPA"]]
        .to_string(index=False)
    )

    print("\nAverage GPA by major:")
    print(
        students.groupby("major", as_index=False)["GPA"]
        .mean()
        .sort_values("GPA", ascending=False)
        .to_string(index=False)
    )

    print("\nMERGED STUDENT AND SCORE DATA")
    print("\nMissing values before cleaning:")
    print(
        pd.DataFrame(
            {
                "students.csv": students.isna().sum(),
                "scores.csv": scores.isna().sum(),
            }
        ).fillna(0).astype(int).to_string()
    )

    students_clean = students.copy()
    students_clean["age"] = students_clean["age"].fillna(
        students_clean["age"].median()
    )
    major_gpa_medians = students_clean.groupby("major")["GPA"].transform("median")
    students_clean["GPA"] = students_clean["GPA"].fillna(major_gpa_medians)
    students_clean["GPA"] = students_clean["GPA"].fillna(
        students_clean["GPA"].median()
    )

    print("\nMissing values after cleaning student age and GPA:")
    print(
        pd.DataFrame(
            {
                "students.csv": students_clean.isna().sum(),
                "scores.csv": scores.isna().sum(),
            }
        ).fillna(0).astype(int).to_string()
    )
    print(
        "\nMissing subject scores are kept missing; each student's average "
        "uses their available scores."
    )

    merged = students_clean.merge(
        scores,
        on="student_id",
        how="left",
        validate="one_to_one",
    )
    subject_columns = ["python", "math", "database"]
    merged["average_score"] = merged[subject_columns].mean(axis=1)

    print("\nMerged data with each student's average score:")
    print(
        merged[["student_id", "name", "major", "average_score"]]
        .sort_values("student_id")
        .to_string(index=False, float_format=lambda value: f"{value:.2f}")
    )

    print("\nTop five students by average score:")
    print(
        merged.nlargest(5, "average_score")[
            ["student_id", "name", "major", "average_score"]
        ].to_string(index=False, float_format=lambda value: f"{value:.2f}")
    )

    print("\nAverage score by major:")
    print(
        merged.groupby("major", as_index=False)["average_score"]
        .mean()
        .sort_values("average_score", ascending=False)
        .to_string(index=False, float_format=lambda value: f"{value:.2f}")
    )


if __name__ == "__main__":
    main()
