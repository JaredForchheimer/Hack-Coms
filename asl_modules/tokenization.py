import re
import spacy

nlp = spacy.load("en_core_web_sm")

SKIP_POS = {"DET", "AUX", "ADP", "PART", "CCONJ", "SCONJ"}

PHRASE_MAP = {
    r"\bhow are you\b": ["HOW", "YOU"],
    r"\bwhat is your name\b": ["YOU", "NAME", "WHAT"],
    r"\bmy name is\b": ["NAME", "ME"],
    r"\bi am\b": ["I"],
    r"\bi'm\b": ["I"],
}

def tokens(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r"[^\w\s'\-]", "", sentence)
    doc = nlp(sentence)

    asl_tokens = []

    for sent in doc.sents:
        clause_tokens = []
        for token in sent:
            if token.is_space or token.is_punct:
                continue
            if token.pos_ in SKIP_POS:
                continue
            if token.pos_ in ["NOUN", "PROPN","PRON", "VERB", "ADJ"]:
                lemma = token.lemma_.upper()
                if lemma not in clause_tokens:
                    clause_tokens.append(lemma)

        # Simple reorder: noun groups before verbs
        verbs = [t for t in clause_tokens if nlp(t.lower())[0].pos_ == "VERB"]
        non_verbs = [t for t in clause_tokens if t not in verbs]
        reordered = non_verbs + verbs
        asl_tokens.extend(reordered)

    seen = set()
    final_tokens = []
    for w in asl_tokens:
        if w not in seen:
            final_tokens.append(w)
            seen.add(w)

    return final_tokens

def reorder_asl(doc, content_words):
    subj, verb, dobj = None, None, None
    for token in doc:
        if token.dep_ == "nsubj":
            subj = token.lemma_.upper()
        elif token.pos_ == "VERB":
            verb = token.lemma_.upper()
        elif token.dep_ in {"dobj", "pobj"}:
            dobj = token.lemma_.upper()

    if dobj and subj and verb:
        # Topic–Comment: OBJECT SUBJECT VERB
        return [dobj, subj, verb]

    return content_words

def main():
    examples = ["Wikipedia is a free online encyclopedia that anyone can edit, and millions already have.Wikipedia's purpose is to benefit readers by presenting information on all branches of knowledge. Hosted by the Wikimedia Foundation, Wikipedia consists of freely editable content, with articles that usually contain numerous links guiding readers to more information.",
"Written collaboratively by volunteers known as Wikipedians, Wikipedia articles can be edited by anyone with Internet access, except in limited cases in which editing is restricted to prevent disruption or vandalism. ",
"Since its creation on January 15, 2001, it has grown into the world's largest reference website, attracting over a billion visitors each month. Wikipedia currently has more than sixty-five million articles in more than 300 languages, including 7,083,956 articles in English, with 115,137 active contributors in the past month."

"Wikipedia's fundamental principles are summarized in its five pillars. While the Wikipedia community has developed many policies and guidelines, new editors do not need to be familiar with them before they start contributing."
]

    for sent in examples:
        print(f"\n🗣️ English: {sent}")
        print(f"🤟 ASL Gloss: {tokens(sent)}")

if __name__ == "__main__":
    main()
