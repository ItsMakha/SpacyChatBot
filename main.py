import spacy
from typing import Final
from telegram import Update
import logging
import random
import sys  # Import sys for logging to stdout
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler, ContextTypes
import re  # Import re for regex operations

# Define states
STATE0 = 0
token: Final = '7456792218:AAE9cibfZ4JbGg1Nsax8ScdD_GRpB2iTlqk'  # Replace with your actual bot token

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


# Placeholder for regex patterns and POVs mapping, define these as needed
povs_c = re.compile(r'\b(I|me|my)\b')  # Example regex pattern for POV change
povs = {'I': 'you', 'me': 'you', 'my': 'your'}  # Example POV mapping

def wh_question_handler(nlp, sentence, verbs_idxs):
    """Handle WH-questions."""
    logging.debug("INVOKING WH-QUESTION HANDLER")
    reply = [sentence[0].text.lower()]
    part = [chunk.text for chunk in sentence.noun_chunks if chunk.root.dep_ == 'nsubj']
    if part: 
        reply.append(part[0])
    reply.append(" ".join([sentence[i].text.lower() for i in verbs_idxs]))
    part = [chunk.text for chunk in sentence.noun_chunks if chunk.root.dep_ == 'dobj']
    if part: 
        reply.append(part[0])
    reply = re.sub(povs_c, lambda match: povs.get(match.group()), " ".join(reply))
    reply = random.choice(["I don't know ", "I can't say "]) + reply
    reply += random.choice([
        ", but I'll try to find out for you. Please check in with me again later.",
        ", but perhaps that's something I'd be able to find out for you. Remind me, if I forget.",
        ". I'll see if I can find out, though. Ask me again sometime."
    ])
    return reply

def yn_question_handler(nlp, sentence, verbs_idxs):
    """Handle Yes/No questions."""
    logging.debug("INVOKING YN-QUESTION HANDLER")
    reply = []
    part = [chunk.text for chunk in sentence.noun_chunks if chunk.root.dep_ == 'nsubj']
    if part:
        reply.append(part[0])
    reply.append(" ".join([sentence[i].text.lower() for i in verbs_idxs]))
    part = [chunk.text for chunk in sentence.noun_chunks if chunk.root.dep_ == 'dobj']
    if part:
        reply.append(part[0])
    reply = re.sub(povs_c, lambda match: povs.get(match.group()), " ".join(reply))
    reply = random.choice([
        "I don't know whether ",
        "I can't say if ",
    ]) + reply
    reply += random.choice([
        " at this very moment. Let me find out.",
        ". I may have to think about this some more.",
    ])
    return reply

def wish_handler(nlp, sentence, verbs_idxs):
    """Handle wishes."""
    logging.debug("INVOKING WISH HANDLER")
    reply = sentence.text
    reply = re.sub(povs_c, lambda match: povs.get(match.group()), reply)
    reply = random.choice([
        "Understood: ",
        "Got it: ",
    ]) + reply
    reply += random.choice([
        " I'll see what I can do.",
        "",
    ])
    return reply

def instruction_handler(nlp, sentence, verbs_idxs):
    """Handle instructions."""
    logging.debug("INVOKING INSTRUCTION HANDLER")
    reply = sentence.text
    reply = re.sub(povs_c, lambda match: povs.get(match.group()), reply)
    reply = random.choice([
        "Understood: ",
        "Got it: ",
    ]) + reply
    reply += random.choice([
        " What do you think about that?",
        " Thanks for sharing.",
    ])
    return reply

def generic_handler(nlp, sentence, verbs_idxs):
    """Handle generic sentences."""
    logging.debug("INVOKING GENERIC HANDLER")
    reply = sentence.text
    reply = re.sub(povs_c, lambda match: povs.get(match.group()), reply)
    return reply

class SentenceTyper(spacy.matcher.Matcher):
    """Determine sentence type."""
    def __init__(self, vocab):
        super().__init__(vocab)
        self.add("WH-QUESTION", [[{"IS_SENT_START": True, "TAG": {"IN": ["WDT", "WP", "WP$", "WRB"]}}]])
        self.add("YN-QUESTION",
                 [[{"IS_SENT_START": True, "TAG": "MD"}, {"POS": {"IN": ["PRON", "PROPN", "DET"]}}],
                 [{"IS_SENT_START": True, "POS": "VERB"}, {"POS": {"IN": ["PRON", "PROPN", "DET"]}}, {"POS": "VERB"}]])
        self.add("INSTRUCTION",
                 [[{"IS_SENT_START": True, "TAG": "VB"}],
                 [{"IS_SENT_START": True, "LOWER": {"IN": ["please", "kindly"]}}, {"TAG": "VB"}]])
        self.add("WISH",
                 [[{"IS_SENT_START": True, "TAG": "PRP"}, {"TAG": "MD"},
                  {"POS": "VERB", "LEMMA": {"IN": ["love", "like", "appreciate"]}}],  
                 [{"IS_SENT_START": True, "TAG": "PRP"}, {"POS": "VERB", "LEMMA": {"IN": ["want", "need", "require"]}}]])

    def __call__(self, *args, **kwargs):
        """Return appropriate sentence type handler."""
        matches = super().__call__(*args, **kwargs)
        if matches:
            match_id, _, _ = matches[0]
            if match_id == self.vocab.strings["WH-QUESTION"]:
                return wh_question_handler
            elif match_id == self.vocab.strings["YN-QUESTION"]:
                return yn_question_handler
            elif match_id == self.vocab.strings["WISH"]:
                return wish_handler
            elif match_id == self.vocab.strings["INSTRUCTION"]:
                return instruction_handler
        return generic_handler

class VerbFinder(spacy.matcher.DependencyMatcher):
    """Find verb phrases."""
    def __init__(self, vocab):
        super().__init__(vocab)
        self.add("VERBPHRASE",
                 [[{"RIGHT_ID": "node0", "RIGHT_ATTRS": {"DEP": "ROOT"}},
                   {"LEFT_ID": "node0", "REL_OP": "<<", "RIGHT_ID": "node1", "RIGHT_ATTRS": {"POS": "PART"}},
                   {"LEFT_ID": "node0", "REL_OP": ">", "RIGHT_ID": "node2", "RIGHT_ATTRS": {"POS": "VERB"}}],
                  [{"RIGHT_ID": "node0", "RIGHT_ATTRS": {"DEP": "ROOT"}},
                   {"LEFT_ID": "node0", "REL_OP": ">", "RIGHT_ID": "node1", "RIGHT_ATTRS": {"TAG": "MD"}}],
                  [{"RIGHT_ID": "node0", "RIGHT_ATTRS": {"DEP": "ROOT"}}]])

    def __call__(self, *args, **kwargs):
        """Return sequence of token ids constituting the verb phrase."""
        verbmatches = super().__call__(*args, **kwargs)
        if verbmatches:
            if len(verbmatches) > 1:
                logging.debug(f"NOTE: VerbFinder found {len(verbmatches)} matches.")
                for verbmatch in verbmatches:
                    logging.debug(verbmatch)
            match_id, token_idxs = verbmatches[0]
            return sorted(token_idxs)

def state0_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Use SpaCy to handle state0."""
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(update.message.text)
    reply = ''

    # Instantiate SentenceTyper and VerbFinder
    sentence_typer = SentenceTyper(nlp.vocab)
    verb_finder = VerbFinder(nlp.vocab)

    # Determine the handler based on sentence type
    handler = sentence_typer(doc)
    verb_idxs = verb_finder(doc)

    # Generate the reply
    reply = handler(nlp, doc, verb_idxs)

    # Send the reply to the user
    update.message.reply_text(reply)
    
    # Stay in the same state
    return STATE0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Announce yourself in a way that suggests the kind of interaction expected."""
    await update.message.reply_text("Hi! I am your bot. How may I be of service?")
    return STATE0

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gracefully exit the conversation."""
    await update.message.reply_text("Thanks for the chat. I'll be off then!")
    return ConversationHandler.END

async def help_command(update, context):
    """Handle help command."""
    await update.message.reply_text("You can start by typing something, or use /cancel to end the chat.")
    return

if __name__ == '__main__':
    """The bot's main message loop is set up and run from here."""
    print("Starting Bot...")
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE0: [MessageHandler(filters.TEXT & ~filters.COMMAND, state0_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('help', help_command)]
    )

    application.add_handler(conv_handler)
    print("Polling...")
    application.run_polling(poll_interval=3)
