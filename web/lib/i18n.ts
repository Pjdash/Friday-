import type { Lang } from "./types";

/**
 * UI strings. English is the source of truth: the other languages must define every key
 * (enforced by the Messages type), so a missing translation is a compile error, not a blank label.
 *
 * Legal sentences (final decision, zero fee, never share OTP) are NOT translated here. They are the
 * official sentences already published in the knowledge base, copied from mitra/i18n.py, so wording
 * stays official. Keep OFFICIAL in sync with that file.
 *
 * TODO before launch: have a native speaker of each language review the hi/kn/ta strings below.
 */

const en = {
  "app.name": "MitraSeva",
  "app.tagline": "Scheme assistant",
  "nav.home": "Home",
  "nav.check": "Check eligibility",
  "nav.chat": "Ask a question",
  "nav.about": "How it works",
  "nav.menu": "Menu",
  "lang.label": "Language",
  "skip": "Skip to main content",
  "common.optional": "Optional",
  "common.retry": "Try again",
  "common.loading": "Loading…",
  "common.close": "Close",

  "home.title": "Find out which welfare schemes you may qualify for",
  "home.lead":
    "Answer a few questions or ask in your own language. It is free to use. We never ask for an OTP or money.",
  "home.ctaCheck": "Check my eligibility",
  "home.ctaChat": "Ask a question",
  "home.schemes": "Schemes you can check",
  "home.benefit": "Benefit",
  "home.department": "Department",
  "home.checkThis": "Check this scheme",
  "home.loadError": "Could not load the schemes. Please try again.",
  "home.waking": "Getting things ready…",

  "safety.title": "Free of charge. Never share an OTP.",

  "check.title": "Eligibility check",
  "check.lead": "This is a preliminary check. The department makes the final decision.",
  "check.scheme": "Scheme",
  "check.allSchemes": "All schemes",
  "check.sample": "Try a sample person",
  "check.sampleHint": "These are fictional details, just for trying the tool.",
  "check.consent":
    "I agree that the details I enter are used only for this check. They are not saved.",
  "check.submit": "Check eligibility",
  "check.checking": "Checking…",
  "check.reset": "Start over",
  "check.asOf": "Rules in force on",
  "check.asOfHint":
    "Leave this as today unless you want to see how a different date changes the result.",
  "check.advanced": "More options",
  "check.results": "Result",
  "check.fixErrors": "Please correct the highlighted details.",

  "f.age": "Age (years)",
  "f.annual_household_income": "Annual household income (₹)",
  "f.occupation": "Occupation",
  "f.land_holding_acres": "Total household land (acres)",
  "f.residence_type": "Residence",
  "f.category": "Category",
  "f.land.help": "Add up all plots held by the household. Enter 0 if none.",
  "f.select": "Select…",
  "occ.farmer": "Farmer",
  "occ.student": "Student",
  "occ.retired": "Retired",
  "occ.shopkeeper": "Shopkeeper",
  "occ.daily_wage": "Daily-wage worker",
  "occ.other": "Other",
  "cat.general": "General",
  "cat.obc": "OBC",
  "cat.sc": "Scheduled Caste (SC)",
  "cat.st": "Scheduled Tribe (ST)",
  "res.rural": "Rural",
  "res.urban": "Urban",

  "outcome.meets_criteria": "Meets the criteria",
  "outcome.does_not_meet": "Does not meet the criteria",
  "outcome.needs_info": "More information needed",
  "outcome.not_open": "Not open right now",
  "outcome.help.meets_criteria":
    "Based on the details you gave, you appear to qualify. Apply with the documents listed below.",
  "outcome.help.does_not_meet":
    "Based on the details you gave, you do not meet this scheme's criteria. See the reasons below.",
  "outcome.help.needs_info": "A few more details are needed to finish this check.",
  "outcome.help.not_open": "This scheme is not open for applications on this date.",

  "verdict.how": "How we checked",
  "verdict.met": "Met",
  "verdict.notMet": "Not met",
  "verdict.unknown": "Not known",
  "verdict.blockers": "What stops you qualifying",
  "verdict.missing": "Still needed",
  "verdict.documents": "Documents to bring",
  "verdict.mandatory": "Required",
  "verdict.optional": "Optional",
  "verdict.conditional": "Depends on your case",
  "verdict.validity": "Validity",
  "verdict.caveats": "Good to know",
  "verdict.benefit": "Benefit",
  "verdict.department": "Department",
  "verdict.sources": "Based on",
  "verdict.print": "Print checklist",
  "verdict.asOf": "Rules as of {date}",
  "verdict.englishNote": "Rule details are shown in English for now.",
  "verdict.alternativesNote":
    "Some rules offer alternatives. You only need to meet one of them, so one item marked “Not met” does not stop you qualifying.",

  "chat.title": "Ask the assistant",
  "chat.lead":
    "Ask about eligibility, documents, fees, delays or rejections, or tell us if someone asks you for money or an OTP.",
  "chat.placeholder": "Type your question…",
  "chat.send": "Send",
  "chat.thinking": "Looking this up…",
  "chat.you": "You",
  "chat.assistant": "Assistant",
  "chat.suggest1": "Am I eligible for the Vriddhjan pension?",
  "chat.suggest2": "What documents do I need for Kisan Samriddhi Yojana?",
  "chat.suggest3": "Is there any fee to apply?",
  "chat.suggest4": "My application was rejected. What can I do?",
  "chat.needsTitle": "A few details will help",
  "chat.needsSubmit": "Use these details",
  "chat.clear": "Clear chat",
  "chat.sources": "Sources",
  "chat.langNote": "Replies are in the language selected at the top of the page.",
  "chat.empty": "Try one of these:",

  "escalate.fraud_desk.title": "Possible fraud: please report it",
  "escalate.fraud_desk.body":
    "This chat cannot file a report for you. Report it yourself to the fraud desk (MitraSeva Portal > Report Fraud, or a District Collectorate Vigilance Counter). You can also call the National Cyber Crime Helpline 1930.",
  "escalate.human_review.title": "Ask for a human review",
  "escalate.human_review.body":
    "This chat cannot file a request for you. Ask the Block Grievance Desk to review the decision and quote your Application Reference Number (ARN).",
  "escalate.other.title": "Please follow up with an officer",
  "escalate.other.body":
    "This chat cannot take any action for you. Please contact the concerned office directly.",

  "flag.no_consent": "Your saved record was not used because consent is not on file.",
  "flag.unknown_citizen": "We could not find that record.",
  "flag.unsupported_scheme": "That scheme is not covered by this assistant yet.",
  "flag.llm_generated":
    "This answer was written by an AI from the official documents. Please check important details with the department.",
  "flag.llm_not_found": "No matching official document was found for this question.",
  "flag.prompt_injection_removed":
    "Part of your message was ignored because it looked like an instruction to the assistant.",

  "err.generic": "Something went wrong. Please try again.",
  "err.unavailable": "The service is not reachable right now. Please try again in a minute.",
  "err.rate": "Too many requests. Please wait a moment and try again.",
  "err.invalid": "Please check the details you entered.",
  "err.required": "This field is required.",
  "err.number": "Enter a valid number.",
  "err.consent": "Please tick the box to continue.",

  "about.title": "How this works",
  "about.p1":
    "The assistant checks your details against the official scheme guidelines and circulars. It does not guess: every result lists the documents it is based on.",
  "about.p2":
    "Later circulars override older guideline text. The checker applies the rules in force on the date shown.",
  "about.privacy.title": "Your privacy",
  "about.privacy.body":
    "We do not store your details. They are sent to the assistant only to produce your answer, and they are not saved in your browser. Do not enter your name, phone number or Aadhaar number: they are not needed.",
  "about.official.title": "Official position",

  "footer.note": "Preliminary guidance only. Not an official decision.",
} as const;

export type MessageKey = keyof typeof en;
type Messages = Record<MessageKey, string>;

const hi: Messages = {
  "app.name": "MitraSeva",
  "app.tagline": "योजना सहायक",
  "nav.home": "मुख्य पृष्ठ",
  "nav.check": "पात्रता जांचें",
  "nav.chat": "सवाल पूछें",
  "nav.about": "यह कैसे काम करता है",
  "nav.menu": "मेनू",
  "lang.label": "भाषा",
  "skip": "मुख्य सामग्री पर जाएँ",
  "common.optional": "वैकल्पिक",
  "common.retry": "फिर कोशिश करें",
  "common.loading": "लोड हो रहा है…",
  "common.close": "बंद करें",

  "home.title": "जानिए आप किन कल्याणकारी योजनाओं के पात्र हो सकते हैं",
  "home.lead":
    "कुछ सवालों के जवाब दें या अपनी भाषा में पूछें। यह सेवा मुफ़्त है। हम कभी OTP या पैसे नहीं मांगते।",
  "home.ctaCheck": "मेरी पात्रता जांचें",
  "home.ctaChat": "सवाल पूछें",
  "home.schemes": "जिन योजनाओं की जांच आप कर सकते हैं",
  "home.benefit": "लाभ",
  "home.department": "विभाग",
  "home.checkThis": "इस योजना की जांच करें",
  "home.loadError": "योजनाएँ लोड नहीं हो सकीं। कृपया फिर कोशिश करें।",
  "home.waking": "सेवा तैयार हो रही है…",

  "safety.title": "बिल्कुल मुफ़्त। OTP किसी को न बताएँ।",

  "check.title": "पात्रता जांच",
  "check.lead": "यह केवल प्रारंभिक जांच है। अंतिम निर्णय संबंधित विभाग लेता है।",
  "check.scheme": "योजना",
  "check.allSchemes": "सभी योजनाएँ",
  "check.sample": "नमूना व्यक्ति आज़माएँ",
  "check.sampleHint": "ये काल्पनिक विवरण हैं, सिर्फ़ टूल आज़माने के लिए।",
  "check.consent":
    "मैं सहमत हूँ कि मेरे दिए विवरण का उपयोग केवल इस जांच के लिए होगा। वे सहेजे नहीं जाते।",
  "check.submit": "पात्रता जांचें",
  "check.checking": "जांच हो रही है…",
  "check.reset": "फिर से शुरू करें",
  "check.asOf": "इस तारीख़ के नियम",
  "check.asOfHint":
    "आज की तारीख़ रहने दें, जब तक आप यह न देखना चाहें कि किसी और तारीख़ पर नतीजा कैसे बदलता है।",
  "check.advanced": "और विकल्प",
  "check.results": "नतीजा",
  "check.fixErrors": "कृपया चिह्नित जानकारी ठीक करें।",

  "f.age": "आयु (वर्ष)",
  "f.annual_household_income": "वार्षिक पारिवारिक आय (₹)",
  "f.occupation": "व्यवसाय",
  "f.land_holding_acres": "परिवार की कुल ज़मीन (एकड़)",
  "f.residence_type": "निवास",
  "f.category": "वर्ग",
  "f.land.help": "परिवार के सभी खेत जोड़ें। न हो तो 0 लिखें।",
  "f.select": "चुनें…",
  "occ.farmer": "किसान",
  "occ.student": "विद्यार्थी",
  "occ.retired": "सेवानिवृत्त",
  "occ.shopkeeper": "दुकानदार",
  "occ.daily_wage": "दिहाड़ी मज़दूर",
  "occ.other": "अन्य",
  "cat.general": "सामान्य",
  "cat.obc": "ओबीसी",
  "cat.sc": "अनुसूचित जाति (SC)",
  "cat.st": "अनुसूचित जनजाति (ST)",
  "res.rural": "ग्रामीण",
  "res.urban": "शहरी",

  "outcome.meets_criteria": "मानदंड पूरे होते हैं",
  "outcome.does_not_meet": "मानदंड पूरे नहीं होते",
  "outcome.needs_info": "और जानकारी चाहिए",
  "outcome.not_open": "अभी खुली नहीं है",
  "outcome.help.meets_criteria":
    "आपके दिए विवरण के अनुसार आप पात्र लगते हैं। नीचे दिए दस्तावेज़ों के साथ आवेदन करें।",
  "outcome.help.does_not_meet":
    "आपके दिए विवरण के अनुसार आप इस योजना के मानदंड पूरे नहीं करते। नीचे कारण देखें।",
  "outcome.help.needs_info": "जांच पूरी करने के लिए कुछ और जानकारी चाहिए।",
  "outcome.help.not_open": "इस तारीख़ पर यह योजना आवेदन के लिए खुली नहीं है।",

  "verdict.how": "हमने कैसे जांचा",
  "verdict.met": "पूरा",
  "verdict.notMet": "पूरा नहीं",
  "verdict.unknown": "पता नहीं",
  "verdict.blockers": "आपको पात्र होने से क्या रोकता है",
  "verdict.missing": "अभी भी चाहिए",
  "verdict.documents": "साथ ले जाने वाले दस्तावेज़",
  "verdict.mandatory": "ज़रूरी",
  "verdict.optional": "वैकल्पिक",
  "verdict.conditional": "आपके मामले पर निर्भर",
  "verdict.validity": "वैधता",
  "verdict.caveats": "जानने योग्य बातें",
  "verdict.benefit": "लाभ",
  "verdict.department": "विभाग",
  "verdict.sources": "आधार",
  "verdict.print": "सूची प्रिंट करें",
  "verdict.asOf": "{date} के नियम",
  "verdict.englishNote": "नियमों का विवरण अभी अंग्रेज़ी में दिखाया गया है।",
  "verdict.alternativesNote":
    "कुछ नियमों में विकल्प होते हैं। उनमें से कोई एक पूरा करना काफ़ी है, इसलिए “पूरा नहीं” वाली एक बात आपको पात्र होने से नहीं रोकती।",

  "chat.title": "सहायक से पूछें",
  "chat.lead":
    "पात्रता, दस्तावेज़, शुल्क, देरी या अस्वीकृति के बारे में पूछें, या बताएँ कि किसी ने आपसे पैसे या OTP मांगा।",
  "chat.placeholder": "अपना सवाल लिखें…",
  "chat.send": "भेजें",
  "chat.thinking": "देख रहे हैं…",
  "chat.you": "आप",
  "chat.assistant": "सहायक",
  "chat.suggest1": "क्या मैं वृद्धजन पेंशन के लिए पात्र हूँ?",
  "chat.suggest2": "किसान समृद्धि योजना के लिए कौन से दस्तावेज चाहिए?",
  "chat.suggest3": "क्या आवेदन के लिए कोई शुल्क लगता है?",
  "chat.suggest4": "मेरा आवेदन अस्वीकार हो गया, अब क्या करूँ?",
  "chat.needsTitle": "कुछ जानकारी से मदद मिलेगी",
  "chat.needsSubmit": "ये विवरण इस्तेमाल करें",
  "chat.clear": "चैट साफ़ करें",
  "chat.sources": "आधार",
  "chat.langNote": "उत्तर पृष्ठ के ऊपर चुनी गई भाषा में मिलते हैं।",
  "chat.empty": "इनमें से कोई आज़माएँ:",

  "escalate.fraud_desk.title": "संभावित धोखाधड़ी: कृपया शिकायत करें",
  "escalate.fraud_desk.body":
    "यह चैट आपकी ओर से शिकायत दर्ज नहीं कर सकता। fraud_desk पर खुद शिकायत करें (MitraSeva पोर्टल > Report Fraud, या ज़िला कलेक्टोरेट का सतर्कता काउंटर)। आप राष्ट्रीय साइबर क्राइम हेल्पलाइन 1930 पर भी कॉल कर सकते हैं।",
  "escalate.human_review.title": "मानव समीक्षा की माँग करें",
  "escalate.human_review.body":
    "यह चैट आपकी ओर से अनुरोध दर्ज नहीं कर सकता। ब्लॉक शिकायत डेस्क से निर्णय की समीक्षा करने को कहें और अपना आवेदन संदर्भ संख्या (ARN) बताएँ।",
  "escalate.other.title": "कृपया किसी अधिकारी से संपर्क करें",
  "escalate.other.body":
    "यह चैट आपकी ओर से कोई कार्रवाई नहीं कर सकता। कृपया संबंधित कार्यालय से सीधे संपर्क करें।",

  "flag.no_consent": "आपका सहेजा हुआ रिकॉर्ड इस्तेमाल नहीं हुआ क्योंकि सहमति दर्ज नहीं है।",
  "flag.unknown_citizen": "वह रिकॉर्ड नहीं मिला।",
  "flag.unsupported_scheme": "वह योजना अभी इस सहायक में शामिल नहीं है।",
  "flag.llm_generated":
    "यह उत्तर आधिकारिक दस्तावेज़ों के आधार पर एआई ने लिखा है। ज़रूरी बातें विभाग से जांच लें।",
  "flag.llm_not_found": "इस सवाल के लिए कोई मेल खाता आधिकारिक दस्तावेज़ नहीं मिला।",
  "flag.prompt_injection_removed":
    "आपके संदेश का एक हिस्सा अनदेखा किया गया क्योंकि वह सहायक को दिए गए निर्देश जैसा लग रहा था।",

  "err.generic": "कुछ गड़बड़ हो गई। कृपया फिर कोशिश करें।",
  "err.unavailable": "सेवा अभी उपलब्ध नहीं है। कृपया एक मिनट बाद फिर कोशिश करें।",
  "err.rate": "बहुत अधिक अनुरोध हो गए। कृपया थोड़ा रुककर फिर कोशिश करें।",
  "err.invalid": "कृपया दिए गए विवरण जांच लें।",
  "err.required": "यह जानकारी ज़रूरी है।",
  "err.number": "सही संख्या लिखें।",
  "err.consent": "आगे बढ़ने के लिए बॉक्स पर निशान लगाएँ।",

  "about.title": "यह कैसे काम करता है",
  "about.p1":
    "सहायक आपके विवरण को आधिकारिक योजना दिशानिर्देशों और परिपत्रों से मिलाकर जांचता है। यह अंदाज़ा नहीं लगाता: हर नतीजे में उन दस्तावेज़ों की सूची होती है जिन पर वह आधारित है।",
  "about.p2":
    "बाद के परिपत्र पुराने दिशानिर्देशों पर प्राथमिकता रखते हैं। जांच उस तारीख़ पर लागू नियमों से होती है जो दिखाई गई है।",
  "about.privacy.title": "आपकी निजता",
  "about.privacy.body":
    "हम आपके विवरण सहेजते नहीं हैं। वे केवल आपका उत्तर तैयार करने के लिए सहायक को भेजे जाते हैं और आपके ब्राउज़र में सहेजे नहीं जाते। अपना नाम, फ़ोन नंबर या आधार नंबर न लिखें: इनकी ज़रूरत नहीं है।",
  "about.official.title": "आधिकारिक स्थिति",

  "footer.note": "केवल प्रारंभिक मार्गदर्शन। यह आधिकारिक निर्णय नहीं है।",
};

const kn: Messages = {
  "app.name": "MitraSeva",
  "app.tagline": "ಯೋಜನಾ ಸಹಾಯಕ",
  "nav.home": "ಮುಖಪುಟ",
  "nav.check": "ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ",
  "nav.chat": "ಪ್ರಶ್ನೆ ಕೇಳಿ",
  "nav.about": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
  "nav.menu": "ಮೆನು",
  "lang.label": "ಭಾಷೆ",
  "skip": "ಮುಖ್ಯ ವಿಷಯಕ್ಕೆ ಹೋಗಿ",
  "common.optional": "ಐಚ್ಛಿಕ",
  "common.retry": "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
  "common.loading": "ಲೋಡ್ ಆಗುತ್ತಿದೆ…",
  "common.close": "ಮುಚ್ಚಿ",

  "home.title": "ನೀವು ಯಾವ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳಿಗೆ ಅರ್ಹರಾಗಿರಬಹುದು ಎಂದು ತಿಳಿಯಿರಿ",
  "home.lead":
    "ಕೆಲವು ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ ಅಥವಾ ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಕೇಳಿ. ಇದು ಉಚಿತ. ನಾವು ಎಂದಿಗೂ OTP ಅಥವಾ ಹಣ ಕೇಳುವುದಿಲ್ಲ.",
  "home.ctaCheck": "ನನ್ನ ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ",
  "home.ctaChat": "ಪ್ರಶ್ನೆ ಕೇಳಿ",
  "home.schemes": "ನೀವು ಪರಿಶೀಲಿಸಬಹುದಾದ ಯೋಜನೆಗಳು",
  "home.benefit": "ಲಾಭ",
  "home.department": "ಇಲಾಖೆ",
  "home.checkThis": "ಈ ಯೋಜನೆಯನ್ನು ಪರಿಶೀಲಿಸಿ",
  "home.loadError": "ಯೋಜನೆಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  "home.waking": "ಸೇವೆ ಸಿದ್ಧವಾಗುತ್ತಿದೆ…",

  "safety.title": "ಸಂಪೂರ್ಣ ಉಚಿತ. OTP ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",

  "check.title": "ಅರ್ಹತೆ ಪರಿಶೀಲನೆ",
  "check.lead": "ಇದು ಪ್ರಾಥಮಿಕ ಪರಿಶೀಲನೆ ಮಾತ್ರ. ಅಂತಿಮ ನಿರ್ಧಾರವನ್ನು ಸಂಬಂಧಪಟ್ಟ ಇಲಾಖೆ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.",
  "check.scheme": "ಯೋಜನೆ",
  "check.allSchemes": "ಎಲ್ಲಾ ಯೋಜನೆಗಳು",
  "check.sample": "ಮಾದರಿ ವ್ಯಕ್ತಿಯನ್ನು ಪ್ರಯತ್ನಿಸಿ",
  "check.sampleHint": "ಇವು ಕಾಲ್ಪನಿಕ ವಿವರಗಳು, ಉಪಕರಣವನ್ನು ಪ್ರಯತ್ನಿಸಲು ಮಾತ್ರ.",
  "check.consent":
    "ನಾನು ನೀಡುವ ವಿವರಗಳನ್ನು ಈ ಪರಿಶೀಲನೆಗೆ ಮಾತ್ರ ಬಳಸಲು ಒಪ್ಪುತ್ತೇನೆ. ಅವುಗಳನ್ನು ಉಳಿಸಲಾಗುವುದಿಲ್ಲ.",
  "check.submit": "ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ",
  "check.checking": "ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
  "check.reset": "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ",
  "check.asOf": "ಈ ದಿನಾಂಕದ ನಿಯಮಗಳು",
  "check.asOfHint":
    "ಬೇರೆ ದಿನಾಂಕದಲ್ಲಿ ಫಲಿತಾಂಶ ಹೇಗೆ ಬದಲಾಗುತ್ತದೆ ಎಂದು ನೋಡಬೇಕಾದರೆ ಮಾತ್ರ ಬದಲಿಸಿ.",
  "check.advanced": "ಹೆಚ್ಚಿನ ಆಯ್ಕೆಗಳು",
  "check.results": "ಫಲಿತಾಂಶ",
  "check.fixErrors": "ದಯವಿಟ್ಟು ಗುರುತಿಸಿದ ವಿವರಗಳನ್ನು ಸರಿಪಡಿಸಿ.",

  "f.age": "ವಯಸ್ಸು (ವರ್ಷ)",
  "f.annual_household_income": "ವಾರ್ಷಿಕ ಕುಟುಂಬ ಆದಾಯ (₹)",
  "f.occupation": "ಉದ್ಯೋಗ",
  "f.land_holding_acres": "ಕುಟುಂಬದ ಒಟ್ಟು ಜಮೀನು (ಎಕರೆ)",
  "f.residence_type": "ವಾಸಸ್ಥಳ",
  "f.category": "ವರ್ಗ",
  "f.land.help": "ಕುಟುಂಬದ ಎಲ್ಲಾ ಜಮೀನುಗಳನ್ನು ಕೂಡಿಸಿ. ಇಲ್ಲದಿದ್ದರೆ 0 ಬರೆಯಿರಿ.",
  "f.select": "ಆಯ್ಕೆ ಮಾಡಿ…",
  "occ.farmer": "ರೈತ",
  "occ.student": "ವಿದ್ಯಾರ್ಥಿ",
  "occ.retired": "ನಿವೃತ್ತ",
  "occ.shopkeeper": "ಅಂಗಡಿಯವರು",
  "occ.daily_wage": "ದಿನಗೂಲಿ ಕಾರ್ಮಿಕ",
  "occ.other": "ಇತರೆ",
  "cat.general": "ಸಾಮಾನ್ಯ",
  "cat.obc": "ಒಬಿಸಿ",
  "cat.sc": "ಪರಿಶಿಷ್ಟ ಜಾತಿ (SC)",
  "cat.st": "ಪರಿಶಿಷ್ಟ ಪಂಗಡ (ST)",
  "res.rural": "ಗ್ರಾಮೀಣ",
  "res.urban": "ನಗರ",

  "outcome.meets_criteria": "ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸುತ್ತೀರಿ",
  "outcome.does_not_meet": "ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸುವುದಿಲ್ಲ",
  "outcome.needs_info": "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಬೇಕು",
  "outcome.not_open": "ಈಗ ತೆರೆದಿಲ್ಲ",
  "outcome.help.meets_criteria":
    "ನೀವು ನೀಡಿದ ವಿವರಗಳ ಪ್ರಕಾರ ನೀವು ಅರ್ಹರಂತೆ ಕಾಣುತ್ತೀರಿ. ಕೆಳಗಿನ ದಾಖಲೆಗಳೊಂದಿಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.",
  "outcome.help.does_not_meet":
    "ನೀವು ನೀಡಿದ ವಿವರಗಳ ಪ್ರಕಾರ ನೀವು ಈ ಯೋಜನೆಯ ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸುವುದಿಲ್ಲ. ಕೆಳಗೆ ಕಾರಣಗಳನ್ನು ನೋಡಿ.",
  "outcome.help.needs_info": "ಪರಿಶೀಲನೆ ಪೂರ್ಣಗೊಳಿಸಲು ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ಬೇಕು.",
  "outcome.help.not_open": "ಈ ದಿನಾಂಕದಂದು ಈ ಯೋಜನೆ ಅರ್ಜಿಗಳಿಗೆ ತೆರೆದಿಲ್ಲ.",

  "verdict.how": "ನಾವು ಹೇಗೆ ಪರಿಶೀಲಿಸಿದೆವು",
  "verdict.met": "ಪೂರೈಸಿದೆ",
  "verdict.notMet": "ಪೂರೈಸಿಲ್ಲ",
  "verdict.unknown": "ತಿಳಿದಿಲ್ಲ",
  "verdict.blockers": "ನೀವು ಅರ್ಹರಾಗುವುದನ್ನು ತಡೆಯುವುದು",
  "verdict.missing": "ಇನ್ನೂ ಬೇಕಾಗಿರುವುದು",
  "verdict.documents": "ತರಬೇಕಾದ ದಾಖಲೆಗಳು",
  "verdict.mandatory": "ಕಡ್ಡಾಯ",
  "verdict.optional": "ಐಚ್ಛಿಕ",
  "verdict.conditional": "ನಿಮ್ಮ ಪ್ರಕರಣವನ್ನು ಅವಲಂಬಿಸಿದೆ",
  "verdict.validity": "ಮಾನ್ಯತೆ",
  "verdict.caveats": "ತಿಳಿದುಕೊಳ್ಳಬೇಕಾದ ವಿಷಯಗಳು",
  "verdict.benefit": "ಲಾಭ",
  "verdict.department": "ಇಲಾಖೆ",
  "verdict.sources": "ಆಧಾರ",
  "verdict.print": "ಪಟ್ಟಿಯನ್ನು ಮುದ್ರಿಸಿ",
  "verdict.asOf": "{date} ರ ನಿಯಮಗಳು",
  "verdict.englishNote": "ನಿಯಮಗಳ ವಿವರಗಳನ್ನು ಸದ್ಯ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ತೋರಿಸಲಾಗಿದೆ.",
  "verdict.alternativesNote":
    "ಕೆಲವು ನಿಯಮಗಳಲ್ಲಿ ಪರ್ಯಾಯಗಳಿವೆ. ಅವುಗಳಲ್ಲಿ ಒಂದನ್ನು ಪೂರೈಸಿದರೆ ಸಾಕು, ಆದ್ದರಿಂದ “ಪೂರೈಸಿಲ್ಲ” ಎಂದು ಗುರುತಿಸಿದ ಒಂದು ಅಂಶ ನಿಮ್ಮನ್ನು ಅರ್ಹರಾಗುವುದರಿಂದ ತಡೆಯುವುದಿಲ್ಲ.",

  "chat.title": "ಸಹಾಯಕರನ್ನು ಕೇಳಿ",
  "chat.lead":
    "ಅರ್ಹತೆ, ದಾಖಲೆಗಳು, ಶುಲ್ಕ, ವಿಳಂಬ ಅಥವಾ ತಿರಸ್ಕಾರದ ಬಗ್ಗೆ ಕೇಳಿ, ಅಥವಾ ಯಾರಾದರೂ ಹಣ ಅಥವಾ OTP ಕೇಳಿದರೆ ತಿಳಿಸಿ.",
  "chat.placeholder": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ…",
  "chat.send": "ಕಳುಹಿಸಿ",
  "chat.thinking": "ಹುಡುಕಲಾಗುತ್ತಿದೆ…",
  "chat.you": "ನೀವು",
  "chat.assistant": "ಸಹಾಯಕ",
  "chat.suggest1": "ನಾನು ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿಗೆ ಅರ್ಹನೇ?",
  "chat.suggest2": "ಕಿಸಾನ್ ಸಮೃದ್ಧಿ ಯೋಜನೆಗೆ ಯಾವ ದಾಖಲೆಗಳು ಬೇಕು?",
  "chat.suggest3": "ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಶುಲ್ಕ ಇದೆಯೇ?",
  "chat.suggest4": "ನನ್ನ ಅರ್ಜಿ ತಿರಸ್ಕೃತವಾಗಿದೆ, ಈಗ ಏನು ಮಾಡಬೇಕು?",
  "chat.needsTitle": "ಕೆಲವು ವಿವರಗಳು ಸಹಾಯ ಮಾಡುತ್ತವೆ",
  "chat.needsSubmit": "ಈ ವಿವರಗಳನ್ನು ಬಳಸಿ",
  "chat.clear": "ಚಾಟ್ ತೆರವುಗೊಳಿಸಿ",
  "chat.sources": "ಆಧಾರ",
  "chat.langNote": "ಪುಟದ ಮೇಲ್ಭಾಗದಲ್ಲಿ ಆಯ್ಕೆ ಮಾಡಿದ ಭಾಷೆಯಲ್ಲಿ ಉತ್ತರ ಸಿಗುತ್ತದೆ.",
  "chat.empty": "ಇವುಗಳಲ್ಲಿ ಒಂದನ್ನು ಪ್ರಯತ್ನಿಸಿ:",

  "escalate.fraud_desk.title": "ಸಂಭಾವ್ಯ ವಂಚನೆ: ದಯವಿಟ್ಟು ದೂರು ನೀಡಿ",
  "escalate.fraud_desk.body":
    "ಈ ಚಾಟ್ ನಿಮ್ಮ ಪರವಾಗಿ ದೂರು ದಾಖಲಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. fraud_desk ಗೆ ನೀವೇ ದೂರು ನೀಡಿ (MitraSeva ಪೋರ್ಟಲ್ > Report Fraud, ಅಥವಾ ಜಿಲ್ಲಾಧಿಕಾರಿ ಕಚೇರಿಯ ವಿಜಿಲೆನ್ಸ್ ಕೌಂಟರ್). ರಾಷ್ಟ್ರೀಯ ಸೈಬರ್ ಕ್ರೈಂ ಸಹಾಯವಾಣಿ 1930 ಗೂ ಕರೆ ಮಾಡಬಹುದು.",
  "escalate.human_review.title": "ಮಾನವ ಪರಿಶೀಲನೆಗೆ ಕೋರಿ",
  "escalate.human_review.body":
    "ಈ ಚಾಟ್ ನಿಮ್ಮ ಪರವಾಗಿ ಮನವಿ ಸಲ್ಲಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ಬ್ಲಾಕ್ ಕುಂದುಕೊರತೆ ಡೆಸ್ಕ್‌ಗೆ ನಿರ್ಧಾರವನ್ನು ಪರಿಶೀಲಿಸುವಂತೆ ಕೇಳಿ ಮತ್ತು ನಿಮ್ಮ ಅರ್ಜಿ ಉಲ್ಲೇಖ ಸಂಖ್ಯೆ (ARN) ತಿಳಿಸಿ.",
  "escalate.other.title": "ದಯವಿಟ್ಟು ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ",
  "escalate.other.body":
    "ಈ ಚಾಟ್ ನಿಮ್ಮ ಪರವಾಗಿ ಯಾವುದೇ ಕ್ರಮ ಕೈಗೊಳ್ಳಲು ಸಾಧ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಸಂಬಂಧಪಟ್ಟ ಕಚೇರಿಯನ್ನು ನೇರವಾಗಿ ಸಂಪರ್ಕಿಸಿ.",

  "flag.no_consent": "ನಿಮ್ಮ ಉಳಿಸಿದ ದಾಖಲೆಯನ್ನು ಬಳಸಿಲ್ಲ, ಏಕೆಂದರೆ ಸಮ್ಮತಿ ದಾಖಲಾಗಿಲ್ಲ.",
  "flag.unknown_citizen": "ಆ ದಾಖಲೆ ಸಿಗಲಿಲ್ಲ.",
  "flag.unsupported_scheme": "ಆ ಯೋಜನೆ ಈ ಸಹಾಯಕದಲ್ಲಿ ಇನ್ನೂ ಸೇರಿಲ್ಲ.",
  "flag.llm_generated":
    "ಈ ಉತ್ತರವನ್ನು ಅಧಿಕೃತ ದಾಖಲೆಗಳ ಆಧಾರದ ಮೇಲೆ AI ಬರೆದಿದೆ. ಮುಖ್ಯ ವಿವರಗಳನ್ನು ಇಲಾಖೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
  "flag.llm_not_found": "ಈ ಪ್ರಶ್ನೆಗೆ ಹೊಂದುವ ಅಧಿಕೃತ ದಾಖಲೆ ಸಿಗಲಿಲ್ಲ.",
  "flag.prompt_injection_removed":
    "ನಿಮ್ಮ ಸಂದೇಶದ ಒಂದು ಭಾಗವನ್ನು ಕಡೆಗಣಿಸಲಾಗಿದೆ, ಏಕೆಂದರೆ ಅದು ಸಹಾಯಕಕ್ಕೆ ನೀಡಿದ ಸೂಚನೆಯಂತೆ ಕಾಣುತ್ತಿತ್ತು.",

  "err.generic": "ಏನೋ ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  "err.unavailable": "ಸೇವೆ ಈಗ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಒಂದು ನಿಮಿಷದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  "err.rate": "ಹೆಚ್ಚು ವಿನಂತಿಗಳಾಗಿವೆ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಕಾಯ್ದು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  "err.invalid": "ದಯವಿಟ್ಟು ನೀಡಿದ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
  "err.required": "ಈ ವಿವರ ಅಗತ್ಯ.",
  "err.number": "ಸರಿಯಾದ ಸಂಖ್ಯೆ ಬರೆಯಿರಿ.",
  "err.consent": "ಮುಂದುವರಿಯಲು ಬಾಕ್ಸ್‌ಗೆ ಗುರುತು ಹಾಕಿ.",

  "about.title": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
  "about.p1":
    "ಸಹಾಯಕವು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಅಧಿಕೃತ ಯೋಜನಾ ಮಾರ್ಗಸೂಚಿಗಳು ಮತ್ತು ಸುತ್ತೋಲೆಗಳೊಂದಿಗೆ ಹೋಲಿಸಿ ಪರಿಶೀಲಿಸುತ್ತದೆ. ಇದು ಊಹಿಸುವುದಿಲ್ಲ: ಪ್ರತಿ ಫಲಿತಾಂಶವೂ ಅದು ಆಧಾರಿತವಾಗಿರುವ ದಾಖಲೆಗಳನ್ನು ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ.",
  "about.p2":
    "ನಂತರದ ಸುತ್ತೋಲೆಗಳು ಹಳೆಯ ಮಾರ್ಗಸೂಚಿ ಪಠ್ಯಕ್ಕಿಂತ ಮೇಲುಗೈ ಸಾಧಿಸುತ್ತವೆ. ತೋರಿಸಿದ ದಿನಾಂಕದಂದು ಜಾರಿಯಲ್ಲಿರುವ ನಿಯಮಗಳನ್ನು ಪರಿಶೀಲನೆ ಅನ್ವಯಿಸುತ್ತದೆ.",
  "about.privacy.title": "ನಿಮ್ಮ ಗೌಪ್ಯತೆ",
  "about.privacy.body":
    "ನಾವು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಉಳಿಸುವುದಿಲ್ಲ. ನಿಮ್ಮ ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಮಾತ್ರ ಅವುಗಳನ್ನು ಸಹಾಯಕಕ್ಕೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ ಮತ್ತು ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗುವುದಿಲ್ಲ. ನಿಮ್ಮ ಹೆಸರು, ಫೋನ್ ಸಂಖ್ಯೆ ಅಥವಾ ಆಧಾರ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಬೇಡಿ: ಅವುಗಳ ಅಗತ್ಯವಿಲ್ಲ.",
  "about.official.title": "ಅಧಿಕೃತ ನಿಲುವು",

  "footer.note": "ಪ್ರಾಥಮಿಕ ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ. ಇದು ಅಧಿಕೃತ ನಿರ್ಧಾರವಲ್ಲ.",
};

const ta: Messages = {
  "app.name": "MitraSeva",
  "app.tagline": "திட்ட உதவியாளர்",
  "nav.home": "முகப்பு",
  "nav.check": "தகுதியைச் சரிபார்க்கவும்",
  "nav.chat": "கேள்வி கேளுங்கள்",
  "nav.about": "இது எப்படி செயல்படுகிறது",
  "nav.menu": "பட்டி",
  "lang.label": "மொழி",
  "skip": "முதன்மை உள்ளடக்கத்திற்குச் செல்லவும்",
  "common.optional": "விருப்பத்திற்குரியது",
  "common.retry": "மீண்டும் முயலவும்",
  "common.loading": "ஏற்றுகிறது…",
  "common.close": "மூடு",

  "home.title": "நீங்கள் எந்த நலத்திட்டங்களுக்குத் தகுதி பெறலாம் என்பதை அறியுங்கள்",
  "home.lead":
    "சில கேள்விகளுக்குப் பதிலளிக்கவும் அல்லது உங்கள் மொழியில் கேளுங்கள். இது இலவசம். நாங்கள் ஒருபோதும் OTP அல்லது பணம் கேட்க மாட்டோம்.",
  "home.ctaCheck": "என் தகுதியைச் சரிபார்க்கவும்",
  "home.ctaChat": "கேள்வி கேளுங்கள்",
  "home.schemes": "நீங்கள் சரிபார்க்கக்கூடிய திட்டங்கள்",
  "home.benefit": "பலன்",
  "home.department": "துறை",
  "home.checkThis": "இந்தத் திட்டத்தைச் சரிபார்க்கவும்",
  "home.loadError": "திட்டங்களை ஏற்ற முடியவில்லை. மீண்டும் முயலவும்.",
  "home.waking": "சேவை தயாராகிறது…",

  "safety.title": "முற்றிலும் இலவசம். OTP-ஐ யாரிடமும் பகிர வேண்டாம்.",

  "check.title": "தகுதிச் சரிபார்ப்பு",
  "check.lead":
    "இது ஆரம்பநிலைச் சரிபார்ப்பு மட்டுமே. இறுதி முடிவை சம்பந்தப்பட்ட அரசுத் துறையே எடுக்கும்.",
  "check.scheme": "திட்டம்",
  "check.allSchemes": "அனைத்துத் திட்டங்கள்",
  "check.sample": "மாதிரி நபரை முயலவும்",
  "check.sampleHint": "இவை கற்பனை விவரங்கள், கருவியை முயற்சிக்க மட்டும்.",
  "check.consent":
    "நான் அளிக்கும் விவரங்கள் இந்தச் சரிபார்ப்புக்கு மட்டுமே பயன்படுத்தப்படுவதை ஒப்புக்கொள்கிறேன். அவை சேமிக்கப்படாது.",
  "check.submit": "தகுதியைச் சரிபார்க்கவும்",
  "check.checking": "சரிபார்க்கிறது…",
  "check.reset": "மீண்டும் தொடங்கு",
  "check.asOf": "இந்தத் தேதியின் விதிகள்",
  "check.asOfHint":
    "வேறு தேதியில் முடிவு எப்படி மாறும் என்று பார்க்க விரும்பினால் மட்டும் மாற்றவும்.",
  "check.advanced": "மேலும் விருப்பங்கள்",
  "check.results": "முடிவு",
  "check.fixErrors": "குறிக்கப்பட்ட விவரங்களைச் சரிசெய்யவும்.",

  "f.age": "வயது (ஆண்டுகள்)",
  "f.annual_household_income": "ஆண்டு குடும்ப வருமானம் (₹)",
  "f.occupation": "தொழில்",
  "f.land_holding_acres": "குடும்பத்தின் மொத்த நிலம் (ஏக்கர்)",
  "f.residence_type": "வசிப்பிடம்",
  "f.category": "பிரிவு",
  "f.land.help": "குடும்பத்தின் அனைத்து நிலங்களையும் கூட்டவும். இல்லையென்றால் 0 என எழுதவும்.",
  "f.select": "தேர்ந்தெடுக்கவும்…",
  "occ.farmer": "விவசாயி",
  "occ.student": "மாணவர்",
  "occ.retired": "ஓய்வு பெற்றவர்",
  "occ.shopkeeper": "கடைக்காரர்",
  "occ.daily_wage": "தினக்கூலி",
  "occ.other": "மற்றவை",
  "cat.general": "பொது",
  "cat.obc": "ஓபிசி",
  "cat.sc": "பட்டியல் சாதியினர் (SC)",
  "cat.st": "பழங்குடியினர் (ST)",
  "res.rural": "கிராமப்புறம்",
  "res.urban": "நகர்ப்புறம்",

  "outcome.meets_criteria": "நிபந்தனைகளை நிறைவு செய்கிறீர்கள்",
  "outcome.does_not_meet": "நிபந்தனைகளை நிறைவு செய்யவில்லை",
  "outcome.needs_info": "கூடுதல் தகவல் தேவை",
  "outcome.not_open": "இப்போது திறக்கப்படவில்லை",
  "outcome.help.meets_criteria":
    "நீங்கள் அளித்த விவரங்களின்படி நீங்கள் தகுதியுடையவராகத் தெரிகிறீர்கள். கீழ்க்காணும் ஆவணங்களுடன் விண்ணப்பிக்கவும்.",
  "outcome.help.does_not_meet":
    "நீங்கள் அளித்த விவரங்களின்படி இந்தத் திட்டத்தின் நிபந்தனைகளை நீங்கள் நிறைவு செய்யவில்லை. காரணங்களைக் கீழே பார்க்கவும்.",
  "outcome.help.needs_info": "சரிபார்ப்பை முடிக்க இன்னும் சில தகவல்கள் தேவை.",
  "outcome.help.not_open": "இந்தத் தேதியில் இந்தத் திட்டம் விண்ணப்பங்களுக்குத் திறக்கப்படவில்லை.",

  "verdict.how": "நாங்கள் எப்படிச் சரிபார்த்தோம்",
  "verdict.met": "நிறைவு",
  "verdict.notMet": "நிறைவு இல்லை",
  "verdict.unknown": "தெரியவில்லை",
  "verdict.blockers": "நீங்கள் தகுதி பெறுவதைத் தடுப்பவை",
  "verdict.missing": "இன்னும் தேவையானவை",
  "verdict.documents": "கொண்டு வர வேண்டிய ஆவணங்கள்",
  "verdict.mandatory": "கட்டாயம்",
  "verdict.optional": "விருப்பத்திற்குரியது",
  "verdict.conditional": "உங்கள் நிலையைப் பொறுத்தது",
  "verdict.validity": "செல்லுபடியாகும் காலம்",
  "verdict.caveats": "தெரிந்துகொள்ள வேண்டியவை",
  "verdict.benefit": "பலன்",
  "verdict.department": "துறை",
  "verdict.sources": "அடிப்படை",
  "verdict.print": "பட்டியலை அச்சிடுக",
  "verdict.asOf": "{date} தேதியின் விதிகள்",
  "verdict.englishNote": "விதிகளின் விவரங்கள் தற்போது ஆங்கிலத்தில் காட்டப்படுகின்றன.",
  "verdict.alternativesNote":
    "சில விதிகளில் மாற்று வழிகள் உள்ளன. அவற்றில் ஒன்றை நிறைவு செய்தால் போதும்; எனவே “நிறைவு இல்லை” எனக் குறிக்கப்பட்ட ஒன்று உங்களைத் தகுதி பெறுவதிலிருந்து தடுக்காது.",

  "chat.title": "உதவியாளரிடம் கேளுங்கள்",
  "chat.lead":
    "தகுதி, ஆவணங்கள், கட்டணம், தாமதம் அல்லது நிராகரிப்பு பற்றிக் கேளுங்கள், அல்லது யாராவது பணம் அல்லது OTP கேட்டால் தெரிவியுங்கள்.",
  "chat.placeholder": "உங்கள் கேள்வியை எழுதுங்கள்…",
  "chat.send": "அனுப்பு",
  "chat.thinking": "தேடுகிறது…",
  "chat.you": "நீங்கள்",
  "chat.assistant": "உதவியாளர்",
  "chat.suggest1": "நான் முதியோர் ஓய்வூதியத்திற்குத் தகுதியானவரா?",
  "chat.suggest2": "கிசான் சம்ரித்தி திட்டத்திற்கு என்ன ஆவணங்கள் தேவை?",
  "chat.suggest3": "விண்ணப்பிக்கக் கட்டணம் உண்டா?",
  "chat.suggest4": "என் விண்ணப்பம் நிராகரிக்கப்பட்டது, இப்போது என்ன செய்வது?",
  "chat.needsTitle": "சில விவரங்கள் உதவும்",
  "chat.needsSubmit": "இந்த விவரங்களைப் பயன்படுத்தவும்",
  "chat.clear": "அரட்டையை அழி",
  "chat.sources": "அடிப்படை",
  "chat.langNote": "பக்கத்தின் மேலே தேர்ந்தெடுத்த மொழியில் பதில் கிடைக்கும்.",
  "chat.empty": "இவற்றில் ஒன்றை முயலவும்:",

  "escalate.fraud_desk.title": "சாத்தியமான மோசடி: புகார் அளியுங்கள்",
  "escalate.fraud_desk.body":
    "இந்த அரட்டையால் உங்கள் சார்பில் புகார் பதிவு செய்ய முடியாது. fraud_desk-இல் நீங்களே புகார் அளியுங்கள் (MitraSeva இணையதளம் > Report Fraud, அல்லது மாவட்ட ஆட்சியர் அலுவலக விஜிலன்ஸ் கவுண்டர்). தேசிய இணையக் குற்ற உதவி எண் 1930-க்கும் அழைக்கலாம்.",
  "escalate.human_review.title": "மனித மறுஆய்வைக் கோருங்கள்",
  "escalate.human_review.body":
    "இந்த அரட்டையால் உங்கள் சார்பில் கோரிக்கை பதிவு செய்ய முடியாது. வட்டார குறைதீர் மையத்திடம் முடிவை மறுஆய்வு செய்யுமாறு கேட்டு, உங்கள் விண்ணப்பக் குறிப்பு எண்ணை (ARN) குறிப்பிடுங்கள்.",
  "escalate.other.title": "அதிகாரியைத் தொடர்புகொள்ளுங்கள்",
  "escalate.other.body":
    "இந்த அரட்டையால் உங்கள் சார்பில் எந்த நடவடிக்கையும் எடுக்க முடியாது. சம்பந்தப்பட்ட அலுவலகத்தை நேரடியாகத் தொடர்புகொள்ளுங்கள்.",

  "flag.no_consent":
    "ஒப்புதல் பதிவில் இல்லாததால் உங்கள் சேமிக்கப்பட்ட பதிவு பயன்படுத்தப்படவில்லை.",
  "flag.unknown_citizen": "அந்தப் பதிவு கிடைக்கவில்லை.",
  "flag.unsupported_scheme": "அந்தத் திட்டம் இந்த உதவியாளரில் இன்னும் சேர்க்கப்படவில்லை.",
  "flag.llm_generated":
    "இந்த பதிலை அதிகாரப்பூர்வ ஆவணங்களின் அடிப்படையில் AI எழுதியது. முக்கிய விவரங்களைத் துறையிடம் உறுதிசெய்து கொள்ளுங்கள்.",
  "flag.llm_not_found": "இந்தக் கேள்விக்குப் பொருந்தும் அதிகாரப்பூர்வ ஆவணம் கிடைக்கவில்லை.",
  "flag.prompt_injection_removed":
    "உங்கள் செய்தியின் ஒரு பகுதி உதவியாளருக்கான கட்டளை போலத் தோன்றியதால் புறக்கணிக்கப்பட்டது.",

  "err.generic": "ஏதோ தவறு நேர்ந்தது. மீண்டும் முயலவும்.",
  "err.unavailable": "சேவை இப்போது கிடைக்கவில்லை. ஒரு நிமிடம் கழித்து மீண்டும் முயலவும்.",
  "err.rate": "அதிகமான கோரிக்கைகள். சற்றுக் காத்திருந்து மீண்டும் முயலவும்.",
  "err.invalid": "நீங்கள் அளித்த விவரங்களைச் சரிபார்க்கவும்.",
  "err.required": "இந்த விவரம் அவசியம்.",
  "err.number": "சரியான எண்ணை உள்ளிடவும்.",
  "err.consent": "தொடர பெட்டியில் குறியிடவும்.",

  "about.title": "இது எப்படி செயல்படுகிறது",
  "about.p1":
    "உதவியாளர் உங்கள் விவரங்களை அதிகாரப்பூர்வ திட்ட வழிகாட்டுதல்கள் மற்றும் சுற்றறிக்கைகளுடன் ஒப்பிட்டுச் சரிபார்க்கிறது. இது ஊகிக்காது: ஒவ்வொரு முடிவும் அது அடிப்படையாகக் கொண்ட ஆவணங்களைப் பட்டியலிடும்.",
  "about.p2":
    "பிந்தைய சுற்றறிக்கைகள் பழைய வழிகாட்டுதல் உரையை மீறும். காட்டப்பட்ட தேதியில் நடைமுறையில் உள்ள விதிகளையே சரிபார்ப்பு பயன்படுத்துகிறது.",
  "about.privacy.title": "உங்கள் தனியுரிமை",
  "about.privacy.body":
    "உங்கள் விவரங்களை நாங்கள் சேமிப்பதில்லை. உங்கள் பதிலைத் தயாரிக்க மட்டுமே அவை உதவியாளருக்கு அனுப்பப்படுகின்றன; உங்கள் உலாவியிலும் சேமிக்கப்படுவதில்லை. உங்கள் பெயர், தொலைபேசி எண் அல்லது ஆதார் எண்ணை உள்ளிட வேண்டாம்: அவை தேவையில்லை.",
  "about.official.title": "அதிகாரப்பூர்வ நிலை",

  "footer.note": "ஆரம்பநிலை வழிகாட்டுதல் மட்டுமே. இது அதிகாரப்பூர்வ முடிவு அல்ல.",
};

const MESSAGES: Record<Lang, Messages> = { en, hi, kn, ta };

/** True if `key` is a real message id. Use for keys built from backend data (flags, field names). */
export const isMessageKey = (key: string): key is MessageKey => Object.hasOwn(en, key);

export function t(lang: Lang, key: MessageKey, vars?: Record<string, string>): string {
  let text = MESSAGES[lang]?.[key] ?? MESSAGES.en[key];
  if (vars) for (const [k, v] of Object.entries(vars)) text = text.replace(`{${k}}`, v);
  return text;
}

/** Official sentences from the knowledge base (mitra/i18n.py). Do not paraphrase. */
export const OFFICIAL: Record<"finalDecision" | "zeroFee" | "neverShareOtp", Record<Lang, string>> = {
  finalDecision: {
    en: "This is a preliminary check only. The concerned government department makes the final decision after verification.",
    hi: "आवेदन करने से मंजूरी पक्की नहीं होती। दस्तावेज़ जांच के बाद संबंधित विभाग ही अंतिम निर्णय लेता है।",
    kn: "ಪ್ರತಿ ಯೋಜನೆಯ ಅರ್ಜಿಯ ಮೇಲೆ ಸಂಬಂಧಪಟ್ಟ ಸರ್ಕಾರಿ ಇಲಾಖೆಯೇ ಅಂತಿಮ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.",
    ta: "அனைத்து விண்ணப்பங்களிலும் சம்பந்தப்பட்ட அரசுத் துறையே இறுதி முடிவை எடுக்கும்.",
  },
  zeroFee: {
    en: "There is no fee for any scheme application or benefit release (₹0). Do not pay any agent or middleman.",
    hi: "किसी भी योजना के आवेदन फॉर्म के लिए कोई सरकारी शुल्क (₹0) नहीं है। किसी दलाल, एजेंट या बिचौलिए को पैसा न दें।",
    kn: "ಯಾವುದೇ ಯೋಜನೆಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಅಥವಾ ಹಣ ಬಿಡುಗಡೆ ಮಾಡಲು ಶುಲ್ಕ (₹0) ಇಲ್ಲ. ಮಧ್ಯವರ್ತಿಗಳಿಗೆ ಅಥವಾ ಏಜೆಂಟ್‌ಗಳಿಗೆ ಹಣ ನೀಡಬೇಡಿ.",
    ta: "எந்த நலத்திட்ட விண்ணப்பத்திற்கும் அல்லது உதவித்தொகை விடுவிப்பதற்கும் கட்டணம் (₹0) கிடையாது. இடைத்தரகர்கள் அல்லது ஏஜென்டுகளுக்கு பணம் கொடுக்க வேண்டாம்.",
  },
  neverShareOtp: {
    en: "Never share your OTP, bank PIN or password with anyone. No government official will ask for them, and no genuine caller can get your application approved.",
    hi: "सरकारी अधिकारी कभी फोन पर OTP, बैंक PIN या पैसे नहीं मांगते। अपना OTP किसी के भी साथ साझा न करें।",
    kn: "ನಿಮ್ಮ OTP, ಬ್ಯಾಂಕ್ PIN ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
    ta: "உங்கள் OTP, வங்கி PIN அல்லது கடவுச்சொல்லை யாரிடமும் பகிர வேண்டாம்.",
  },
};
