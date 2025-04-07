from setuptools import setup, find_packages

setup(
    name="trip-planner",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'flask==2.0.1',
        'flask-cors==3.0.10',
        'python-dotenv==0.19.0',
        'openai==0.27.8',
        'langchain==0.0.213',
        'langchain-openai==0.0.1'
    ],
    entry_points={
        'console_scripts': [
            'trip-planner=src.app:main'
        ]
    }
)
