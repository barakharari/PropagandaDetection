# useful code:

## /ReuterBERT
PropagandaDetection/ReuterBERT/main.ipynb : follows a tutorial which outlines training BERT (or really RoBERTa) from scratch. https://towardsdatascience.com/how-to-train-a-bert-model-from-scratch-72cfce554fc6

## /Data is not useful

## /notebooks
seems to be for preprocessing data for classification. Maybe some preprocessing for BERT/RoBERTa too?

## /scripts

### /aschern_data: individual doccuments that (maybe) are to be supplied to BERT for propaganda classification.

### /result_techniques 
contains text files identifying propaganda along with which text/source the propaganda is from: article_id	span_start	span_end	span	context	label


# PropagandaDetection

- 2016_election_data folder holds data for each candidate seperated into subdirectories and stored as json
- aschern_data folder holds all data as txt files
- orrignal text files can be found in : PropagandaDetection>scripts>aschern_data>meta
    - In each file, every line is a sentance from the orriginal doccument.
- Data used for classification is found in :
    - PropagandaDetection>data>classifier_training_data.csv    (this data is not from kaggle)
    - PropagandaDetection>scripts>classifier_training_data.csv (this data is from kaggle)
