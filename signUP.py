import logging
import os.path
from locust import HttpUser, TaskSet, task, constant
from faker import Faker
import json
import environmentVariable
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (999999, 999999))
USERS = environmentVariable.user

fake = Faker()

def generator(number_of_records):
    CRED = []
    counter = 1
    for _ in range(number_of_records):
        CRED.append({"Name": fake.name(), "Address": fake.address(),
                     "PostalCode": fake.postcode(), "city": fake.city(),
                     "TelephoneNumber": fake.phone_number(),
                     "EmailAddress": "admin" + str(counter) + "@example.com"})
        counter += 1
    with open('user_Credentials.json', 'w') as file:
        json.dump(CRED, file, indent=4)
    return CRED


if not os.path.exists("user_Credentials.json"):
    USER_CREDENTIALS = generator(USERS)
else:
    f = open("user_Credentials.json", "r")
    USER_CREDENTIALS = list(json.load(f))
    f.close()

class MyLoadTester(HttpUser):
    host = "http://" + environmentVariable.host + ":7005"

    wait_time = constant(1)
    Name = "NOT_FOUND"
    Address = "NOT_FOUND"
    PostalCode = "NOT_FOUND"
    City = "NOT_FOUND"
    TelephoneNumber = "NOT_FOUND"
    EmailAddress = "NOT_FOUND"
    value = "NOT FOUND"

    @task
    def on_start(self):
        if len(USER_CREDENTIALS) > 0:
            temp = USER_CREDENTIALS.pop()

            self.Name = temp["Name"]
            self.Address = temp["Address"]
            self.PostalCode = temp["PostalCode"]
            self.City = temp["City"]
            self.TelephoneNumber = temp["TelephoneNumber"]
            self.EmailAddress = temp["EmailAddress"]

        logging.info('Register Customer with %s email and %s password', self.email, self.password)
        with  self.client.post("/CustomerManagement/Register", json={'name': self.name, 'address': self.address, 'postalcode': self.postalcode, 'city': self.city, 'Telephonenumber': self.telephonenumber, 'emailaddress': self.emailaddress},catch_response=True) as response:
            print(response.json())
            if ("email") in response.json():
                if response.status_code == 200:
                    response.success()
                    print(f"Partial account creation for {self.email}")
                else:
                    response.failure("HTTP 200 OK not received")
            else:
                response.failure("Failed to Create account")
