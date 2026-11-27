# Combined Greek cascade (Bubenik + Horrocks) vs. Olander's "Greek sound changes as regular expressions"

Olander: https://sproghistorie.dk/greek-sound-changes/ (51 ordered regex changes, PIE > Proto-Greek (after
no. 30) > East Ionic; last update 24 June 2023). Ours: `nov26-greek-combined-cfr.txt`.

## Method

Olander's 57 built-in example words were run through his own engine in the browser (the PIE input after his
input clean-up, which already applies laryngeal colouring, and his final output). They were converted to DiaSim
tokens with the same conventions as our cascades (h₁ h₂ h₃ = h χ xʷ; k̑ g̑ = c ɟ; ɛ̄ ɔ̄ = ɛː ɔː; ē ō = eː oː
"spurious diphthongs"; accent = ˈ). The PIE forms went through our combined cascade, and the result at the
`Classical Attic` stage was compared with Olander's output.
Lexicon: `greek-olander-examples-lexicon.txt`. Its gold column holds **Olander's Ionic outputs**, although the header
names our `Classical Attic` stage so that DiaSim scores against that stage.

**Exact matches: 9/57.** Most of the 48 differences fall into the four kinds below. Two were genuine bugs in our
cascade (see the end), and both are now fixed.

## 1. The two cascades describe different dialects (expected)

Olander's endpoint is East Ionic and ours is Attic, so these differences are not errors:

| Feature | Olander (Ionic) | Ours (Attic) | Examples |
|---|---|---|---|
| Psilosis (loss of h-) | applied (no. 51) | h kept | *sēmi- ɛ̄mi- / hɛːmi; *séms ḗs / hems |
| *ā* after e, i, r | ɛ̄ everywhere (no. 44) | Attic reversion to ā (B2.4) | k̑r̥díi̯ah₂: kradíɛ̄ / kradíā |
| *tw*, *ts* | ts > s(s) | Attic tt (B3.5) | *tu̯ŕ̥k̑s: sráks / ttraks |
| 3rd compensatory lengthening | yes (no. 46) | no, Attic (B2.5.3) | *ksénu̯os: ksē̂nos / ksénos |
| Contraction of *tréyes* | Ionic trées | Attic treîs (B2.7) | |

## 2. Rules that Olander states and neither handbook author states (gaps in our sources)

These are the main reason the match rate is low. Bubenik's PIE > Greek section is selective, and Horrocks does not
treat prehistory at all.

| Olander rule | Example (Olander / ours) |
|---|---|
| 1, 13 final *-ms > -ns, *-m > -n* | agrṓs / agróms; agrón / agróm; ḗs / hems |
| 3 dental stop > s before dental stop | kestós / kenttós; ephthós / hepttós |
| 5 *Ku̯ > Kʷ* | thḗr / khḗr |
| 7 early (pre-Greek) vowel contractions | néɛ̄s / néaas; agrɔ̂n / agroːm; agrɔ̂i / agroeː |
| 8 metathesis *TK > KT* | árktos / ratkos |
| 9 vowel epenthesis before initial *r* | érebos / rebos (Bubenik derives érebos from *h₁regʷ- instead) |
| 11 syllabic sonorant before vowel or i̯ > *aR* | ompʰalós / apʰlɔ̂s; baínō / bɔ̂ |
| 14 Cowgill's Law | núks / nopts; ségumai / sebomai |
| 17 voicing and aspiration assimilation of stops | aúksonta / ugsonta; hektós / ekʰtós; krúbdēn / krupʰdɛːn |
| 19 epenthetic b/d in *mr, ml, nr* | memblōk- / memlɔːk-; blṓskō / mlɔːskɔː (Bubenik shows *ml- > bl-* only inside an example) |
| 21 loss of word-final stops | éphere / ephered; ána / anakt |
| 26 simplification of T₁sT₁ | láskō / lakskɔː |
| 28 *dl > gl* | gleûkos / dleukos |
| 34 non-initial *ti > si* | génesis / genetis; dósis / dotis (Horrocks states assibilation only for *-nti*) |
| 36, 37 labial stops > nasal before a nasal | ómma / opma; léleimmai / lelepmai; semnós / sebnos |
| 23 *kʷi̯ > tʃ*; initial *i̯ > zd* | óssomai / opjomai; zugón / hugom (Bubenik: initial j > dj is lexical; we encode j > h) |
| 43 primary *ts > s* | eleuso- / elewtso- |
| *sr- > hr-* (in no. 16) | rhéō / sreɔː |

## 3. Different laryngeal theories

| Point | Olander | Bubenik (ours) | Examples |
|---|---|---|---|
| *iH* before a vowel or glide | *iH₃u̯ > i̯ōu̯*; *tih₃- > ti̯ō- > sō-* | *iHC > ī* (B1.3b) | zōós / diːos; sōtêra / tiːtɛːra |
| Initial *H* before *i̯* | lost (no. 6g) | vocalized before any non-syllabic (B1.3a) | ɛ̄k- / eɛːk |
| Rix's Law, *HR̥-* and *Hu-* | *h₃n̥- > on-*, *h₂u- > au-* | not stated; the H is lost | ompʰalós; aúksonta |
| *R̥H* before a vowel | *tn̥h₂ús > tanús* | not stated | tanús / taus |
| Syllabic liquids | *ra*, but *ar* word-finally and in Rix's-Law contexts | *ra/la* (B1.2b, Bubenik's first-listed reflex) | árktos |

## 4. Accent

Olander encodes the Proto-Greek law of limitation and recessive accent (no. 29) and the σωτῆρα law (no. 47).
Bubenik describes these as synchronic constraints, so they are comment-only in our cascade. Accent-only
differences: pherómenos, thugátēr, krúbdēn, éphere, aúlaks. We do encode Wheeler's and Vendryes' Laws, which
Olander does not. One of Olander's own outputs has two accents (ἄγρῶι), which looks like a bug in his engine.

## Rule-by-rule correspondence (Olander no. → ours)

| Olander | Ours | | Olander | Ours |
|---|---|---|---|---|
| 1 *-ms > -ns* | none | | 27 h- before initial u | none |
| 2 final i̯ after long vowel | none | | 28 *dl > gl* | none |
| 3 *TT > sT* | none | | 29 law of limitation | comment-only |
| 4 *K̑ > K* | INFERRED merger | | 30 *i̯ > h* | B1.2c |
| 5 *Ku̯ > Kʷ* | none | | 31 s between stops | none |
| 6 laryngeals | B1a, B1.3a–d (different details) | | 32 syllabic liquids | B1.2b |
| 7 early contractions | none | | 33 denasalization of ã | not needed (n̥ > a directly) |
| 8 *TK > KT* | none | | 34 *ti > si* | H1a (*-nti* only) |
| 9 epenthesis before r- | none | | 35 labiovelars | B3.6 / H1b |
| 10 devoicing of aspirates | B1.1a | | 36, 37 nasal assimilation | none |
| 11 *R̥ > aR* before vowel | none | | 38 loss of non-initial h, ē ō > ɛ̄ ɔ̄ | B1.1c, E3, B2.5.1 |
| 12 syllabic nasals | B1.2a | | 39 *ln* | B2.5.1b |
| 13 *-m > -n* | none | | 40 late contractions | B2.7 (Olander allows them only in words of more than two syllables) |
| 14 Cowgill | none | | 41 loss of initial/intervocalic w | B2.5.3 |
| 15 βουκόλος law | B1.1b | | 42 sonorant + j | B3.7d |
| 16 *s > h* | B1.1c | | 43 affricates > sibilants | B3.5 (Attic outcome) |
| 17 voicing/aspiration assimilation | none (only B3.2, deaspiration before s) | | 44 *ā > ɛ̄* | B2.4 (+ Attic reversion) |
| 18 dental + glide | B3.5 | | 45 *ns* (CL2) | B2.5.2 |
| 19 epenthetic consonants | none | | 46 postconsonantal w | B2.5.3 (Attic: no lengthening) |
| 20 Osthoff's Law | none | | 47 σωτῆρα law | comment-only |
| 21 loss of final stops | none | | 48 prevocalic shortening | none |
| 22 Grassmann | B3.3 | | 49 *ss > s* | (Attic *t(h)j > s* directly) |
| 23 main palatalization | B3.5, B3.7d | | 50 quantitative metathesis | B4.3 |
| 24 h-fronting | none | | 51 psilosis | Ionic; comment-only |
| 25, 26 *n* before *sC*; T₁sT₁ | none | | | |

**Relative order agrees wherever both cascades contain the rules**: s > h before vocalization of syllabic liquids;
palatalization before loss of labiovelars; labiovelars before ā-fronting; 1st compensatory lengthening before
ā-fronting, 2nd after; contraction before quantitative metathesis.

Our cascade goes on past Classical Attic to Modern Greek (Horrocks), which Olander's does not.

## Bugs in our cascade found by this comparison (fixed)

1. **Palatovelar aspirates:** devoicing came before the palatovelar merger, so \*g̑ʰ became cʰ, a symbol outside the
   inventory (θήρ, ἐκτός, ἔχω). Fix: the merger now comes first.
2. **s > h after an off-glide:** Bubenik says *s* becomes *h* "elsewhere before a vowel". I had restricted it to after
   a vowel, so it missed *h₂áu̯sōs*. Fix: the rule now also applies after *j* and *w*, and medial *h* loss likewise.
   The analogically restored aorist *-s-* of ἔπαυσα is now an expected mismatch in `greek-combined-lexicon.txt`.

After the fixes, the source-based lexicons still score the same as before: Bubenik PIE 24/27 and PG 42/44;
combined Classical Attic 18/19 and Modern Greek 17/19; combined early lexicon 4/4. Every remaining miss is marked
as expected in its lexicon.
