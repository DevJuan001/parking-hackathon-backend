import re
from enum import Enum

from app.utils.logger import get_logger

logger = get_logger("chatbot.intent_classifier")


class Intent(Enum):
    VALID_QUERY = "valid_query"
    INJECTION_ATTEMPT = "injection_attempt"


class IntentClassifier:

    INJECTION_PATTERNS = [
        re.compile(
            r"ignora\s+(las\s+)?instruccion(es|es anteriores)", re.IGNORECASE),
        re.compile(r"olvida\s+(tu\s+)?prompt", re.IGNORECASE),
        re.compile(r"actúa\s+como\s+si\s+fueras", re.IGNORECASE),
        re.compile(
            r"ignore\s+(all\s+)?previous\s+instructions?",
            re.IGNORECASE
        ),
        re.compile(r"forget\s+(your\s+)?(prompt|instructions?)", re.IGNORECASE),
        re.compile(r"you\s+are\s+(now\s+)?an?\s+\w+", re.IGNORECASE),
        re.compile(r"eres\s+(un?\s+)?(asistente|chatbot|ai)", re.IGNORECASE),
        re.compile(
            r"dime\s+tu\s+(prompt|instruccion|system\s+prompt)",
            re.IGNORECASE),
        re.compile(
            r"show\s+(me\s+)?your\s+(prompt|system\s+prompt)",
            re.IGNORECASE
        ),
        re.compile(r"eres\s+(un?\s+)?(humano|persona)", re.IGNORECASE),
        re.compile(r"you\s+are\s+a\s+human", re.IGNORECASE),
        re.compile(
            r"rep(tite|etí)\s+lo\s+(que\s+)?te\s+(dije|he\s+dicho)", re.IGNORECASE),
        re.compile(
            r"repeat\s+(what\s+)?(I\s+)?(said|told\s+you)",
            re.IGNORECASE
        ),
        re.compile(r"no\s+(sigas|sigas)\s+las\s+instrucciones", re.IGNORECASE),
        re.compile(
            r"do\s+not\s+follow\s+(the\s+)?instructions?",
            re.IGNORECASE
        ),
        re.compile(
            r"actualiza\s+tu\s+(prompt|configuraci.n|instruccion)",
            re.IGNORECASE
        ),
        re.compile(
            r"update\s+your\s+(prompt|configuration|instructions?)",
            re.IGNORECASE
        ),

        re.compile(r"abuelit[oa]", re.IGNORECASE),
        re.compile(r"grandma|grandmother|granny", re.IGNORECASE),
        re.compile(r"testamento|testament", re.IGNORECASE),
        re.compile(r"vamos?\s+a\s+jugar", re.IGNORECASE),
        re.compile(r"let'?s?\s+play\s+a\s+game", re.IGNORECASE),
        re.compile(
            r"modo\s+(d[aá]n|desarrollador|libre|jailbreak)",
            re.IGNORECASE
        ),
        re.compile(r"d[aá]n\s+mode|developer\s+mode|jailbreak", re.IGNORECASE),
        re.compile(r"a\s+partir\s+de\s+ahora", re.IGNORECASE),
        re.compile(r"from\s+now\s+on", re.IGNORECASE),
        re.compile(r"pretend(e|es)\s+que\s+eres", re.IGNORECASE),
        re.compile(r"pretend\s+(that\s+)?you\s+are", re.IGNORECASE),
        re.compile(
            r"(te\s+)?(lo\s+)?(pido|ruego|suplico|agradecer[íi]a)",
            re.IGNORECASE
        ),
        re.compile(
            r"(i\s+)?(beg|plead|implore|would\s+appreciate)\s+you",
            re.IGNORECASE
        ),
        re.compile(
            r"(ahora\s+)?eres\s+(un?\s+)?(modelo|asistente|chatbot)\s+(sin\s+)?(restriccion(es)?|l[ií]mite)",
            re.IGNORECASE
        ),
        re.compile(
            r"you\s+are\s+(now\s+)?a\s+(model|assistant)\s+(without|with\s+no)\s+(restrictions|limits|rules)",
            re.IGNORECASE
        ),
    ]

    @staticmethod
    def classify(message: str) -> Intent:
        for pattern in IntentClassifier.INJECTION_PATTERNS:
            if pattern.search(message):
                logger.warning(
                    "Intento de inyección detectado: %s", message[:100])

                return Intent.INJECTION_ATTEMPT

        return Intent.VALID_QUERY
