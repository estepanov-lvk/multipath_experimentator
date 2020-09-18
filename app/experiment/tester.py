import asyncio

STAGES = [
    "Перезагрузка виртуальных машин (1/9)"
]


class Tester:
    queue = list()

    def __init__(self):
        from app.models import Experiment
        exps = Experiment.query.filter_by(completed = False).all()

        #TODO: sorting
        self.queue = exps

        self.running = False
        self.current_experiment = -1
        self.current_stage = "Выключен"

    def waiting_experiments(self):
        return self.queue
        
    def form_state(self):
        state_msg = {}
        state_msg['current_experiment'] = self.current_experiment.id
        state_msg['current_stage'] = self.current_stage
        return state_msg

    async def run_experiments(self):
        print("Async run of run")
        self.current_experiment = self.queue[0]
        self.current_stage = STAGES[0]
        pass

    def start(self):
        if not self.running:
            self.running = True
            asyncio.run(self.run_experiments())

