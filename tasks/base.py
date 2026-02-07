import random

class TaskTemplate:
    def __init__(
        self,
        id,
        topic,
        level,
        source,
        params,
        task_template,
        solution_template,
        time_minutes=None,
        tikz_template=None,
        formula=None,
    ):
        self.id = id
        self.topic = topic
        self.level = level
        self.source = source
        self.params = params
        self.task_template = task_template
        self.solution_template = solution_template
        self.time_minutes = time_minutes
        self.tikz_template = tikz_template
        self.formula = formula

    def generate(self):
        values = {k: random.choice(v) for k, v in self.params.items()}
        if self.formula:
            values["result"] = self.formula(values)

        task = self.task_template.format(**values)
        solution = self.solution_template.format(**values)
        tikz = self.tikz_template.format(**values) if self.tikz_template else None

        return {
            "topic": self.topic,
            "level": self.level,
            "source": self.source,
            "task": task,
            "solution": solution,
            "tikz": tikz,
            "description": self.source,
            "time_minutes": self.time_minutes or 10,
        }
