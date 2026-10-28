"""Paraphrased guidance and evaluation scenarios informed by the call dataset."""

INTENT_LABELS = [
    "asking_purpose",
    "available_now",
    "busy_requesting_callback",
    "providing_business_context",
    "describing_business_need",
    "requesting_information",
    "expressing_interest",
    "raising_objection",
    "declining",
    "do_not_call",
    "wrong_contact_or_referral",
    "language_or_connection_issue",
    "agreeing_next_step",
    "unclear",
]

INTENT_DEFINITIONS = {
    "asking_purpose": "The prospect asks why the caller reached out or what the call concerns.",
    "available_now": "The prospect indicates they can continue speaking now.",
    "busy_requesting_callback": "The prospect is busy or asks for a call at another time.",
    "providing_business_context": "The prospect describes their role, company, or current approach.",
    "describing_business_need": "The prospect describes a goal, challenge, or desired improvement.",
    "requesting_information": "The prospect asks to receive a report or other information.",
    "expressing_interest": "The prospect shows interest without agreeing to a concrete next step.",
    "raising_objection": "The prospect raises a concern or reason the offer may not fit.",
    "declining": "The prospect declines or says they are not interested.",
    "do_not_call": "The prospect asks not to receive further calls.",
    "wrong_contact_or_referral": "The person reached is not the right contact or refers to another contact.",
    "language_or_connection_issue": "A language mismatch or poor connection prevents a useful conversation.",
    "agreeing_next_step": "The prospect explicitly agrees to a specific action or scheduled conversation.",
    "unclear": "The words do not support a confident intent classification.",
}

GENERAL_GUIDANCE = [
    "Calls may be brief; answer the prospect's immediate concern before continuing.",
    "A request for information is not automatically an agreed meeting or follow-up.",
    "General interest is not a scheduled next step unless the prospect agrees to one.",
    "A callback request is not a confirmed appointment: do not invent a time or promise to call before the prospect confirms it.",
    "For a callback without a prospect-chosen time, ask openly when they are free; do not suggest a time or narrow the choice for them.",
    "If the prospect gives only a broad window such as after lunch, ask when within that window they are free and wait for their answer before confirming.",
    "For requested information, confirm the preferred channel and details; do not assume an email address or claim anything was sent.",
    "For an objection, acknowledge it without arguing or using social proof; ask one gentle follow-up only if the prospect seems open to continuing.",
    "Before asking for a referral or another contact's details, ask permission and make it easy for the prospect to decline.",
    "When the connection or language is a problem, ask whether they prefer to reconnect, continue another way, or end; do not assume email is wanted.",
    "After an agreed meeting, confirm only the agreed details; offer or send a calendar invite only if the prospect agrees to that method.",
    "A request not to be called must be honored without another pitch.",
    "Wrong-contact and referral situations need confirmation, not assumptions.",
    "Use only what the prospect said. Do not invent needs, company claims, promises, or outcomes.",
    "Recorded call outcomes can differ from the conversation; determine intent from turns.",
    "A missing or not-logged outcome is not evidence that the prospect declined.",
    "If speech is ambiguous, choose unclear intent and high uncertainty.",
]

STAGE_EXAMPLES = {
    1: [
        {
            "pattern": "The prospect checks who called or whether the caller reached the right person.",
            "likely_intent": "wrong_contact_or_referral",
            "coaching": "Identify yourself and confirm the contact briefly; accept a correction if they are the wrong person.",
        },
        {
            "pattern": "The person reached says they have left the company or do not handle this area.",
            "likely_intent": "wrong_contact_or_referral",
            "coaching": "Thank them and ask about the appropriate contact only if they seem willing to help.",
        },
    ],
    2: [
        {
            "pattern": "The prospect asks what the call concerns or why they were contacted.",
            "likely_intent": "asking_purpose",
            "coaching": "Give a concise, factual reason for calling and avoid restarting a long pitch.",
        },
        {
            "pattern": "The prospect asks for a report or information to be sent.",
            "likely_intent": "requesting_information",
            "coaching": "Clarify what they are open to receiving; do not treat the request as a meeting agreement.",
        },
    ],
    3: [
        {
            "pattern": "The prospect is busy, in a meeting, or unable to speak now.",
            "likely_intent": "busy_requesting_callback",
            "coaching": "Offer to end the call or ask whether a specific callback time would suit them.",
        },
        {
            "pattern": "The prospect is willing to listen for a short time.",
            "likely_intent": "available_now",
            "coaching": "Keep the explanation brief and let the prospect decide whether to continue.",
        },
    ],
    4: [
        {
            "pattern": "The prospect describes their role, company, or current business context.",
            "likely_intent": "providing_business_context",
            "coaching": "Reflect one relevant detail and ask a focused question about their responsibilities.",
        },
        {
            "pattern": "The prospect redirects the caller to another person or department.",
            "likely_intent": "wrong_contact_or_referral",
            "coaching": "Confirm the suggested contact and avoid assuming that a referral is a sales opportunity.",
        },
    ],
    5: [
        {
            "pattern": "The prospect mentions a business goal, concern, or area they want to improve.",
            "likely_intent": "describing_business_need",
            "coaching": "Use their wording and ask one open question to understand the need more clearly.",
        },
        {
            "pattern": "The prospect gives little detail or says the current approach is working.",
            "likely_intent": "providing_business_context",
            "coaching": "Do not manufacture a problem; ask permission for one relevant follow-up or move on.",
        },
    ],
    6: [
        {
            "pattern": "The prospect declines or says they are not interested.",
            "likely_intent": "declining",
            "coaching": "Acknowledge the answer and end politely if they confirm; do not pressure them.",
        },
        {
            "pattern": "The prospect questions the value, relevance, or timing of the offer.",
            "likely_intent": "raising_objection",
            "coaching": "Respond to the stated concern briefly without arguing or making unsupported claims.",
        },
        {
            "pattern": "The prospect explicitly asks for no further calls.",
            "likely_intent": "do_not_call",
            "coaching": "Stop the pitch, acknowledge the request, and end the call politely.",
        },
    ],
    7: [
        {
            "pattern": "The prospect is open to information or a later conversation.",
            "likely_intent": "requesting_information",
            "coaching": "Confirm the preferred channel or a concrete callback time; distinguish a request from a booked appointment.",
        },
        {
            "pattern": "The prospect expresses interest without committing to a next step.",
            "likely_intent": "expressing_interest",
            "coaching": "Ask whether they would like a specific next step; do not record agreement before they confirm.",
        },
    ],
    8: [
        {
            "pattern": "The prospect explicitly agrees to a meeting or a callback at a specific time.",
            "likely_intent": "agreeing_next_step",
            "coaching": "Summarize only what was actually agreed and confirm the practical details.",
        },
        {
            "pattern": "The call ends without a clear agreement or with incomplete information.",
            "likely_intent": "unclear",
            "coaching": "Close politely and leave the outcome uncertain when the conversation does not support a firmer label.",
        },
    ],
}


def prompt_guidance(stage_number: int) -> dict:
    """Return concise dataset-informed principles and examples for one stage."""
    return {
        "intent_labels": INTENT_LABELS,
        "intent_definitions": INTENT_DEFINITIONS,
        "dataset_principles": GENERAL_GUIDANCE,
        "stage_patterns": STAGE_EXAMPLES.get(stage_number, []),
        "note": (
            "Patterns are paraphrased from the supplied fictional call collection, "
            "not transcript quotes or scripts. They describe possible intent and "
            "do not prove an outcome."
        ),
    }


# Synthetic paraphrases informed by the dataset. These are safe to keep in source
# and test against the prompt without publishing source transcript lines.
EVALUATION_CASES = [
    {"stage": 2, "words": "Please explain the reason for your call first.", "intent": "asking_purpose"},
    {"stage": 3, "words": "I can listen for a couple of minutes.", "intent": "available_now"},
    {"stage": 3, "words": "I am occupied now; try me after lunch.", "intent": "busy_requesting_callback"},
    {"stage": 2, "words": "Send a short overview to my work email.", "intent": "requesting_information"},
    {"stage": 5, "words": "We want to increase repeat orders from current customers.", "intent": "describing_business_need"},
    {"stage": 6, "words": "We already have a provider for that service.", "intent": "raising_objection"},
    {"stage": 6, "words": "Please remove this number and do not call again.", "intent": "do_not_call"},
    {"stage": 1, "words": "I do not manage this area; the operations lead may help.", "intent": "wrong_contact_or_referral"},
    {"stage": 5, "words": "That could be useful, but I have not decided on a meeting.", "intent": "expressing_interest"},
    {"stage": 6, "words": "The audio keeps breaking and I cannot follow you.", "intent": "language_or_connection_issue"},
    {"stage": 7, "words": "Let's meet Tuesday at three with our operations lead.", "intent": "agreeing_next_step"},
    {"stage": 4, "words": "Okay.", "intent": "unclear"},
]
