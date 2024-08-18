from locust import HttpUser, TaskSet, task, between
import os

class UserBehavior(TaskSet):
    def on_start(self):
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

class StressTestUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)

if __name__ == "__main__":
    user_counts = [2000]
    
    for count in user_counts:
        print(f"Running stress test with {count} users...")
        command = f"locust -f stress_test.py --host http://192.168.56.10 --csv=stress_test_results_{count} --headless -u {count} -r 20 -t 20m"
        os.system(command)
        
        stats_filename = f"stress_test_results_{count}_stats.csv"
        failures_filename = f"stress_test_results_{count}_failures.csv"
        
        with open(stats_filename, "r") as stats_file:
            print(stats_file.read())
        
        with open(failures_filename, "r") as failures_file:
            print(failures_file.read())
