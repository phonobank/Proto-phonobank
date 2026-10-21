# July 2026 rule extraction systemic issues:

## 1 Feature representation and phonemic inventory issues

DiaSim delimits phone segments with a space, and has certain phones defined in symbolDefs.csv. Diacritized symbols can be generatively built by applying diacritics in file (in DiaSim folder) "fullSymbolDiacriticDefs" to phones defined in symbolDefs.csv. 
Although in some cases either the actor or the critic detected issues with treating something as a single phone that would not be either defined in symbolDefs, nor DEFINABLE by applying diacritics to a segment that was (see 2A), in many cases it wasn't. 

Rules are referred to with their unique identifier as labeled by Pardess -- e.g. R2A, etc.

### 1A Incorrect rule formatting for DiaSim. 

Different usage of the same symbol in the syntax of DiaSim's cascades vs. the source can causes errors and must be caught. 


### 1Aii Rightly handled by actor:  $ used by Pardess as syllable boundary vs. $ as comment symbol in DiaSim

Actor rightly detected the possible error here since DiaSim doesn't represent syllable boundaries and also uses '$' to flag comments. Made appropriate decisions based on available data, e.g. word bound '#' instead of '$' for R7 because all examples were word initial. 

### 1Aiii Failure to understand that spaces delimit phones

And that glides are separate phones: 

- R2A and R2B have "ay" and "oy" as inputs; these are two segments but they would be treated as one phone, a phone that is undefined and undefinable. 

- R53B: "ea" treated as a non-delimited,single phone input-- correct treatment is e̯ as a glide phoneme

### 1Aiv Pardess' "//" 

As Pardess explains, this means "on either side". Neither actor nor critic treat it as such in : R13B, R13D. Unfortunately, the way to handle this is two separate rules: one for the context coming before the mutandum, and one for the context coming after. 

E.g. for a putative rule "X > Y // A", it should be two rules: "X > Y / A __" and "X > Y / __ A". 


### 1B Incorrect phone symbol usage

Pardess uses both "y" and "j" for "j"; this was not picked up and "y" was written like /y/ (front high round vowel), not /j/ (unround front high glide). Seen inː R2A, R2B


### 1C accuracy in symbol usage

#### 1Ci spurious null context "/ __"

Without any reason in the Pardess text, actor makes a void context stipulation "/ __" in R13A. This does nothing but cause errors. Critic kept it. 

#### 1Cii good job on (X)* usage

Actor got this in a number of cases, that (...)* means "any number of repeats of the segmental material parenthesized", with appropriate usage, and that Pardess' "Co" is ([+cons])*. 

#### 1Ciii null symbol

R60 -- extractor uses '0' rather than the correct '∅'. Missed by critic. On R59B and R59C above, '∅' is correctly used, curiously.

#### 1Civ "?" instead of "*" -- caught by critic

-- R47A: actor uses '?' instead of '*' for the "any number of repeats (...)*" construct. Critic corrects it.


#### 1Cv consonantal "C"

The "C" symbol for "consonant", a shorthand, should be replaced with [+cons] or [-syl] as appropriate. But it's left as it is by actor and critic for rule 13F:
[+syl,+hi,-back] > [+long] / __ (C) #

Correct formulation: 
[+syl,+hi,-back] > [+long] / __ ([+cons]) #


### 1D alpha feature handling 

DiaSim uses alpha features to indicate that positive or negative concord between the values of two features. Regardless of where the alpha feature is marked (e.g. "αback" is "α" "marking" the feature "back"), this concordance or negative concordance applies for and only for phones prefixed by the same alpha feature, which for the purposes of DiaSim is any symbol before a phone in a feature matrix (bounded by []) other than "-", "+", "!', or "0". For examples of usage of alpha features, see https://github.com/clmarr/DiaSim/wiki/Cascade#alpha-features 

#### 1Di  Intersegmental feature mapping via alpha values confused with intrasegmental feature mapping. 

R13C -- two identical vowels coalescing -- actor rightly uses alpha values to capture the coalescence. But it uses just a single alpha value "α", which makes all features concerned equal to EACH OTHER. This will not have the intended effect. This speaks to a lack of understanding of what an α feature does -- it forces the same feature value specification for EVERY occurrence of the same α symbol in a rule. 

Actor: [+syl,αhi,αlo,αback,αround,αtense] [+syl,αhi,αlo,αback,αround,αtense] > [+syl,αhi,αlo,αback,αround,αtense] ∅
Correct: [+syl,αhi,βlo,ɣback,ðround,ɛtense] > ∅ / __ [+syl,αhi,βlo,ɣback,ðround,ɛtense]

Same error in R37B for "degemination of identical adjacent vowels" 

Actor-- and, uncritically, also critic, has :

[+syl,αhi,αlo,αback,αround,αtense,αlong] [+syl,αhi,αlo,αback,αround,αtense,αlong] > [+syl,αhi,αlo,αback,αround,αtense,αlong] ∅

Correct -- two rules: 

[+syl,alo,efront,ihi,uround] > ∅ / __ [+syl,alo,efront,ihi,uround,+prim]
[+syl,alo,efront,ihi,uround] > ∅ / [+syl,alo,efront,ihi,uround,+stres] __

R18E total assimilation rule, which calls for alpha feature equalities of each of various features between segments, but NOT of the features to EACH OTHER. This errant rule by the actor imposes the latter:

[-son] [-cont,αant,αcor,αvoi,+delrel] > [-cont,αant,αcor,αvoi,+delrel] [-cont,αant,αcor,αvoi,+delrel]

Correct handling would be this -- in this case, since there is a single output, the alpha feats aren't even necessary: 

[-cont,-son] > [+delrel,-ant,+distr,+cor,-back,-hi] / __ [+cor,-ant,+delrel]


#### 1Dii alpha feature identity used where polarity needed

R41A -- trying to capture a rule that makes l n s into ʎ ɲ ʃ respectively, the actor uses a feature matrix [+ant,+cor,+son,αlat,αnas] for a rule covering the first two. 
However, this would only be true for a segment that is either neither [+lat] and [+nas] (not /l/ or /n/ -- but /r/ would apply!), or both, which doesn't exist. 
This would have worked with the following: [+ant,+cor,+son,αlat,-αnas]. 

Instead of doing that, the critic simplified it into three rules (one s > ʃ , one n >ɲ , one l > ʎ, each with the same context "__ j"). That also works.

### 1E redundancy

#### 1Ei input/output redundancy

Neither actor nor critic seems to understand that having the same feature stipulation in both input and output for the same position is redundant. E.g. "[-cont,-ant,-cor] > [+ant,+lab,-cor]" --> "-cor" is redundant. 

Missed clearly by critic in, e.g., R32, as well.

### 1F feature inventory errors

#### 1Fi low 
DiaSim uses "lo" not "low". Both actor and critic can miss this -- e.g. R13A, R13B, R31A, R32, R33, R35, R36A, R37A, R47B

Actor also misses this in: R28, R47A, R49A

#### 1Fii Rightly detected by actor: non-existent [rep] feature in Pardess 

Pardess uses [rep] to distinguish [r] from [ɾ]. This is not represented in DiaSim's symbolDefs.csv. 
Effectively it is redundant given the feature [cont], which has the same value as it. 
This was rightly detected. 

Lack of feature [rep], which is inverse of the feature [cont] for /r/ ~ /ɾ/ -- rightly detected. 

For R51, this was rightly replaced with r > ɾ rather than having [-rep] on the output side of the arrow.


#### 1Fiii missing relevant info in mapping between phones and features
If the feature settings of one phone don't all become the feature settings for another, it will not become that phone. Not all features are explicated by sources -- e.g. a "k > p" rule could fail to mention that the /k/ is no longer +hi and +back (as in R10Ca), so it wouldn't really become p, but rather pˠ. This is not fatal but is preferable to fix. 

- R10Ca -- rule changes k g ŋ to p b m. In order to do this, [back] and [hi] must be made negative -- but the actor didn't do this, and the critic, rather than fixing this, made a rule that coronalized them instead. 

#### 1Fiv Rightly detected by critic: central vowels as -back 

When Pardess 1990 was written, the feature [front] had not yet been demonstrated, so he provisionally treated central vowels /ɨ/ and /ə/ as [+back]. They are central however, and in DiaSim [-back,-front]. The critic caught this correctly, and solved it by changing the rules to symbol substitutions rather than guessing at the right features -- this is good. 

Fixed correctly: R47A, R49, R50 

#### 1Fv Rightly corrected by critic: accidental inclusion of unintended phones in input to rule 

R18B -- affrication of alveolar stops, by the actor's feature matrix for input, would also hit /ɾ/ which is also [-cont] and alveolar; the critic correctly added the feature "-son" to the feature matrix. 

##### 1Fv.i Incomplete fix for 46A

The fix for R46A did change e to ə, but did not change e̯ to ə̯. Since Pardess' rule operates on [-cons] segments, this also applies to the glide /e̯/ that exists at this time. 
This is clear from Pardess' examples: kəme̯ašə > kəmə̯ašə >> cămașă "shirt", etc. 

The fix for this can use a disjunction: {e;e̯} > {ə;ə̯}

However, this is not ideal as it actually only applies to non-stressed variants (per DiaSim notation). Failing to hit the stress variants due to this matter of DiaSim marking stress on syllabic vowels is an acceptable error. But, to dodge it, one could use "[-cons,+front,-hi,-lo] > [-front,0tense]" to make mid vocoids to schwa-quality elements. This is more secure as it applies regardless of stress. 

##### 1Fv.ii Implicitly missed in 47B 

Rule R47B describes raising of e before a nasal consonant. To capture /e/ regardless of stress (presumably), the actor used the feature matrix [+syl,-back,-low,-hi]. Aside from the errant usage of [-low] (rather than correct [-lo]), this would also hit /ə/. The critic did not correct this.

##### 1Fv.iii R46A and R46B reversal 

In R46A, the actor decided to treat the output of a backing rule upon e/e̯ as truly back, in isolation from other such cases. It almost did so right, using the following rule: 

[+syl,-back] > [+back] / [+lab,-cor] ([+cons])* __ ([+cons])* [+syl,+back]

However, it should have also had [-front] in the output (between > and /). 

(good actor -- good call on treating prior context as labial.)

The critic changed this to specificaly a rule "e > ə", which does not affect stressed ˈe or asyllabic, thus introducing an error.

The actor's policy was errant in the carrythru to R46B however. 
It understood R46B as "Loss of the R46A-derived back/mid vowel before [a]"-- but wrote "ɔ > a / __ a".

This would not work, because /ɔ/ is not the output of R46A -- /ɔ/ is also [+round], [+lab], [-tense].

The critic's fix here is better.

#### 1Fvi feature matrices that do not capture intended phone(s)

The error: using feature matrices that do not have features that correspond to the intended phone(s). This is especially egregious when only one phone is being referred to. 

Example: R45B -- a rule dissimilating "č" (/t͡ʃ/) to /t/ after "š" (/ʃ/). Pardess uses [+delrel,-ant,+cor] on the input side for his rule, but makes it clear he is treating only /t͡ʃ/ as input. 

The actor uses the feature matrix [-ant,+cor,+distr,+cont]. This is truly bizarre. There is no reason for [+cont] to be used for this, as it is not [+cont]. 

In this case (rule R45B), the critic fixes the matter in the most sensible way: just using specific phone symbols: t͡ʃ > t / ʃ __


This error is quite prevalent. The material here will not exhaustively enumerate cases where it occurs. 

Other cases where the critic caught it and responded appropriately: R43, R44


#### 1Fvii Feature matrices that transform null symbols

Feature matrices in the output can only transform -- be aligned to -- a phone or a phone class captured by a feature matrix. They cannot operate on the null symbol. 


Actor error in R20 did this, not caught by critic: 
∅ [+cons] [+son,-cons,-syl] > [+son,-cons,-syl] [+cons] ∅ / [+syl,+stres] __

Critic caught that something was wrong... but not this. 

Best wayis with three rules, given the description of the rule in Pardess: 

∅ > j / [+prim] __ ([+cons])* j 
∅ > w / [+prim] __ ([+cons])* w
[-syl,-cons,ifront] > ∅ / [+prim] [-syl,-cons,ifront] ([+cons])* __

- 

Likewise for the pre-yod gemination rule in R18A 

Actor: [+syl] ∅ [-son,-cont] j > [+syl] [-son,-cont] [-son,-cont] j

Critics use of alpha features wrongly doesn't fix it:
[+syl] ∅ [-son,-cont,αant,αcor,αvoi] j > [+syl] [-son,-cont,αant,αcor,αvoi] [-son,-cont,αant,αcor,αvoi] j

This is the right way:
{t;d;k;ɡ;p;b} > {t t;d d;k k;ɡ ɡ;p p;b b} / [-cons] __ j

## 2 fidelity issues


### 2A document reading issues

#### 2Ai Wrong parsing of symbol in Pardess by actor

- ɛː mistaken for eː in R2A (not caught by critic)

- ŋ mistaken for rj in R10Cb, "partial assimilation of velars" (caught by critic, but fixed in an 
idiosyncratic and erroneous way)

- also for R10Cb, m mistaken for nn (not caught by critic)

- R53A -- /ʃ/ written as š mistaken for s by actor, caught by critic.

- R57: examples make clear Pardess really means e̯ -- the glide -- not e the vowel. Both actor and critic miss this.

Doesn't affect rules, but schwa "ə" is clearly misread as "Q" in some places. 

### 2B omission of relevant info in source.

Critic rightly corrected actor's omissions for...

-R4A, vowels on other side of prior and posterior consonants. 

-R13A, -lo (erroneously as -low tho) in first input position. 

-R23 actor misses the β > g development AFTER u. Critic reinserts i.

-R31A: one or many status of posterior consonant missed by actor, reasserted by critic. However, both missed the restriction that it does not happen before n or mC.

-R32: specificity to ea missed by actor, reinserted by critic

-R33: non-geminateness of posterior nasal context omitted by actor. Fixed by critic.

-R37A: -long omitted by actor. Fixed by critic.

The following bloopers of the actor were missed by the critic: 


- R59A -- Pardess explicitly states the rule does NOT apply after a consonant followed by a liquid. Both actor and critic ignore this.

- R59B -- the source has w̥, with the voiceless diacritic underneath; the actor missed this, the critic didn't notice.

### 2C spurious material inserted 

#### 2Ci (...)* inserted on wrong side of context locus by actor -- fixed by critic

For 46A -- the Co is in the POSTERIOR context only, not the prior. Correctly caught by critic -- good job. 

Incorrect context in the actor's rule: "[+lab,-cor] ([+cons])* __ ([+cons])* [+syl,+back]"

Correct context in critic's rule: "[+cons,+ant,-cor] __ ([+cons])* [+syl,+back]"

([+lab,+cons] or [+cons,+ant,-cor] would both be correct for the first element, because he outright calls it a labial.)

### 2D wrong interpretation

R38 -- Pardess has e becoming the glide e̯, spelling out ea > e̯a. Actor has the glide as /j/ instead of /e̯/. Critic fixed this.

### 2E content hallucination

#### 2Ei actual content replaced with hallucination


R45A -- s > ʃ before "č" /t͡ʃ/ in Pardess -- actor hallucinates this as a pre-yod palatalization rule. No reason for this in Pardess. 

Critic fixes it in the case of R45A

### 2F content non-coverage

Rules that don't cover semantics...

R15 --  Actor makes only these three rules for a general vowel hiatus loss rule: 
o o > oː ∅
e eː > ∅ eː
i eː > ∅ eː

Critic handles this correctly, using alpha features correctly too:

[+syl,-long,αback] > ∅ / [+cons] __ [+syl,+long,+stres,αback]



## 3 changes by critic that produce errors

Critic sometimes makes changes that break the rule and lose its intent. 

### 3A "fixes" that produce errors

- R10Ca, which produces labials from velars, was 'fixed' in a way that erroneously would make the velars instead into coronals (without changing the features [back] and [hi]). It also messed up the correct usage of alpha features ([αnas]) by the actor to capture ŋn > mn vs kt > pt. Note that [-cor] in the output is redundant given that it's also in the input. Failed to fix representation issue for output, which needs specification of [-back,-hi]. [βcont,βnas] should be used since Pardess treats nasals and stops, but DiaSim doesn't -- this means, either nasal and continuant, or not continuant and not nasal (within DiaSim, where nasals *are* continuant). 

Actor: [-cont,-ant,-cor] > [+ant,+lab,-cor,αnas] / [+syl,+stres] __ [+ant,+cor,αnas]
Critic: [-ant,-cor,αnas] > [+ant,+lab,-cor,αnas] / [+syl,+stres] __ [+ant,+cor]
Correct: [βcont,βnas,-ant,-cor] > [+ant,+lab,-back,-hi,αnas,αson] / [+syl,+stres] __ [+ant,+cor,αnas]


### 3B critic "fix" was spurious AND produced error


-- TODO check actor accuracy for the below: 

- R10Cb, actor's (correct) handling of pretonic conditioning errantly removed by critic; failed to fix output representation issue (same as above). The fix is allegedly a citation sisue which doesn't justify the change made to the rule formalism by the critic. The critic also introduces the same alpha feature redundancy, and messes up the formerly correct usage of alpha features by the actor. Same nasal/continuant issue as above. The critic does rightly correct that this rule IS coronalizing -- but misses that [+distr] is also necessary for alveolars (maybe this should be added into a policy file). [+prim] is actually necessary since [+stres,-prim] is a countertonic, not a tonic. 

Actor: [-cont,-ant,-cor] > [+ant,+cor,αnas] / __ [+ant,+cor,-cont,αnas] (@)* [+syl,+stres]
Critic: [-ant,-cor,αnas] > [+ant,+cor,αnas] / [+syl,-stres] __ [+ant,+cor]
Correct: [βcont,βnas,-ant,-cor] > [+ant,+cor,+distr,αnas,αson] / [+syl,-stres] __ [+ant,+cor,αnas] (@)* [+prim] 


- R23 "Degemination of all consonants except [ll],[nn],[rr] (Otero P28)
"

Actor made this rule pair that was massively errant in deleting the second element of ANY pair of obstruents and then the second of ANY non-anterior pair of sonorant consonants:

[-son] [-son] > [-son] ∅
[+son,+cons,-ant] [+son,+cons,-ant] > [+son,+cons,-ant] ∅

Critic tried to save this by using alpha features, but the massive rules used just a single alpha feature, which leads to massive errors since it wrongly implies identical values for all values it's used for (see 1D):

[-son,αcont,αdelrel,αvoi,αant,αcor,αdistr,αlab,αhi,αback] [-son,αcont,αdelrel,αvoi,αant,αcor,αdistr,αlab,αhi,αback] > [-son,αcont,αdelrel,αvoi,αant,αcor,αdistr,αlab,αhi,αback] ∅
[+son,+cons,-ant,αcor,αdistr,αlab,αhi,αback,αlat,αnas] [+son,+cons,-ant,αcor,αdistr,αlab,αhi,αback,αlat,αnas] > [+son,+cons,-ant,αcor,αdistr,αlab,αhi,αback,αlat,αnas] ∅
[+son,+cons,+ant,-cor] [+son,+cons,+ant,-cor] > [+son,+cons,+ant,-cor] ∅

Correct policy would be this:

[-cor,βlab,mnas,+cons] > ∅ / __ [-cor,βlab,mnas,+cons]
[-son,+cor,scont] > ∅ / __ [-son,+cor,scont]

Which emerges from the inventory. One could just list the geminate pairs alternatively.

- R52B -- for a rule changing voiced palatal (postalveolar) affricate d͡ʒ to ʒ before [o] and [u], the actor correctly included the feature [+voi] as part of the input conditioning. The actor's input was this feature matrix: [+delrel,-ant,+voi]. For no apparent reason, the critic replaces this with the following feature matrix: [-son,+delrel,-ant]. [-son] is redundant for [+delrel]; [+voi] is lost and thus this would (wrongly) affect the voiced affricate /t͡ʃ/. Both the actor and, even moreso, critic, got rather sidetracked onwhether a rule 57 exists -- in the blurb under the rule R52B, Pardess oddly goes on about R57A and R57B having "applied only in Daco-Romanian dialects"; this red-herring was likely a typo on his part but does not justify this change at all.



# 4 specific policies for Pardess

rep -> cont

Pardess treats nasals as stops, but DiaSim doesn't. So nasals have to be included as inputs or contexts where he speaks of stops unless he excludes them or says "obstruent stops". 