from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient

# Username and Password authentication

class ValidateUser(Action):
    def name(self) -> Text:
        return "action_validate_user"
    

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("Hi")
        username = tracker.get_slot("username")
        password = tracker.get_slot("password")
        print("The username is :- ",username)
        print("The password is :- ",password)


        client = MongoClient("mongodb://localhost:27017/")
        db = client["chatbot"]
        collection = db["employee"]

        # Query MongoDB for user authentication
        user = collection.find_one({"username": username, "password": password})
        print("user:- ",user)

        if user:
            
            dispatcher.utter_message(text="User authenticated! Please let me know how I can help you")
            
        else:
            dispatcher.utter_message(text="Invalid credentials! Please try again.")

        return []
    

# getting salary details

from typing import Any, Text, Dict, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionGetSalary(Action):
    def name(self) -> Text:
        return "action_get_salary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username")
        employee_id = tracker.get_slot("employee_id")

        # Connect to MongoDB
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["chatbot"]
            collection = db["employee"]
        except ConnectionFailure:
            dispatcher.utter_message("Failed to connect to MongoDB.")
            return []

        # Query MongoDB for employee salary
        employee = collection.find_one({"username": username})

        if employee:
            salary = employee.get("salary")
            if salary:
                dispatcher.utter_message(f"The salary of {username}  is {salary}.")
            else:
                dispatcher.utter_message(f"No salary information found for {username}.")
        else:
            dispatcher.utter_message(f"No employee found with username {username}.")

        client.close()
        return []


# Leaves Status

class ActionGetLeaves(Action):
    def name(self) -> Text:
        return "action_status_for_leave"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username")
        
        # Connect to MongoDB
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["chatbot"]
            collection = db["employee"]
        except ConnectionFailure:
            dispatcher.utter_message("Failed to connect to MongoDB.")
            return []

        # Query MongoDB for employee salary
        employee = collection.find_one({"username": username})

        if employee:
            leaves = employee.get("leaves")
            if leaves:
                dispatcher.utter_message(f"The total leaves of {username}  is {leaves}.")
            else:
                dispatcher.utter_message(f"No leaves information found for {username}.")
        else:
            dispatcher.utter_message(f"No employee found with username {username}.")

        client.close()
        return []


from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from pymongo import MongoClient
from datetime import datetime

class ActionApplyLeave(FormValidationAction):
    def name(self) -> Text:
        return "validate_leavesapplication_form"

    def validate_start_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value is None:
            dispatcher.utter_message("Please provide a valid start date.")
            return {"start_date": None}
        else:
            return {"start_date": slot_value}

    def validate_end_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value is None:
            dispatcher.utter_message("Please provide a valid end date.")
            return {"end_date": None}
        else:
            return {"end_date": slot_value}

    def validate_reason(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value is None:
            dispatcher.utter_message("Please provide a reason for leave.")
            return {"reason": None}
        else:
            return {"reason": slot_value}



from typing import Any, Dict, List, Text
from pymongo import MongoClient
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionLeavesSubmit(Action):
    def name(self) -> Text:
        return "action_leaves_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # MongoDB connection
        client = MongoClient("mongodb://localhost:27017/")
        db = client["chatbot"]
        collection = db["employee"]

        # Get slot values
        start_date = tracker.get_slot("start_date")['from'][:10]
        end_date = tracker.get_slot("end_date")['to'][:10]
        # start_date = tracker.get_slot("start_date")
        # end_date = tracker.get_slot("end_date")
        reason = tracker.get_slot("reason")
        username = tracker.get_slot("username")  # Assuming username is stored in sender_id
        password = tracker.get_slot("password")
        print("Start Date :- ", start_date)
        print("End Date :- ", end_date)
        print("Reason :- ", reason)
        # Calculate leave duration
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        leave_duration = (end_date_obj - start_date_obj).days + 1

        # Fetch remaining leave balance from MongoDB
        user_leave_record = collection.find_one({"username": username, "password": password})
        print("Username :-",username)
        print("User Leave Record:", user_leave_record)  # Debug statement
        remaining_leaves = user_leave_record.get("leaves", 0)  # default to 0 if leaves not found

        
        print("Remaining Leaves:", remaining_leaves)  # Debug statement
        print("Leave Duration:", leave_duration)  # Debug statement

        # Check if leave balance is sufficient
        if remaining_leaves >= leave_duration:
            left_leaves = remaining_leaves - leave_duration
            
            # Update leave balance in MongoDB
            collection.update_one({"username": username}, {"$inc": {"leaves": -leave_duration}})
            print("Left Leaves After Update:", left_leaves)  # Debug statement

            # Confirm leave application
            dispatcher.utter_message(f"Your leave application from {start_date} to {end_date} for {reason} has been submitted to your line manager.")
        else:
            dispatcher.utter_message("Insufficient leave balance.")

        client.close()
        return [SlotSet("start_date", None), SlotSet("end_date", None), SlotSet("reason", None)]


# class ActionLeavesSubmit(Action):
#     def name(self) -> Text:
#         return "action_leaves_submit"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
   
#         # MongoDB connection
#         client = MongoClient("mongodb://localhost:27017/")
#         db = client["chatbot"]
#         collection = db["employee"]

#         # Get slot values
#         start_date = tracker.get_slot("start_date")
#         end_date = tracker.get_slot("end_date")
#         reason = tracker.get_slot("reason")
#         username = tracker.sender_id  # Assuming username is stored in sender_id

#         # Calculate leave duration
#         start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
#         leave_duration = (end_date_obj - start_date_obj).days + 1

#         print("The start date is :- ", start_date )
#         print("The end date is :- ",end_date)

#         # Fetch remaining leave balance from MongoDB
#         user_leave_record = collection.find_one({"username": username})
#         print("User Leave:- ",user_leave_record)
#         print("username is :-",username)
#         remaining_leaves = user_leave_record.get("leaves")  # default to 0 if leaves not found

#         # Check if leave balance is sufficient
#         if remaining_leaves >= leave_duration:
#             left_leaves= remaining_leaves- leave_duration
#             print("left leaves are :-",  left_leaves)
            
#             # Update leave balance in MongoDB
#             collection.update_one({"username": username}, { "$set": { 'leaves': left_leaves}})

#             # Confirm leave application
#             dispatcher.utter_message(f"Your leave application from {start_date} to {end_date} for {reason} has been approved.")
#         else:
#             dispatcher.utter_message("Insufficient leave balance.")

#         client.close()
#         return [SlotSet("start_date", None), SlotSet("end_date", None), SlotSet("reason", None)]



# class ActionApplyLeave(Action):
#     def name(self) -> Text:
#         return "action_apply_leave"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # MongoDB connection
#         client = MongoClient("mongodb://localhost:27017/")
#         db = client["chatbot"]
#         collection = db["employee"]

#         # Get slot values
#         start_date = tracker.get_slot("start_date")
#         end_date = tracker.get_slot("end_date")
#         reason = tracker.get_slot("reason")
#         username = tracker.get_slot("username")
#         employee = collection.find_one({"username": username})

#         print("Start date is :- " , start_date )
#         print("End date is :- ", end_date)

#         # Check if end_date is None
#         if end_date is None:
#             dispatcher.utter_message("Please provide a valid end date.")
#             return []
        
#         if start_date is None:
#             dispatcher.utter_message("Please provide a valid start date.")
#             return []
        

#         # Calculate leave duration
#         start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
#         leave_duration = (end_date_obj - start_date_obj).days + 1

      

#         # Fetch remaining leave balance from MongoDB
#         user_leave_record = collection.find_one({"username": username})
#         remaining_leaves = user_leave_record["leaves"]

#         # Check if leave balance is sufficient
#         if remaining_leaves >= leave_duration:
#             # Update leave balance in MongoDB
#             collection.update_one({"username": username}, {"$inc": {"remaining_leaves": -leave_duration}})

#             # Confirm leave application
#             dispatcher.utter_message(f"Your leave application from {start_date} to {end_date} for {reason} has been approved.")
#         else:
#             dispatcher.utter_message("Insufficient leave balance.")

#         client.close()
#         return [SlotSet("start_date", None), SlotSet("end_date", None), SlotSet("reason", None)]





   
# Menu options

# class ActionHandleMenu(Action):
#     def name(self) -> Text:
#         return "action_handle_menu"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         user_choice = tracker.latest_message.get("intent")
#         print("userchoice")
#         print(user_choice)
#         print("tracker :- /n/n",tracker.latest_message)
#         if user_choice == "/leave":
#             # Perform actions for leave
#             dispatcher.utter_message(text="You selected Leave. Here's some information about leave.")
#         elif user_choice == "/hr_policy":
#             # Perform actions for HR policy
#             dispatcher.utter_message(text="You selected HR Policy. Here's some information about HR policy.")
#         elif user_choice == "/benefits":
#             # Perform actions for benefits
#             dispatcher.utter_message(text="You selected Benefits. Here's some information about benefits.")
#         elif user_choice == "/training":
#             # Perform actions for training
#             dispatcher.utter_message(text="You selected Training. Here's some information about training.")
#         elif user_choice == "/salary":
#             # Perform actions for salary
#             dispatcher.utter_message(text="You selected Salary. Here's some information about salary.")
#         else:
#             dispatcher.utter_message(text="I'm sorry, I didn't understand your selection.")
#         return []
    

# from typing import Any, Text, Dict, List
# from pymongo import MongoClient
# from datetime import datetime

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# class TestDispatcher(CollectingDispatcher):
#     def utter_message(self, *args: Any, **kwargs: Any) -> None:
#         message = kwargs.get("text")
#         if message:
#             print(message)
#         super().utter_message(*args, **kwargs)

# class ActionApplyLeave(Action):
#     def name(self) -> Text:
#         return "action_apply_leave"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # MongoDB connection
#         client = MongoClient("mongodb://localhost:27017/")
#         db = client["chatbot"]
#         collection = db["employee"]

#         # Get slot values
#         start_date = tracker.get_slot("start_date")
#         end_date = tracker.get_slot("end_date")
#         reason = tracker.get_slot("reason")
#         username = tracker.get_slot("username")
#         employee = collection.find_one({"username": username})

#         # Calculate leave duration
#         start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
#         leave_duration = (end_date_obj - start_date_obj).days + 1

#         # Fetch remaining leave balance from MongoDB
#         user_leave_record = collection.find_one({"username": username})
#         remaining_leaves = user_leave_record["leaves"]

#         # Check if leave balance is sufficient
#         if remaining_leaves >= leave_duration:
#             # Update leave balance in MongoDB
#             collection.update_one({"username": username}, {"$inc": {"leaves": -leave_duration}})

#             # Confirm leave application
#             dispatcher.utter_message(f"Your leave application from {start_date} to {end_date} for {reason} has been approved.")
#         else:
#             dispatcher.utter_message("Insufficient leave balance.")

#         client.close()
#         return [SlotSet("start_date", None), SlotSet("end_date", None), SlotSet("reason", None)]


# # Create a dispatcher and tracker
# dispatcher = TestDispatcher()
# tracker = Tracker(
#     sender_id="test",
#     slots={"start_date": "2024-03-07", "end_date": "2024-03-09", "reason": "vacation", "username": "Ignace Ormonde"},
#     latest_message={},
#     events=[],
#     paused=False,
#     followup_action=None,
#     active_loop=None,
#     latest_action_name=None,
# )

# # Create an instance of your action
# action = ActionApplyLeave()

# # Call the run method of your action
# action.run(dispatcher, tracker, {})