class SportsClub:
    def __init__(self):
        # قاعدة البيانات الوهمية (تستبدل لاحقاً بـ SQL)
        self.users = {}          # {"username": "password"}
        self.captains = {}       # {"name": {"age": int, "address": str, "gender": str, "sport": str, "active": bool}}
        self.sports = {
            "football": {"Ahmed", "Akrm", "Ali"},
            "basketball": {"Ahmed", "Saed", "Moha"},
            "swimming": {"Akrm", "Moha", "Er"}
        }
        self.messages = {}       # {"username": ["msg1", "msg2"]}
        self.complaints = []     # [{"user": "x", "content": "y", "rating": "z"}]
        self.applications = {}   # {"username": {"sport": "football", "reason": "...", "status": "pending"}}

    # --- عمليات تسجيل الدخول والإنشاء ---
    def add_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        self.messages[username] = ["Welcome to Bisto Sports Club!"]
        return True

    def authenticate_user(self, username, password):
        return self.users.get(username) == password
        
    def add_captain_request(self, name, age, address, gender, sport):
        self.captains[name] = {
            "age": age, "address": address, "gender": gender, 
            "sport": sport, "active": False
        }
        return True

    # --- عمليات الأعضاء (Users) ---
    def apply_for_sport(self, username, sport, message):
        if username in self.sports.get(sport, set()):
            return False, "You are already subscribed to this sport."
        self.applications[username] = {"sport": sport, "reason": message, "status": "pending"}
        return True, "Application sent to admin."

    def add_complaint(self, username, complaint_data):
        self.complaints.append({"user": username, **complaint_data})

    def get_user_messages(self, username):
        return self.messages.get(username, [])

    # --- عمليات الإدارة (Admin) ---
    def get_all_members_by_sport(self):
        return self.sports

    def approve_application(self, username, approve=True):
        if username not in self.applications:
            return False
        app = self.applications.pop(username)
        if approve:
            sport = app["sport"]
            self.sports[sport].add(username)
            self.messages.setdefault(username, []).append(f"Congratulations! You've been accepted to {sport}.")
        else:
            self.messages.setdefault(username, []).append(f"Sorry, your application for {app['sport']} was rejected.")
        return True


class TerminalUI:
    def __init__(self, club: SportsClub):
        self.club = club
        self.admin_pass = "admin123" # افتراضي

    def run(self):
        while True:
            print("\n" + "="*30)
            print("Welcome to Bisto Sports Club!")
            print("1. Admin Panel\n2. User Sign Up\n3. User Login\n4. Captain Apply\n0. Exit")
            ch = input("Choose an option: ").strip()

            if ch == "1":
                self.admin_menu()
            elif ch == "2":
                self.user_signup()
            elif ch == "3":
                self.user_login()
            elif ch == "4":
                self.captain_apply()
            elif ch == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")

    def admin_menu(self):
        pwd = input("Enter Admin Password: ")
        if pwd != self.admin_pass:
            print("Access Denied!")
            return
            
        while True:
            print("\n--- Admin Dashboard ---")
            pending = len(self.club.applications)
            print(f"1. View Players\n2. Review Applications ({pending})\n3. View Complaints\n0. Back")
            ch = input("Choice: ").strip()
            
            if ch == "1":
                sports = self.club.get_all_members_by_sport()
                for sport, players in sports.items():
                    print(f"\n{sport.capitalize()} Team: {', '.join(players) if players else 'Empty'}")
            elif ch == "2":
                if not self.club.applications:
                    print("No pending applications.")
                    continue
                for user, data in list(self.club.applications.items()):
                    print(f"\nUser: {user} wants to join {data['sport']}")
                    print(f"Message: {data['reason']}")
                    acc = input("Approve? (y/n): ").strip().lower()
                    self.club.approve_application(user, approve=(acc == 'y'))
                    print("Processed.")
            elif ch == "0":
                break

    def user_signup(self):
        name = input("Enter new username: ").strip()
        pwd = input("Enter password: ").strip()
        if self.club.add_user(name, pwd):
            print("Sign up successful! You can now log in.")
        else:
            print("Username already exists.")

    def user_login(self):
        name = input("Username: ").strip()
        pwd = input("Password: ").strip()
        
        if not self.club.authenticate_user(name, pwd):
            print("Invalid credentials!")
            return
            
        self.user_dashboard(name)

    def user_dashboard(self, username):
        while True:
            msgs = self.club.get_user_messages(username)
            msg_alert = " (You have new messages!)" if msgs else ""
            print(f"\n--- Welcome {username} ---")
            print(f"1. Subscribe to a sport\n2. Send a complaint\n3. View Messages{msg_alert}\n0. Logout")
            ch = input("Choice: ").strip()
            
            if ch == "1":
                sport = input("Which sport? (football/basketball/swimming): ").strip().lower()
                msg = input("Why do you want to join and what are your skills? ")
                success, response = self.club.apply_for_sport(username, sport, msg)
                print(response)
            elif ch == "2":
                what = input("What went wrong? ")
                why = input("Why is this disappointing? ")
                rate = input("Rate our service (1-10): ")
                self.club.add_complaint(username, {"what": what, "why": why, "rating": rate})
                print("Complaint submitted. Thank you!")
            elif ch == "3":
                if not msgs:
                    print("No messages.")
                else:
                    for i, m in enumerate(msgs):
                        print(f"[{i+1}] {m}")
                    input("Press enter to return...")
            elif ch == "0":
                break

    def captain_apply(self):
        print("\n--- Captain Application ---")
        name = input("Name: ").strip()
        age = input("Age: ").strip()
        address = input("Address: ").strip()
        gender = input("Gender: ").strip()
        sport = input("Sport you want to train: ").strip()
        
        self.club.add_captain_request(name, int(age) if age.isdigit() else 0, address, gender, sport)
        print("Application submitted to admin! We will contact you.")

# تشغيل البرنامج
if __name__ == "__main__":
    bisto_backend = SportsClub()
    app_frontend = TerminalUI(bisto_backend)
    app_frontend.run()
