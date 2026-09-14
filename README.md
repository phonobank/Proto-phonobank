# Proto-phonobank

This directory contains ongoing work for the construction of Phonobank, which aims to be a repository for sound changes in the histories of any language in the world, integrated with CLDF. It aims to maximize notational consistency. 

The rules table will store all the sound changes. 

We are aiming to have an automated extraction method, assisted by AI, to speed up the task of putting in sound laws from different sources. 
We are using an [actor-critic] dynamic to, as this method is built, ensure in can scale without errors -- and catch early sorts of errors so they may be avoided.

## Present horizons

Present priorities: 

A. Scalable extraction method, building for security with actor-critic dynamic (Clayton)

B. Schema for internal representational structure (Isaac)

        See file: "phonobank_blueprint" (Clayton); "proto_schema" (Isaac)

C. Standardization of annotation (Clayton and Mattis -- see "Misl DiaSim interpolation" file to start)

D. Means to check functional equivalence between different cascades (i.e. that they produce the same results on same data). One rule cascades or multirule cascades.

    D.i -- done July 25, 2026 -- DiaSim.UTILS python script (in DiaSim repo) now provides this ability, with the function "cascMatch". Here: https://github.com/clmarr/DiaSim/blob/gamma/UTILS.py; external usage of this via DiaSim-test-run.py file. 

    D.ii -- synthetic data may be necessary for coverage. Means to generate it? 

E. Integration with CLDF

Status: As of late summer 2026, for (A) current work is being done for a relatively easy task of extracting a Romanian cascade from Pardess' diachronic phonology of Romanian. Work paused due to multiple members involved having to finish dissertation work; resumed in September 2026. Analysis ongoing; unfortunately, it seems that the critic catches errors, but fixes them in ways that break the rules in unexpected ways...


Side objectives: 

- data input from: Kummel's book, Index diachronica; Mielke's data

## Rules table

In the [rules-table] we'll be storing a row for each rule in the relative chronology of sound change [cascade] between an [ancestor] language and a [descendant] language


## Coding decisions

### Etyma and cognacy

Etymon ID -- etyma referenced as (claimed to be) affected by a rule have their unique etymon ID in the pertinent column for that rule
the etymon ID points to a table
each etymon in this table is essentially a tuple: (source lexeme ID, descendant lexeme ID)
each of these lexeme IDs points its semantic concept in concepticon as well

COGNACY between two etyma can be extracted as the truth value for whether they point to the same lexeme as their source in this tuple. 

## Notation


For better cohesion and comparability of sound changes stored in Phonobank, it is ideal to minimize differences in representation and retrieval that arise from sources referring to the same phenomena in different ways. 
E.g. each of the following refers to a sound change that is functionally identical to the others: 

- The sentence "e becomes lax before consonants"
- The SPE-style sound law "e > ɛ / __ C" 
- The same sound law, with SPE-style feature matrices: "e > [-tense] / __ [+cons]" 
- The same sound law, with context treated as input: "eC > ɛC" 
- The same sound law, from a chronologically regressive rather than progressive perspective: "ɛ comes from e before consonants", or "ɛ < e / __ C" etc. 

Notation may differ between various sources on how sound laws are expressed, what symbols are used for sound segments, which features are used (if any) and how they are notated, and how phones are mapped to features. Even in the standardized IPA, there are often many equivalent ways to represent the same phone: e.g. a voiceless labiovelar glide could be "ʍ", "w̥", "ů̯" or even "ɰ̥ʷ". 

A medium-horizon goal is to determine and implement a unified notational convention that is accessible and effectively maps between conventions used in different sources without loss of information. 

DiaSim's conventions are used provisionally at least for the time being: 

- rule notation in DiaSim, largely based on SPE, stipulated here: https://github.com/clmarr/DiaSim/wiki/Cascade

- some notes on feature formatting : https://github.com/clmarr/DiaSim/wiki/Representations#features

- symbols and features in use, and the mapping between them : https://github.com/clmarr/DiaSim/blob/gamma/symbolDefs.csv

- shorthands for phonological classes, delimited by tabs: https://github.com/clmarr/DiaSim/blob/gamma/phonClassShortHands.tsv

- diacritics in use, delimited by "= " -- https://github.com/clmarr/DiaSim/blob/gamma/fullSymbolDiacriticDefs.txt


For purposes of automated extraction, it is useful to explicitly flag this, and when a source explains its own notation, it is useful to flag where it does so. 
For example, in Pardess 1990's treatment of Latin to Romanian relative chronology, pages vii-xii (PDF pages 12-17), and more acutely:
 - vii-x (12-15) for features, symbols, and the mapping between them
 - x (15) for shorthands that can be converted to feature matrices (e.g. C = class of consonantals = [+cons]; W = glides = [-syl,-cons]). 
 - x-xi (15-16) for rule formalisms (e.g. "Co = any number of consonants", which would become "([+cons])+"; {} as disjunction just like in DiaSim, etc.) 
 - xii (17) for morphological features


## Actor-critic dynamic

One LLM [actor] extracts the relative chronology of rules from a PDF. 

The [actor] extracts the rule (input, output, context), etyma the source claims are affected, the source including page number.

The role of the other LLMs, the [critics], is to address extraction [infidelities] -- an [infidelity] is where the content extracted by the actor does not actually faithfully represent what was in the source file.

Separate critics are used for [precision] (checking fidelity of extracted content) and [recall] (checking coverage of extracted content), with a pair for each applied to checking three areas, in order: the sound law formalisms, pages in the source attributed, example etyma described as affected.

A [critic] makes a [corrected] file where infidelities (except for [good-infidelities], see below) are corrected, as well as a [correction-report] that lists every [correction] made.

A [good-infidelity] is one where, in fact, the [actor] was correcting an error in the source. E.g. a typo, or applying a sound law that the source never actually explicates. 

E.g. Pardess has "/ŋn/" for input "/gn/"; this is a rule that could have happened but Pardess never explicated this in the rule description. This rule is unnecessary. The actor extracted a rule whereby "/g/" was the input, and words affected where written with "gn". This is "good" but unfaithful. 

The [critic] notes these "good" [infidelities] by listing them in a separate output file. 

### Signals to critics

For training the critic at this early stage, the following flags are used: 
    "$$!!" signals something should be corrected. 
    "$$:)" signals that the actor made no mistake for the associated rule block. 
