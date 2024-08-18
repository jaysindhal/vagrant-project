from locust import HttpUser, TaskSet, task, between
import os
import pandas as pd

class UserBehavior(TaskSet):
    def on_start(self):
        self.register()
        self.login()

    @task(1)
    def register(self):
        response = self.client.post("/project/validate.php", {
            "username": "testuser", 
            "mobile": "1235567890", 
            "email": "testuser@gmail.com", 
            "password": "testpassword", 
            "repeat_password": "testpassword"
        })
        if response.status_code != 200:
            print("Failed to register")

    @task(2)
    def login(self):
        response = self.client.post("/project/validate.php", {"username": "testuser@gmail.com", "password": "testpassword"})
        if response.status_code != 200:
            print("Failed to login")

    @task(3)
    def upload_song(self):
        with open("song.txt", "rb") as song:
            response = self.client.post("/project/uploaded_songs.php", files={"file": song})
            if response.status_code != 200:
                print("Failed to upload song")

class ReliabilityTestUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)

if __name__ == "__main__":
    user_counts = [100, 200, 300, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000]
    combined_data = []

    for count in user_counts:
        print(f"Running reliability test with {count} users...")
        command = f"locust -f reliability_test.py --host http://192.168.56.10 --csv=reliability_test_results_{count} --headless -u {count} -r 1 -t 10m"
        os.system(command)

        stats_filename = f"reliability_test_results_{count}_stats.csv"
        failures_filename = f"reliability_test_results_{count}_failures.csv"

        df_stats = pd.read_csv(stats_filename)
        df_failures = pd.read_csv(failures_filename)

        df_stats['User Count'] = count
        combined_data.append(df_stats)

    combined_df = pd.concat(combined_data)
    combined_df.to_csv("combined_reliability_test_results.csv", index=False)
