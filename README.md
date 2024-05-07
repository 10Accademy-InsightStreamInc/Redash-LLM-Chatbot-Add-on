# Overview - Redash-LLM-Chatbot-Add-on
A Redash add-on which integrates PostgreSQL, and OpenAI's GPT with natural language processing and SQL generation to democratize SQL for a non-technical user to seamlessly fetch and visualize data using LLM and query generation.

# Navigation
- [Project Title](#project-title)
- [Description](#description)
- [Business Need](#business-need)
- [Installation Instructions](#installation-instructions)
- [Usage Guidelines](#usage-guidelines)
- [Contributing](#contributing)
- [License](#license)
- [Authors and Acknowledgment](#authors-and-acknowledgment)
- [Changelog](#changelog)
- [Project Tasks](#project-tasks)

# Project Title
Redash-LLM-Chatbot-Add-on for Advanced Data Analytics and Visualization

## Description
This project focuses on developing a Redash chat add-on designed to enhance data analytics by enabling seamless extraction of insights from multiple Redash dashboards and connected databases using natural language queries. It provides a user-friendly interface for non-technical team members to interact with complex SQL queries autonomously, facilitating deeper, actionable insights from business intelligence platforms. This add-on is crucial for transforming data from platforms like YouTube, Slack, and GMeet into strategic decisions.

## Business Need
Organizations require robust tools to navigate vast amounts of data for competitive advantages in digital content trends. This project addresses the need by enabling

- Simplified data querying through natural language.
- Autonomous knowledge discovery from visualized data on dashboards.
- Enhanced decision-making capabilities through easy access to complex data insights.

# Installation Instructions

1. **Prerequisites**
- Docker and docker-compose installed.
- Node.js and npm for running the frontend.
- Python environment for backend setup.

2. **Fork the Repository**
    ```bash
    git clone https://github.com/10Accademy-InsightStreamInc/Redash-LLM-Chatbot-Add-on
    ```
3. **Navigate to the project directory.**
    - Clone the Forked Repository and navigate to the directory

4. **Set Up Python Environment:**

    ```bash
    python -m venv your_env_name
    ```

    Replace `your_env_name` with the desired name for your environment.
    
5. **Activate the Environment:**

    - On Windows:

    ```bash
    .\your_env_name\scripts\activate
    ```

    - On macOS/Linux:

    ```bash
    source your_env_name/bin/activate
    ```

### Install dependencies
```bash
npm install
```
```bash
pip install -r requirements.txt
```
### Start the application using Docker
```bash
docker-compose up --build
```
## Usage Guidelines
To interact with the Redash Chat Add-on

- Login to Redash Dashboard:
- Navigate to http://localhost:5005 and log in.

## Engage with the Chat Interface
Input queries like, "What are the peak viewership times for our latest videos?" The chat add-on processes the question and either displays results from existing SQL queries or generates new SQL queries to fetch the required information.

## Contributing
To contribute to this project:

## Fork the main repository.
- Create your feature branch 
```bash 
git checkout -b feature/your-feature 
```
- Commit your changes 
```bash 
git commit -am 'Add some feature'
```
- Push to the branch 
```bash 
git push origin feature/your-feature
```
- Submit a pull request.

## Code of Conduct
Please adhere to this project's code of conduct, ensure code quality with comments, and include tests for new features.

## License
This project is released under the MIT License. For more details, see the LICENSE.md file.

## Authors and Acknowledgment
Developers: 
Contributors: Full list in CONTRIBUTORS.md.
Acknowledgments: Thanks to 10 Academy for support and resources.

## Changelog (Future Development)
v1.0.0 - Initial release with EDA, enviroment setup and core functionality for querying via natural language integrated within Redash.

## Project Tasks
- Pre Tasks
    - Project Understanding
    - Environment setup
    - EDA analysis
- Task 1: Schema Design - Develop a database schema suitable for handling complex YouTube data analytics.
- Task 2: Backend API Development - Build the backend to process natural language queries and convert them into SQL commands.
- Task 3: Frontend Integration - Implement a user-friendly interface within Redash to facilitate interaction with the chat add-on.
- Task 4: Testing and Validation - Rigorously test the add-on to ensure reliability and performance.
- Task 5: Documentation and Deployment - Complete comprehensive documentation and prepare the project for deployment using Docker.