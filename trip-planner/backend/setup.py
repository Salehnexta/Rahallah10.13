from setuptools import setup, find_packages

setup(
    name="trip-planner",
    version="1.0.6",
    packages=find_packages(),
    install_requires=[
        'flask==2.0.1',
        'flask-cors==3.0.10',
        'python-dotenv==0.19.0',
        'openai>=1.12.0',
        'langchain>=0.1.0',
        'langchain-openai>=0.0.2',
        'langgraph>=0.0.20'
    ],
    entry_points={
        'console_scripts': [
            'trip-planner=src.app:main'
        ]
    }
)
