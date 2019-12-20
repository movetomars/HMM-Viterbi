Maia's POS Tagger:

A baseline "most likely tag" solution is implemented in baseline.py.
To execute, enter the following command in the command line with a Python 2 environment enabled:

******************************
python baseline.py data/train data/test
******************************

You should expect accuracy of 94.600% in training, and 94.191% in testing.
Running time on my (very slow) laptop: 14 seconds

A HMM solution using the Viterbi algorithm is implemented in hmm.py.
To execute, enter the following command in the command line with a Python 2 environment enabled:

*******************************
python hmm.py data/train data/test
*******************************

You should expect accuracy of 96.28% in training, and 94.08% in testing (UGH, I know. I can't get it to be better).
Running time on Computer Science servers for BOTH training and testing: ~13 minutes
Training: 9 minutes 23 seconds
Testing: 3 minutes 40 seconds

********************************

Implementation Report:

I was able to implement a baseline tagger that grabbed the most frequent tag for each word in under 10 minutes, but the HMM implementation required an investment of over 50 hours of work, professor time, TA time, and tutoring. This 30,000% increase in time investment enabled me to add a little under 2% to my training accuracy (from ~94.8% to ~96.3%), and a whopping zero to my testing accuracy (from ~94% to...still ~94%). I do have a robust morphological system in place to deal with unknown words, but despite significant improvements to this system, I am not yet able to nudge testing accuracy above 94.08%.

	Morphological improvements make heavy use of English inflection: one can be fairly certain that English words ending in “-ed” are likely to be past tense verbs (VBD), that words ending in “-ing” have a high likelihood of being present progressive tense verbs (VBG), and that words ending in “-er” and “-est” are probably comparative and superlative adjectives, respectively (JJR and JJS). English, being a language with several disparate influences, doesn’t have many strong phonotactic constraints, but very few words that are not proper nouns end in “i” and “o.” Adjectives similarly have some distinctive characteristics, including having their compound forms marked as one word with a hyphen (“-”), as in “best-defined.” “-al” is a productive N → Adj. derivational suffix, as is “-able” for V → Adj. transitions. “-ly” might seem to be the most obvious choice when it comes to recognizing an adverb from its affixes, but one can also look for words ending in “-wise” (“otherwise,” “likewise”). My system also had trouble recognizing a single tokenized apostrophe as the plural possessive marker, as well as recognizing curly brackets as exemplars of their non-curly brethren, so I gave it a little additional help with these tasks. Finally, several English modals end in “-ould,” so although my system did not have a great amount of trouble with these words, I added them as a precaution. 

	Primary sticking points in my implementation came frequently, and progress was made in fits and starts. Even after I understood the theory behind the algorithm, implementing it (and recognizing things I had implemented as elements of the theory) was another skill entirely. I ran into especial problems using logarithmic probabilities, because while zeroes are less of a problem when calculating logarithmically, this creates more confusion in the calculation (let me explain - when adding the transition probability, the emission probability, and a value from the previous Viterbi column, one cannot simply add all three of these values together and trust them to weigh against other values properly. For example, if one calculation comes to -4.30 but two of the values are zero, one cannot say that this tag is more likely than a tag whose calculation came to -8 but where all three values were contributing to this total. This introduced the need for calculating the number of non-zero values (among emission, transition, and previous Viterbi)  and dividing the probability by this number. This calculation was unnecessarily convoluted,  and violated Occam’s Razor (especially for a new programmer — the less straightforward my code got, the more errors crept in, and the harder these were to isolate and debug). I ended up “fixing” my code when I switched away from logarithmic calculations and was able to reduce my code by at least 15 lines. I was also originally calculating word indices from 1 and all other indices from 0, which introduced several ill-advised index subtractions and unnecessary conditionals (and yes, these were causing errors; I do not remember why I chose to do this originally). Editing my code for simplicity was actually a huge step toward getting unstuck and making it work. Currently, my implementation is working, albeit with slightly lower testing accuracy than I’d like. I’m heartened that my training accuracy is so good, and in line with what one can expect from a solid HMM implementation. 

	A few tagging errors recur repeatedly. The most prominent of these was the VBN - VBD distinction, which arises in English because our language forms verbs in the perfect aspect by pairing the simple past tense form of the verb (VBD) with a separate modal (“had,” “have”). When these tokens are looked at in isolation, the tagger doesn’t know what to do with a simple past-tense form of a verb (say, “studied”) when that verb was tagged more frequently as VBN in the training data (as part of “had studied,” for example). The tagger can’t know the original presence of the modal that marked this verb as perfective, but calculating sequences of tags rather than tags in isolation helps substantially. Another frequent error that comes up is between prepositions (“IN”), particles (“RP”), and adverbs (“RB”). The same token can act as any of these. Take, for example, the word “up” - it can be a preposition in “up the chute,” a particle in “sew it up,” and an adverb in “up 22% from last week.” Who is to say in which context “up” occurs most frequently? In fact, words that are nominally prepositions are used in these other two contexts very frequently, significantly muddying the waters as to what tag they should be labeled with. And that’s not to mention their apparent ambiguous status even in the gold standard: when “up” was used as part of a phrasal verb, it was hand-tagged half the time as a particle and the other half as a preposition in the training data. How is an automated system to tag accurately when even human taggers have a hard time discerning certain grammatical functions? I would be curious to know more about the limitations of current systems, but it’s quite possible that ambiguities like this account for the 3% of accuracy that state-of-the-art systems have yet to achieve.
