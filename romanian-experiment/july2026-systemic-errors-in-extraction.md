# July 2026 rule extraction systemic issues:

## 1 Feature representation and phonemic inventory issues

DiaSim delimits phone segments with a space, and has certain phones defined in symbolDefs.csv. Diacritized symbols can be generatively built by applying diacritics in file (in DiaSim folder) "fullSymbolDiacriticDefs" to phones defined in symbolDefs.csv. 
Although in some cases either the actor or the critic detected issues with treating something as a single phone that would not be either defined in symbolDefs, nor DEFINABLE by applying diacritics to a segment that was (see 2A), in many cases it wasn't. 

Rules are referred to with their unique identifier as labeled by Pardess -- e.g. R2A, etc.

### 1A Incorrect rule formatting or DiaSim. 

Different usage of the same symbol in the syntax of DiaSim's cascades vs. the source can causes errors and must be caught. 



### 1Aii Rightly handled by actor:  $ used by Pardess as syllable boundary vs. $ as comment symbol in DiaSim

Actor rightly detected teh possible error here since DiaSim doesn't represent syllable boundaries and also uses '$' to flag comments. Made appropriate decisions based on available data, e.g. word bound '#' instead of '$' for R7 because all examples were word initial. 

### 1Aiii Failure to understand that spaces delimit phones

R2A and R2B have "ay" and "oy" as inputs; these are two segments but they would be treated as one phone, a phone that is undefined and undefinable. 

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


### 1D alpha feature handling 

DiaSim uses alpha features to indicate that positive or negative concord between the values of two features. Regardless of where the alpha feature is marked (e.g. "αback" is "α" "marking" the feature "back"), this concordance or negative concordance applies for and only for phones prefixed by the same alpha feature, which for the purposes of DiaSim is any symbol before a phone in a feature matrix (bounded by []) other than "-", "+", "!', or "0". For examples of usage of alpha features, see https://github.com/clmarr/DiaSim/wiki/Cascade#alpha-features 

#### IDi  Intersegmental feature mapping via alpha values confused with intrasegmental feature mapping. 

R13C -- two identical vowels coalescing -- actor rightly uses alpha values to capture the coalescence. But it uses just a single alpha value "α", which makes all features concerned equal to EACH OTHER. This will not have the intended effect. This speaks to a lack of understanding of what an α feature does -- it forces the same feature value specification for EVERY occurrence of the same α symbol in a rule. 

Actor: [+syl,αhi,αlo,αback,αround,αtense] [+syl,αhi,αlo,αback,αround,αtense] > [+syl,αhi,αlo,αback,αround,αtense] ∅
Correct: [+syl,αhi,βlo,ɣback,ðround,ɛtense] > ∅ / __ [+syl,αhi,βlo,ɣback,ðround,ɛtense]


### 1E input/output redundancy

Neither actor nor critic seems to understand that having the same feature stipulation in both input and output for the same position is redundant. E.g. "[-cont,-ant,-cor] > [+ant,+lab,-cor]" --> "-cor" is redundant. 

### 1F feature inventory errors

#### 1Fi low 
DiaSim uses "lo" not "low". Both actor and critic can miss this -- e.g. R13B. 

#### 1Fii Rightly detected by actor: non-existent [rep] feature in Pardess 

Pardess uses [rep] to distinguish [r] from [ɾ]. This is not represented in DiaSim's symbolDefs.csv. 
Effectively it is redundant given the feature [cont], which has the same value as it. 
This was rightly detected. 

Lack of feature [rep], which is inverse of the feature [cont] for /r/ ~ /ɾ/ -- rightly detected. 


#### 1Fiii missing relevant info in mapping between phones and features
If the feature settings of one phone don't all become the feature settings for another, it will not become that phone. Not all features are explicated by sources -- e.g. a "k > p" rule could fail to mention that the /k/ is no longer +hi and +back (as in R10Ca), so it wouldn't really become p, but rather pˠ. This is not fatal but is preferable to fix. 

- R10Ca -- rule changes k g ŋ to p b m. In order to do this, [back] and [hi] must be made negative -- but the actor didn't do this, and the critic, rather than fixing this, made a rule that coronalized them instead. 

#### 1Fiv Rightly detected by critic: central vowels as -back 

When Pardess 1990 was written, the feature [front] had not yet been demonstrated, so he provisionally treated central vowels /ɨ/ and /ə/ as [+back]. They are central however, and in DiaSim [-back,-front]. The critic caught this correctly, and solved it by changing the rules to symbol substitutions rather than guessing at the right features -- this is good. 

Fixed correctly: R47A, R49, R50 

#### 1Fv Rightly corrected by critic: accidental inclusion of unintended phones in input to rule 

R18B -- affrication of alveolar stops, by the actor's feature matrix for input, would also hit /ɾ/ which is also [-cont] and alveolar; the critic correctly added the feature "-son" to the feature matrix. 

##### Incomplete fix for 46A

The fix for 46A did change e to ə, but did not change e̯ to ə̯. Since Pardess' rule operates on [-cons] segments, this also applies to the glide /e̯/ that exists at this time. 
This is clear from Pardess' examples: kəme̯ašə > kəmə̯ašə >> cămașă "shirt", etc. 

The fix for this can use a disjunction: {e;e̯} > {ə;ə̯}

However, this is not ideal as it actually only applies to non-stressed variants (per DiaSim notation). Failing to hit the stress variants due to this matter of DiaSim marking stress on syllabic vowels is an acceptable error. But, to dodge it, one could use "[-cons,+front,-hi,-lo] > [-front,0tense]" to make mid vocoids to schwa-quality elements. This is more secure as it applies regardless of stress. 
=


## 2 fidelity issues


### 2A document reading issues

#### 2Ai Wrong parsing of symbol in Pardess by actor

- ɛː mistaken for eː in R2A (not caught by critic)
- ŋ mistaken for rj in R10Cb, "partial assimilation of velars" (caught by critic, but fixed in an idiosyncratic and erroneous way)
- also for R10Cb, m mistaken for nn (not caught by critic)

Doesn't affect rules, but schwa "ə" is clearly misread as "Q" in some places. 

### 2B omission of relevant info in source.

Critic rightly corrected actor's omissions for...

-R4A, vowels on other side of prior and posterior consonants. 
-R13A, -lo (erroneously as -low tho) in first input position. 

### 2C spurious material inserted 

#### 2Ci (...)* inserted on wrong side of context locus by actor -- fixed by critic

For 46A -- the Co is in the POSTERIOR context only, not the prior. Correctly caught by critic -- good job. 

Incorrect context in the actor's rule: "[+lab,-cor] ([+cons])* __ ([+cons])* [+syl,+back]"

Correct context in critic's rule: "[+cons,+ant,-cor] __ ([+cons])* [+syl,+back]"

([+lab,+cons] or [+cons,+ant,-cor] would both be correct for the first element, because he outright calls it a labial.)

## 3 fixes that produce errors

Critic sometimes makes fixes that break the rule and lose its intent. 

- R10Ca, which produces labials from velars, was 'fixed' in a way that erroneously would make the velars instead into coronals (without changing the features [back] and [hi]). It also messed up the correct usage of alpha features ([αnas]) by the actor to capture ŋn > mn vs kt > pt. Note that [-cor] in the output is redundant given that it's also in the input. Failed to fix representation issue for output, which needs specification of [-back,-hi]. [βcont,βnas] should be used since Pardess treats nasals and stops, but DiaSim doesn't -- this means, either nasal and continuant, or not continuant and not nasal (within DiaSim, where nasals *are* continuant). 

Actor: [-cont,-ant,-cor] > [+ant,+lab,-cor,αnas] / [+syl,+stres] __ [+ant,+cor,αnas]
Critic: [-ant,-cor,αnas] > [+ant,+lab,-cor,αnas] / [+syl,+stres] __ [+ant,+cor]
Correct: [βcont,βnas,-ant,-cor] > [+ant,+lab,-back,-hi,αnas,αson] / [+syl,+stres] __ [+ant,+cor,αnas]

- R10Cb, actor's (correct) handling of pretonic conditioning errantly removed by critic; failed to fix output representation issue (same as above). The fix is allegedly a citation sisue which doesn't justify the change made to the rule formalism by the critic. The critic also introduces the same alpha feature redundancy, and messes up the formerly correct usage of alpha features by the actor. Same nasal/continuant issue as above. The critic does rightly correct that this rule IS coronalizing -- but misses that [+distr] is also necessary for alveolars (maybe this should be added into a policy file). [+prim] is actually necessary since [+stres,-prim] is a countertonic, not a tonic. 

Actor: [-cont,-ant,-cor] > [+ant,+cor,αnas] / __ [+ant,+cor,-cont,αnas] (@)* [+syl,+stres]
Critic: [-ant,-cor,αnas] > [+ant,+cor,αnas] / [+syl,-stres] __ [+ant,+cor]
Correct: [βcont,βnas,-ant,-cor] > [+ant,+cor,+distr,αnas,αson] / [+syl,-stres] __ [+ant,+cor,αnas] (@)* [+prim] 

# 4 specific policies for Pardess

rep -> cont

Pardess treats nasals as stops, but DiaSim doesn't. So nasals have to be included as inputs or contexts where he speaks of stops unless he excludes them or says "obstruent stops". 