# Oct 2026 Hebrew extraction report

This file concerns the performance of actor and critic on the extraction of a Hebrew cascade from a pedagogical document by Benjamin Suchard. 
It is organized by issues.

Overall the actor did quite well. The number of errors was comparable to the manual extraction, this time.

## 1 Chronological issues

### 1A Dating

#### 1Ai rules 2.1-2.3

Suchard discusses these as areal changes that postdate Proto-Canaanite. The actor, based on how they were ordered in the document, nevertheless put them first. This was fixed by the critic (good work).

#### 1Aii feeding and other diachronic relations between rules

It is good to explicitly state these, such as the actor did with 2.1 feeding 2.2, and 2.3 counterfeeding 2.2, and 2.6 feeding 2.8, etc.

#### 1Aiii rule 5.1

Suchard mentions that certain aspects of 5.1, the laxing of stressed *e in certain places, had already occurred in Proto-Hebrew. It was therefore placed at the beginning of Proto-Hebrew, because of this and the fact that it is counterbled by rule 3.1.

The actor alluded to this issue, i.e.  *bént > bέnt > bέtt "daughter", in its comments for 3.1, correctly noting that 5.1 was also fed by 3.5, which is actually missed in the manual extraction -- good job. It correctly placed 5.1 after 3.5, and 3.1 after 5.1. Good work!

#### 1Aiv rule 3.9

Manual extraction missed, and the actor caught, that 3.9 should precede 3.4, as Suchard mentions. It also implemented this correctly. Good workǃ

Furthermore, unlike the manual extraction, the actor caught that 3.9 occurs at word boundaries too.


### 1B Stages

## 2 Functionality

### 2A vowel stress

Rule 2.4 concerns both stressed and unstressed short high vowels, but the actor's rule covers only unstressed cases. Critic does not correct this. Low priority for database aggregation, for this sort of issue, though.

Good for actor stressing monosyllables as part of rule 2.5.

In 2.10, the actor -- and not the manual extraction, originally! -- made sure to preserve stress. (good job)

### 2B accounting for idiosyncratic exceptions

Good catch by critic for 4.4 

#### 2Bi 

In rule 2.8, the "Canaanite shift", long *ā becomes *ō except in syllables after w and o.
Multiple rules are necessary to express this.
One can either use an intermediate stage between aː and oː, (ɑː, ɒː etc...), which reverts to /aː/ in these conditions and otherwise passes to oː, or one can have aː be "protected" by becoming a dummy phoneme in these conditoins, and reverting after aː becomes oː elsewhere.
The actor did the latter, fairly impressively, with one exception: it only accounts for *o in prior syllables if separated from the *ā by zero or one consonant, but there could be multiple consonants.
(It also only accounts for *w coming immediately beforehand, but Suchard was a bit vague on this point.)
The critic failed to correct this.

### 2C "sequences of different consonants"

Certain rules operate adjacent to "different consonants". The manual extraction handled this by making geminate consonants into long consonants. The actor took the functional but longer approach of individual alpha rules, or (3.8) disjunctions. Still, well handled. 

(relevant: 2.11, 3.8, 5.1)

{also relevant to not hittin gbegadkefat -- 5.7}

Analogous pair of solutions where geminate consonants are relevant context, as in theunnumberd rule treated as 5.1.1a (for o) for the actor, and labeled 5.0c in the manual extraction. Likewise 5.3

## 3 symbols

Instead of ᵗs, the actor inexplicably writes "ˢs" in the comment for rules 2.2 and 2.3. The critic did not correct this.

## 4 coverage

Good on the actor for noticing that there were changes that were mentioned only in the writeup for exercise 3, and their awkwardness in relation to 2.4 and 2.9 -- and good on the critic for ascertaining these matters.

Good on the actor for noting morphosyntactic developments in comments for the period they pertain to.

Good on actor for accounting for word boundaries where the manual extraction forgot to: 3.4, 3.9 (spuriously on 4.4 but that's acceptable given what theactor was working with)... etc. 

Good on actor for covering the operation of 4.3 in hiatus cases. 

Good for actor catching the incomplete reduction of vowels after gutturals in 4.4.