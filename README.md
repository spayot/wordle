# wordle solver
## Motivation
* build an agent that can play Wordle, with the goal to maximize its score on a given evaluation set.
## Method and Results

### Heuristic
* use $entropy=\sum p * log_2(1 / p)$ estimates how much a given guess is expected to reduce the number of possible solutions (weighted average of all possible outcomes)
* v1: no prior on what are actual possible solutions (all 13k words are equally considered possible)
* v2: only actual possible solutions (2.9k words) are considered.
* v3: add 2 step look-ahead (consider expected entropy given best next guess following original one and guess outcome) (TO DO)
### Results
| v1 - 13k possible solutions | v2 - 2.9k possible solutions | v3: v2 with 2-steps look-ahead |
|:---|:---:|---:|
| ![](images/eval_v1.png)| ![](images/eval_v2.png)| TO DO|

## How to Install
`conda create -f environment.yml`  
`pip install -e .`

## More Resources
* main source of insipiration for this body of work: https://www.3blue1brown.com/lessons/wordle
* related to above: https://jonathanolson.net/experiments/optimal-wordle-solutions 

## About

