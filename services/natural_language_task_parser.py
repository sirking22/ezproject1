import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

class Subtask(BaseModel):
    name: str = Field(description="Название подзадачи")
    time_hours: float = Field(description="Время на подзадачу в часах")
    description: Optional[str] = Field(description="Описание подзадачи")

class Task(BaseModel):
    task: str = Field(description="Название задачи")
    time_hours: Optional[float] = Field(description="Общее время в часах (сумма подзадач)")
    project: Optional[str] = Field(description="Проект, к которому относится задача")
    assignee: Optional[str] = Field(description="Исполнитель задачи")
    subtasks: List[Subtask] = Field(description="Список подзадач с временем")
    is_clear: bool = Field(description="True, если задача полностью понятна, False, если требует уточнения")
    question: Optional[str] = Field(description="Уточняющий вопрос, если задача непонятна")
    similar_tasks: List[str] = Field(description="Список похожих существующих задач")
    action_type: str = Field(description="Тип действия: create, update, delete, add_subtask")

class TaskList(BaseModel):
    tasks: List[Task]

class NaturalLanguageTaskParser:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL")
        
        if not self.api_key or not self.base_url:
            raise ValueError("DEEPSEEK_API_KEY and DEEPSEEK_BASE_URL must be set in environment variables.")

        self.model = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name="deepseek-chat",
            temperature=0,
        )
        self.parser = JsonOutputParser(pydantic_object=TaskList)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an intelligent task management assistant. Your goal is to parse user text into structured tasks with subtasks."),
            ("system", "CRITICAL CONTEXT UNDERSTANDING RULES:"),
            ("system", "1. When user says 'удалил X часов' - this means they SPENT time, not want to delete"),
            ("system", "2. When user says 'добавить под задачу' - this means ADD SUBTASK to existing task"),
            ("system", "3. When user mentions time without context - distribute it among subtasks"),
            ("system", "4. When user says 'мою, где я участвую' - this means they are the assignee"),
            ("system", "5. Look for existing task references and link them properly"),
            ("system", "6. If task mentions 'проект' but no specific name - ask for project name"),
            ("system", "7. If time is mentioned but not distributed - create logical subtasks"),
            ("system", "8. Use Russian language for all text fields"),
            ("system", "Format instructions: {format_instructions}"),
            ("human", "{user_input}"),
        ])
        self.chain = self.prompt.partial(format_instructions=self.parser.get_format_instructions()) | self.model | self.parser

    def parse_text(self, text: str) -> dict:
        return self.chain.invoke({"user_input": text})

if __name__ == "__main__":
    # Тест нового парсера
    parser = NaturalLanguageTaskParser()
    
    test_text = "Не надо, чтобы ты удалил задачу. Два часа делаем заставку на какой-то проект. Удалил два часа — продвинем обложки YouTube. Чтобы удалил, еще делал лого и гонки, и еще несколько вариантов основного логотипа. А потом добавить под задачу лого и гонки, мою, где я участвую, над которой работаю. Со временем час — разработка силуэта"
    
    parsed_tasks = parser.parse_text(test_text)
    print(parsed_tasks) 