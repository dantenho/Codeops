import os

from codeops.worker.tools.file_read_tool import FileReadTool
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class CodeAgentsCrew:
    base_path = os.path.dirname(os.path.abspath(__file__))
    agents_config = os.path.join(base_path, 'config', 'agents.yaml')
    tasks_config = os.path.join(base_path, 'config', 'tasks.yaml')

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[FileReadTool()],
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.researcher()
        )

    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['writing_task'],
            agent=self.writer()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, # pylint: disable=no-member
            tasks=self.tasks, # pylint: disable=no-member
            process=Process.sequential,
            verbose=True,
        )
