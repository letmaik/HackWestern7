from easygui import *


exercise_name = {
    1: "Push Up",
    2: "Sit Up",
    3: "Run 5km"
}


class Exercise:
    def __init__(self, exercise_id):
        self.exercise = exercise_name[exercise_id]
        self.exercise_file = f'exercises/{exercise_id}.gif'

    def show(self):
        choices = ["Done", "Share"]
        reply = buttonbox(
            self.exercise, image=self.exercise_file, choices=choices)
        return reply
