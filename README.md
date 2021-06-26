# QA-SpaCy
## Overview
Capstone project for San Francisco State University's CSC 620 Course (Natural Language Processing). The goal was to fix and increase the capabilities of an original project outline.

This project is my own implementation and redesign of an automated Simple Factoid Question Answering system, using Wikipedia article body and infobox data to produce a likely answer to a question.
This implementation is divided into three modules, and uses BERT and Word2Vec as the Deep Learning systems involved in answer extraction.
The original use of the Google Knowledge Graph Search API has been altered, and the question classification engine has been turned into a largely rule-based modular mechanism instead.

The original project can be found [here](https://github.com/ekegulskiy/nlp-question-answering)

### Modules
#### 1. Question Pre-processing and Query Generation (qpreprocessing.py)
This module is responsible for processing the raw text of the question and extracting its features
1. Organizes and Displays all linguistic features of the question.
2. Detects named entities such as geographical locations.
3. Classifies the nature of the question based on a set of pre-defined 'question types'
4. Uses rule-based matching to determine frequency-based weights to be used in context extraction in module 3.
5. Decides which query term is the best to send to Google's KGS API for a relevant Wikipedia link

Extra question types can be added as methods in questiontypes.py

#### 2. Data Extraction (dataextraction.py)
This module is responsible for extracting the Wikipedia article of the most relevant subject, as well as its infobox
1. Sends best search term to Google KGS API, and retrieves the Wikipedia url of the highest scoring subject
2. Extracts and cleans article body.
3. Transforms Wikipedia infobox into a dictionary (wkinfobox.py).

#### 3. BERT-SQuAD and Infobox Matching with Word Vectors (answerextraction.py)
This module is responsible for calling 3rd party search engines API and collecting data source objects from them:
1. Using the weights defined in Module 1, calculates chunks of text with the most relevance to the question, returning the top 3.
2. Performs a BERT prediction on the question with each of the most relevant chunks of text and returns the predicted answer. (Mostly innacurate)   
3. For applicable questions (questions with single name or single value answers), matches the question's 'focus word' to a value in the infobox dictionary, and returns the value.


## Installation
### Using Python3
1. Clone this repository
2. With python3 installed on your system, run ```pip install -r requirements.txt```

#### Installing BERT (this section taken from the original project)
Using BERT requires additional installation steps
1. Install python3.6 (http://lavatechtechnology.com/post/install-python-35-36-and-37-on-ubuntu-2004/) and
pip3.6 (https://askubuntu.com/questions/889535/how-to-install-pip-for-python-3-6-on-ubuntu-16-10)
2. install dependant packages: ```pip3.6 install numpy tensorflow==1.15 websocket_server```
3. Clone BERT QA Service project from https://github.com/ekegulskiy/bert-qa-srv.git
4. Obtain uncased_L-12_H-768_A-12.zip package from the repository owner and unzip to some folder. Export BERT_BASE_DIR 
env variable to point to this folder.   
5. Obtain BERT fine-tuned model for question answering from the repository maintainer and store it in the 'output' 
sub-folder of BERT QA Service project.

## Usage
Download the repository from the 'Installing BERT' section, and run:
```python3.6 run_squad.py --vocab_file=$BERT_BASE_DIR/vocab.txt   --bert_config_file=$BERT_BASE_DIR/bert_config.json   --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt   --do_train=False   --train_file=$SQUAD_DIR/train-v1.1.json   --do_predict=True   --predict_file=$SQUAD_DIR/dev-v1.1.json   --train_batch_size=12   --learning_rate=3e-5   --num_train_epochs=2.0   --max_seq_length=384   --doc_stride=128   --output_dir=./output```

Be sure to change environment variables for BERT_BASE_DIR and SQUAD_DIR as needed.

While the BERT Service is running, run:

```python3 run-qa --question='How tall is Mount McKinley?```

## Disclaimer
By no means is this project perfect, there are many flaws and functionalities which could be improved using different models, tools, and algorithms. There might be updates to this code in the future.

## References
Original Project: Eduard Kegulskiy, https://github.com/ekegulskiy

