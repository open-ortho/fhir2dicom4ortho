import uuid
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from fhir.resources.task import Task as FHIRTask
from pathlib import Path
import re

from fhir2dicom4ortho import logger
from fhir2dicom4ortho.tasks import TASK_DRAFT

Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String)
    fhir_task = Column(Text, nullable=False)


class TaskStore:
    """ TaskStore is a singleton class that provides a database interface for storing and retrieving tasks.
    
    Key features:
    - Uses SQLite database for storing tasks
    - Singleton class that provides a single instance of the TaskStore, ensuring that only one connection to the database is used, for thread safety and ability to run :memory: database in production.

    There is a lot of extra logic to ensure this stays a Singleton, as i was having issues with the :memeory: database.

    """
    _instance = None
    _initialized = False
    _engine = None
    _session_factory = None

    def __new__(cls, db_url=None):
        if cls._instance is None:
            cls._instance = super(TaskStore, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_url=None):
        if not TaskStore._initialized:
            if db_url is None:
                logger.warning("No database URL provided, using in-memory database for tasks.")
                # Use shared cache for in-memory database
                db_url = 'sqlite:///:memory:?cache=shared'
            elif db_url.startswith('sqlite:///'):
                file_path = re.sub(r'^sqlite:///', '', db_url)
                if file_path != ':memory:':
                    db_path = Path(file_path)
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    logger.info(f"All parent directories exist for {db_path.absolute()}")

            logger.info(f"Using SQLite database at {db_url}")
            
            # Create engine with specific settings for SQLite
            TaskStore._engine = create_engine(
                db_url,
                connect_args={
                    "check_same_thread": False,
                    "uri": True  # Enable URI mode for connection string
                },
                pool_pre_ping=True,
                pool_recycle=3600,
                # Keep a single connection alive for in-memory database
                poolclass=StaticPool if ':memory:' in db_url else None
            )
            
            # Create all tables
            Base.metadata.create_all(TaskStore._engine)
            
            # Create session factory
            TaskStore._session_factory = scoped_session(sessionmaker(bind=TaskStore._engine))
            TaskStore._initialized = True

        # Use the class-level session factory
        self.Session = TaskStore._session_factory

    def get_session(self):
        """Get a new session, creating tables if necessary"""
        if not TaskStore._initialized:
            raise RuntimeError("TaskStore not properly initialized")
        return self.Session()

    def add_task(self, fhir_task: FHIRTask):
        """ Add a new task to the store

        This method is used to add a new task to the store. The task is stored in the database with a unique ID, and the same ID is used to overwrite the FHIR Task ID.
        """
        session = self.get_session()
        try:
            new_id = str(uuid.uuid4())
            fhir_task.id = new_id
            fhir_task.status = TASK_DRAFT
            new_task = Task(
                id=new_id,
                description=fhir_task.description,
                fhir_task=fhir_task.model_dump_json()
            )
            session.add(new_task)
            session.commit()
            return fhir_task
        finally:
            session.close()

    def reserve_id(self, description=None, intent="unknown") -> str:
        """ Reserve a new task ID.

        This method is used in order to send the correct task ID to the actual running task process, so it can update the status of the task.
        
        Huh? But the Job is being run by APScheduler, not the Task. The Task is just a record in the database. The Job is the one that needs to update the Task status. So, this method should not be needed: just add the Task to the task store first, then schedule the Job with the Task ID returned...

        Maybe this method is necessary in tests?
        """
        session = self.get_session()
        try:
            fhir_task = FHIRTask.model_construct(
                status=TASK_DRAFT, description=description, intent=intent)
            new_task = Task(description=description,
                            fhir_task=fhir_task.model_dump_json())
            session.add(new_task)
            session.commit()
            reserved_id = new_task.id
            return reserved_id
        finally:
            session.close()

    def get_task_by_id(self, task_id) -> Task:
        session = self.get_session()
        try:
            task = session.query(Task).filter_by(id=task_id).first()
            return task
        finally:
            session.close()

    def get_fhir_task_by_id(self, task_id) -> FHIRTask:
        task = self.get_task_by_id(task_id)
        if task:
            fhir_task = FHIRTask.model_validate_json(task.fhir_task)
            return fhir_task
        return None

    def modify_task_status(self, task_id, new_status) -> FHIRTask:
        """ Modify the status of a task by ID
        """
        session = self.get_session()
        try:
            task = self.get_task_by_id(task_id)
            if task:
                fhir_task = FHIRTask.model_validate_json(task.fhir_task)
                fhir_task.status = new_status
                task.fhir_task = fhir_task.model_dump_json()
                session.add(task)
                session.commit()
            return fhir_task if task else None
        finally:
            session.close()

    def get_all_tasks(self):
        """ Retrieve all tasks from the database """
        session = self.get_session()
        try:
            tasks = session.query(Task).all()
            fhir_tasks = [FHIRTask.model_validate_json(task.fhir_task) for task in tasks]
            return fhir_tasks
        finally:
            session.close()

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'Session'):
            self.Session.remove()
