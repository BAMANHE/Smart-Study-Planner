 #Smart Study Planner
FILE_NAME = "study_log.txt"

def classify_session(duration):
    """Classify a study session according to its duration."""
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


def add_session(sessions):
    """Collect and validate one study session from the user."""
    subject = input("Enter subject name: ").strip()
    topic = input("Enter topic covered: ").strip()
    date_label = input("Enter date/day label: ").strip()

    while True:
        duration_text = input("Enter duration in minutes: ").strip()
        try:
            duration = float(duration_text)
            if duration > 0:
                break
            print("Duration must be a positive number. Please try again.")
        except ValueError:
            print("Please enter a valid number for the duration.")

    session = {
        "subject": subject,
        "topic": topic,
        "date": date_label,
        "duration": duration
    }
    sessions.append(session)
    print("Study session added successfully.")


def view_sessions(sessions):
    """Display all saved study sessions in a formatted table."""
    if not sessions:
        print("\nNo study sessions recorded.")
        return

    print("\n" + "-" * 88)
    print(f"{'No.':<5}{'Subject':<20}{'Topic':<25}{'Date':<15}{'Minutes':<10}{'Class':<10}")
    print("-" * 88)

    for number, session in enumerate(sessions, start=1):
        duration = session["duration"]
        classification = classify_session(duration)
        print(
            f"{number:<5}"
            f"{session['subject'][:19]:<20}"
            f"{session['topic'][:24]:<25}"
            f"{session['date'][:14]:<15}"
            f"{duration:<10.1f}"
            f"{classification:<10}"
        )

    print("-" * 88)


def search_by_subject(sessions, subject):
    """Display sessions for a subject, ignoring letter case."""
    target = subject.strip().casefold()
    matches = [session for session in sessions
               if session["subject"].strip().casefold() == target]

    if not matches:
        print(f"\nNo sessions found for subject: {subject}")
        return

    print(f"\nSessions for subject: {subject}")
    print("-" * 75)
    print(f"{'No.':<5}{'Topic':<30}{'Date':<20}{'Minutes':<10}{'Class':<10}")
    print("-" * 75)

    total_minutes = 0
    for number, session in enumerate(matches, start=1):
        duration = session["duration"]
        total_minutes += duration
        print(
            f"{number:<5}"
            f"{session['topic'][:29]:<30}"
            f"{session['date'][:19]:<20}"
            f"{duration:<10.1f}"
            f"{classify_session(duration):<10}"
        )

    print("-" * 75)
    print(f"Total time spent on {subject}: {total_minutes / 60:.2f} hours")


def study_statistics(sessions):
    """Compute and display the requested study statistics."""
    if not sessions:
        print("\nNo study sessions available for statistics.")
        return

    total_minutes = sum(session["duration"] for session in sessions)

    subject_totals = {}
    for session in sessions:
        subject = session["subject"]
        key = subject.casefold()
        if key not in subject_totals:
            subject_totals[key] = {
                "name": subject,
                "minutes": 0
            }
        subject_totals[key]["minutes"] += session["duration"]

    print("\nSTUDY STATISTICS")
    print("-" * 50)
    print(f"Total hours studied overall: {total_minutes / 60:.2f}")

    print("\nTotal hours studied per subject:")
    for item in subject_totals.values():
        print(f"  {item['name']}: {item['minutes'] / 60:.2f} hours")

    weakest = min(subject_totals.values(), key=lambda item: item["minutes"])
    longest = max(sessions, key=lambda session: session["duration"])

    print(f"\nSubject with the least total study time: {weakest['name']}")
    print(
        "Single longest session: "
        f"{longest['duration']:.1f} minutes "
        f"({longest['subject']} - {longest['topic']})"
    )


def save_sessions(sessions):
    """Save all sessions to study_log.txt."""
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            for session in sessions:
                # Use a tab separator and replace tabs/new lines in user text.
                subject = session["subject"].replace("\t", " ").replace("\n", " ")
                topic = session["topic"].replace("\t", " ").replace("\n", " ")
                date_label = session["date"].replace("\t", " ").replace("\n", " ")
                file.write(
                    f"{subject}\t{topic}\t{date_label}\t{session['duration']}\n"
                )
        print(f"Sessions saved successfully to {FILE_NAME}.")
    except OSError as error:
        print(f"Could not save sessions: {error}")


def load_sessions():
    """Load existing sessions from study_log.txt if it exists."""
    sessions = []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.rstrip("\n")
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) != 4:
                    print(f"Skipping invalid record on line {line_number}.")
                    continue

                subject, topic, date_label, duration_text = parts

                try:
                    duration = float(duration_text)
                    if duration <= 0:
                        raise ValueError
                except ValueError:
                    print(f"Skipping invalid duration on line {line_number}.")
                    continue

                sessions.append({
                    "subject": subject,
                    "topic": topic,
                    "date": date_label,
                    "duration": duration
                })

    except FileNotFoundError:
        # First run: the file does not exist yet, so start with an empty list.
        pass
    except OSError as error:
        print(f"Could not load sessions: {error}")

    return sessions


def main():
    """Run the Smart Study Planner menu."""
    sessions = load_sessions()

    while True:
        print("\n========== SMART STUDY PLANNER ==========")
        print("1. Add a study session")
        print("2. View all sessions")
        print("3. Search sessions by subject")
        print("4. View statistics")
        print("5. Save and exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            subject = input("Enter subject to search: ")
            search_by_subject(sessions, subject)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select an option from 1 to 5.")


if __name__ == "__main__":
    main()
