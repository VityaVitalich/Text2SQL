## Improvado Text2SQL Homework
Text2SQL is our new product, which we are already actively developing. We understand that this is a rather complex technical product, which is not easy to make quickly and qualitatively 

This terms of reference are not about how to make a cool product, but about the approach and understanding of the task.   


## Overview
Text2SQL system that operates on a ClickHouse database containing dummy marketing data. The system should efficiently demonstrate Text2SQL functionality via prompting and database metadata while also implementing an easy-to-use testing method that non-developers can utilize. Lastly, validate your model's performance with appropriate metrics.


## Homework description
### Prepare a databease for your Text2SQL model.
Generate a dummy marketing data with a variety of tabels and columns. 
The data must be able to answer the following questions:
- How many active agency customers did we have on January 1st, 2022?
- When did we get the highest number of users per day in Q1 2023?
- When did we get the maximum of daily visits on the website in 2022?
- What was the average CPC in Google Ads in April 2023?
- How many LinkedIn clicks did we have in 2022?
- Which platform had the highest CPC in 2022: Google or Bing?
- Get the best ad name by clicks from Facebook, Google, and LinkedIn for 2022.

Import the data into a ClickHouse database and set up the appropriate schema. 

Reccomendation 1: use ClickHouse Cloud (https://clickhouse.cloud) for database creation, as it has a free trial and is easy to set up.

Reccomendation 2: generate dummy data for these questions via GPT. Example of prompt: 
```
Generate Clickhouse query that will create a new table in DB to answer these questions:
{list of questions}
You can add any additional fields into the table to do it more complex.
I need 100 rows in the table.
```

### Implement a Text2SQL system using LLMs. 
Our product relies on the LLM model GPT-4. With prompting, we take the question, create the context, and generate the right SQL. Your task is to make a model based on one of the LLMs (Hugging Face, GPT or something else) and implement the functionality so that your model can correctly make queries and answer the questions we have attached above.

The most important task is to make the right model architecture that will consistently generate context for each step: selecting a table, selecting a column, generating SQL with filters.
The model must recognise and understand all database elements in order to answer users' questions correctly. 

Think very carefully about how your model will generate context for each element.

### Experiment framework.
Once the model is ready - it needs to be tested and continually improved. To do this, you will need to take metrics and assess the current quality of your model, and then, develop a quick and easy way to test it.
Tests can include changing promtas, changing meta-data, reviewing recent logs and so on.

As a lot of the logic of the operation is built on promtas, database metadata - this means that this method needs to be made so simple that any business user can go in to test it. 

Your way of testing will be looked at by the CEO of Improvado. Think about what it needs to be so that he can figure it out.

## Try your best! 
Upon completion of this test task, your output will be crucial in assessing your ability to work with LLMs, ClickHouse databases, and develop practical solutions for tasks like Text2SQL conversion. Good luck, and we look forward to reviewing your work!

## Additional materials
### Frameworks for working with LLM models, which we sometimes look to for good examples.
- Langchain (https://docs.langchain.com/docs/)
- LlamaIndex (https://gpt-index.readthedocs.io/en/latest/) 

### Papers which we can help with mindset. 
- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (https://arxiv.org/pdf/2201.11903.pdf)
- Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs (https://arxiv.org/pdf/2305.03111.pdf)
- Exploring Chain-of-Thought Style Prompting for Text-to-SQL (https://arxiv.org/pdf/2305.14215.pdf)
- SQL-PALM: Improved LLM for TEXT2SQL (https://arxiv.org/pdf/2306.00739.pdf)
