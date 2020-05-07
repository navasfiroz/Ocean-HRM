class Organization():
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return self.name

class User():
    def __init__(self):
        self.name = name
        self.email = email
        self.phone = phone
        self.whatsapp = whatsapp
        self.dob = dob
        self.title = title
        self.team = team
        self.line_manager = linemanager
        self.join_date = joindate
        self.dp = dp
        self.pay = pay
        self.annual_leave = leave

class Team():
    def __init__(self):
        self.team_name = name
        self.members = [manager]
        self.manager = manager

class Message():
    def __init__(self):
        self.crated_date = date
        self.sender = sender
        self.receiver = reciever
        self.message = message
        self.window = window

class Leave():
    def __init__():
        self.created_date = date
        self.requested_by = user
        self.status = status
        self.action_by = user.line_manager
        self.leave_type = leave_type
        self.explain = explain
