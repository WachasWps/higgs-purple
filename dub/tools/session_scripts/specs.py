# Text-pass specs for the 10 Purple Sunscreen videos (TEXT_BRIEF.md).
# plan: {line_id: {field: value}}  (only the fields that change)
# caps: {line_id: {lang: caption}}  manual caption overrides (else auto-derived from the dubbed text)
# gfx:  full new graphics.json content (elements, caption_moves, caption_y, notes)

def P(x, y):
    return {"x": x, "y": y}


SPECS = {}

# ---------------------------------------------------------------- 00b304b4
SPECS["00b304b4"] = dict(
    plan={
        5: dict(en="I cancel yellow-looking dullness.",
                bn="হলদেটে ডালনেস আমি কাটাই!",
                ta="மஞ்சள் டல்னெஸ் கேன்சல் பண்றேன்!",
                te="పసుపు డల్‌నెస్‌ని కట్ చేస్తా!",
                ml="മഞ്ഞ ഡൾനെസ് ഞാൻ ക്യാൻസൽ ചെയ്യും!",
                **{"or": "ହଳଦିଆ ଡଲନେସ୍ ମୁଁ କାଟିଦିଏ!"}),
        6: dict(en="And I've got the instant glow.",
                bn="আর ইনস্ট্যান্ট গ্লো আমি দেব!",
                ta="இன்ஸ்டன்ட் க்ளோ நான் தரேன்!",
                te="ఇక ఇన్‌స్టంట్ గ్లో నేను ఇస్తా!",
                ml="പിന്നെ ഇൻസ്റ്റന്റ് ഗ്ലോ, അത് ഞാൻ തരും!",
                **{"or": "ଆଉ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ ମୁଁ ଦେବି!"}),
        8: dict(en="Instant glow. Ready for the day.",
                bn="ইনস্ট্যান্ট গ্লো, আজ রেডি!",
                ta="இன்ஸ்டன்ட் க்ளோ, இன்னைக்கு ரெடி!",
                te="ఇన్‌స్టంట్ గ్లో, ఈరోజుకి రెడీ!",
                ml="ഇൻസ്റ്റന്റ് ഗ്ലോ, ഇന്ന് ഫുൾ റെഡി!",
                **{"or": "ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ, ଆଜି ପାଇଁ ରେଡି!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[], elements=[
        dict(type="hook_mono", start=0.2, end=2.4, lines=["SKIN PROTECTION", "DEPARTMENT"], **P(0.6, 0.09), anim="type"),
        dict(type="label", start=2.75, end=4.45, lines=["UV VILLAIN"], **P(0.78, 0.22), anim="pop"),
        dict(type="pill", start=11.0, end=12.7, lines=["4% NIACINAMIDE", "INSTANT GLOW"], **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=12.8, end=14.7, lines=["MADE FOR", "INDIAN SKIN TONES"], sub="NO WHITE CAST",
             **P(0.5, 0.76), anim="fade"),
        dict(type="claim_bold", start=14.9, end=16.95, lines=["INSTANT GLOW"], **P(0.5, 0.12), anim="fade"),
    ], notes="Text pass (EDL): hook kept, lifted above the PSA1 tube; UV VILLAIN tag on the kept villain shot; no supers "
             "in the colour-wheel window 7.6-11.0 (graphic carries its own text; HUD + PURPLE TINT pill removed); "
             "4% NIACINAMIDE / INSTANT GLOW then MADE FOR INDIAN SKIN TONES / NO WHITE CAST below the chin on PS05; "
             "INSTANT GLOW above Meera's head on the PSA3 end shot. Caption lift for the old baked bottom text removed."),
)

# ---------------------------------------------------------------- 291827ba
SPECS["291827ba"] = dict(
    plan={
        4: dict(en="Evidence two: purple cancels yellow-looking dullness.",
                bn="প্রমাণ নম্বর দুই, পার্পল হলদেটে ডালনেস কাটায়!",
                ta="ஆதாரம் ரெண்டு, பர்ப்பிள் மஞ்சள் டல்னெஸ்ஸ கேன்சல் பண்ணும்!",
                te="సాక్ష్యం నంబర్ టూ, పర్పుల్‌తో పసుపు డల్‌నెస్ క్యాన్సిల్!",
                ml="തെളിവ് നമ്പർ ടൂ, പർപ്പിൾ മഞ്ഞ ഡൾനെസ് ക്യാൻസൽ ചെയ്യും!",
                **{"or": "ପ୍ରମାଣ ନମ୍ବର ଦୁଇ, ପର୍ପଲ୍ ହଳଦିଆ ଡଲନେସ୍ କାଟିଦିଏ!"}),
        5: {"or": "ଡଲ୍ ସ୍କିନ୍ ବ୍ରାଇଟ୍ କରିବାରେ ହେଲ୍ପ କରେ!"},   # pre-existing over-budget Odia line, shortened
        6: dict(en="The verdict: protected skin with an instant glow.",
                bn="রায় হলো, প্রোটেক্টেড স্কিন আর ইনস্ট্যান্ট গ্লো!",
                ta="தீர்ப்பு, ப்ரொடெக்டட் ஸ்கின், கூடவே இன்ஸ்டன்ட் க்ளோ!",
                te="తీర్పు, ప్రొటెక్టెడ్ స్కిన్, ఇంకా ఇన్‌స్టంట్ గ్లో!",
                ml="വിധി, പ്രൊട്ടക്റ്റഡ് സ്കിൻ, കൂടെ ഇൻസ്റ്റന്റ് ഗ്ലോ!",
                **{"or": "ରାୟ ହେଲା, ପ୍ରୋଟେକ୍ଟେଡ୍ ସ୍କିନ୍ ସହ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[{"start": 4.95, "end": 7.6, "y": 0.93}], elements=[
        dict(type="hook_mono", start=0.15, end=1.85, lines=["SKIN UNDER", "ATTACK?"], anim="slide_up", **P(0.6, 0.085)),
        dict(type="pill", start=10.5, end=12.4, lines=["4% NIACINAMIDE", "BRIGHTENS DULL-LOOKING SKIN"], **P(0.5, 0.76),
             anim="pop"),
        dict(type="claim_bold", start=12.9, end=15.4, lines=["THE VERDICT:", "INSTANT GLOW"],
             sub="MADE FOR INDIAN SKIN TONES", **P(0.5, 0.75), anim="fade"),
    ], notes="Text pass (EDL): hook over hair on the shared villain-hook clip; no supers in the colour-wheel window "
             "7.6-10.3 (old NO WHITE CAST pill removed); 4% NIACINAMIDE pill below the chin on PS05; verdict claim "
             "INSTANT GLOW + MADE FOR INDIAN SKIN TONES below the chin on PS06. Caption lift kept for the kept "
             "courtroom shot's baked SPF text."),
)

# ---------------------------------------------------------------- 33c29291
SPECS["33c29291"] = dict(
    plan={
        1: {"or": "ଏଇ ସନସ୍କ୍ରିନକୁ ସମସ୍ତେ ଦେଖିବେ, ପକ୍କା!"},     # pre-existing over-budget Odia line, shortened
        3: dict(en="Purple sits opposite yellow, so it cancels dullness.",
                bn="পার্পল হলুদের উল্টো, তাই ডালনেস ক্যানসেল করে।",
                ta="பர்பிள், மஞ்சளுக்கு நேர் எதிர், அதனால டல்னஸ்ஸ கேன்சல் பண்ணும்.",
                te="పర్పుల్ పసుపుకి ఆపోజిట్, అందుకే డల్‌నెస్ క్యాన్సిల్!",
                ml="പർപ്പിൾ മഞ്ഞയുടെ എതിരാണ്, അതുകൊണ്ട് ഡൾനെസ് ക്യാൻസൽ ചെയ്യും.",
                **{"or": "ପର୍ପଲ ହଳଦିଆର ଠିକ ବିପରୀତ, ତେଣୁ ଡଲନେସ କ୍ୟାନସଲ କରେ।"}),
        5: dict(bn="ফোর পার্সেন্ট নায়াসিনামাইড, ব্রাইটনেসে হেল্প!",   # pre-existing over-budget lines, shortened
                **{"or": "ଫୋର ପର୍ସେଣ୍ଟ ନିଆସିନାମାଇଡ, ବ୍ରାଇଟନେସରେ ହେଲ୍ପ!"}),
        7: dict(en="No white cast. Just protected skin and instant glow.",
                bn="হোয়াইট কাস্ট নেই। শুধু প্রোটেকশন আর ইনস্ট্যান্ট গ্লো!",
                ta="வைட் காஸ்ட் இல்ல. ஜஸ்ட் ப்ரொடெக்டட் ஸ்கின், கூடவே இன்ஸ்டன்ட் க்ளோ!",
                te="వైట్ కాస్ట్ లేదు. జస్ట్ ప్రొటెక్టెడ్ స్కిన్, ఇంకా ఇన్‌స్టంట్ గ్లో!",
                ml="വൈറ്റ് കാസ്റ്റ് ഇല്ല. ജസ്റ്റ് പ്രൊട്ടക്റ്റഡ് സ്കിൻ, കൂടെ ഇൻസ്റ്റന്റ് ഗ്ലോ!",
                **{"or": "ହ୍ୱାଇଟ କାଷ୍ଟ ନାହିଁ। ଖାଲି ପ୍ରୋଟେକ୍ସନ ଆଉ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[], elements=[
        dict(type="label", start=0.3, end=2.2, lines=["WHITE CAST"], **P(0.2, 0.46), anim="pop"),
        dict(type="pill", start=8.0, end=10.7, lines=["MADE FOR", "INDIAN SKIN TONES"], **P(0.5, 0.76), anim="pop"),
        dict(type="pill", start=10.9, end=12.8, lines=["4% NIACINAMIDE"], **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=14.0, end=15.8, lines=["SPF 50 PA+++"], sub="UVA + UVB PROTECTION",
             **P(0.5, 0.77), anim="fade"),
        dict(type="claim_bold", start=16.1, end=19.9, lines=["INSTANT GLOW"], sub="NO WHITE CAST", **P(0.5, 0.76),
             anim="fade"),
    ], notes="Text pass (EDL): WHITE CAST tag beside the white blob in the shared villain-hook clip; no supers in the "
             "colour-wheel window 4.6-7.63 (COLOUR CORRECTION claim removed); MADE FOR INDIAN SKIN TONES over the "
             "PS08 hand blend (wrist area, swatch clear); 4% NIACINAMIDE and SPF 50 PA+++ below the chin on PS05; "
             "INSTANT GLOW / NO WHITE CAST below the chin across the PS06 glow shot."),
)

# ---------------------------------------------------------------- 5fd50ab8
SPECS["5fd50ab8"] = dict(
    plan={
        2: dict(en="Relax. My purple sits opposite yellow, so it cancels dullness.",
                bn="রিল্যাক্স। আমার পার্পল হলুদের ঠিক উল্টো দিকে থাকে, তাই ডালনেস ক্যানসেল করে।",
                ta="ரிலாக்ஸ். என் பர்பிள் மஞ்சளுக்கு நேர் எதிர்ல இருக்கு, அதனால டல்னெஸ்ஸ கேன்சல் பண்ணும்!",
                te="రిలాక్స్. నా పర్పుల్ పసుపుకి సరిగ్గా ఆపోజిట్, అందుకే డల్‌నెస్‌ని క్యాన్సిల్ చేస్తుంది!",
                ml="റിലാക്സ്. എന്റെ പർപ്പിൾ മഞ്ഞയുടെ നേരെ എതിരാണ്, അതുകൊണ്ട് ഡൾനെസ് ക്യാൻസൽ ചെയ്യും!",
                **{"or": "ରିଲାକ୍ସ। ମୋ ପର୍ପଲ ହଳଦିଆର ଠିକ ବିପରୀତ, ତେଣୁ ଡଲନେସ କ୍ୟାନସଲ କରେ।"}),
        3: dict(en="Blend me in. Made for Indian skin, no cast.",
                bn="আমায় ব্লেন্ড করে নাও। ইন্ডিয়ান স্কিনের জন্য তৈরি, কাস্ট নেই!",
                ta="என்ன ப்ளெண்ட் பண்ணு. இந்தியன் ஸ்கின்னுக்காகவே செஞ்சது, காஸ்ட் கிடையாது!",
                te="నన్ను బ్లెండ్ చెయ్యి. ఇండియన్ స్కిన్ కోసమే తయారైంది, కాస్ట్ ఉండదు!",
                ml="എന്നെ ബ്ലെൻഡ് ചെയ്യ്. ഇന്ത്യൻ സ്കിന്നിനായി ഉണ്ടാക്കിയത്, കാസ്റ്റ് ഇല്ല!",
                **{"or": "ମୋତେ ବ୍ଲେଣ୍ଡ କର। ଇଣ୍ଡିଆନ ସ୍କିନ ପାଇଁ ତିଆରି, କାଷ୍ଟ ନାହିଁ!"}),
        4: dict(en="Protected. Instant glow. Ready.",
                bn="প্রোটেক্টেড। ইনস্ট্যান্ট গ্লো। একদম রেডি!",
                ta="ப்ரொடெக்ஷன் ஆச்சு. இன்ஸ்டன்ட் க்ளோ வந்தாச்சு. ரெடி!",
                te="ప్రొటెక్షన్ ఉంది. ఇన్‌స్టంట్ గ్లో వచ్చింది. రెడీ!",
                ml="പ്രൊട്ടക്ഷൻ ഓക്കെ. ഇൻസ്റ്റന്റ് ഗ്ലോ. റെഡി!",
                **{"or": "ପ୍ରୋଟେକ୍ସନ ହେଇଗଲା। ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ। ରେଡି!"}),
        5: dict(en="Instant glow, then go.",
                bn="আগে ইনস্ট্যান্ট গ্লো, তারপর গো!",
                ta="முதல்ல இன்ஸ்டன்ட் க்ளோ, அப்புறம் கோ!",
                te="ముందు ఇన్‌స్టంట్ గ్లో, తర్వాత గో!",
                ml="ആദ്യം ഇൻസ്റ്റന്റ് ഗ്ലോ, പിന്നെ ഗോ!",
                **{"or": "ଆଗେ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ, ତା ପରେ ଗୋ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[], elements=[
        dict(type="label", start=0.9, end=2.8, lines=["YELLOW-LOOKING", "DULLNESS"], **P(0.2, 0.42), anim="pop"),
        dict(type="claim_bold", start=9.4, end=12.8, lines=["NO WHITE CAST"], sub="MADE FOR INDIAN SKIN TONES",
             **P(0.5, 0.76), anim="fade"),
        dict(type="pill", start=13.05, end=15.35, lines=["SPF 50 PA+++", "4% NIACINAMIDE"], **P(0.5, 0.74), anim="pop"),
        dict(type="claim_bold", start=16.0, end=19.95, lines=["INSTANT GLOW"], sub="FOR INDIAN SKIN TONES",
             **P(0.5, 0.12), anim="fade"),
    ], notes="Text pass (EDL): YELLOW-LOOKING DULLNESS tag beside her dull cheek on PS07; no supers in the colour-wheel "
             "window 3.6-8.97 (HUD + PURPLE TINT removed); NO WHITE CAST / MADE FOR INDIAN SKIN TONES below the chin "
             "on PS05; SPF + niacinamide pill below the chin on PS06; INSTANT GLOW above Meera's head across the PSA3 "
             "end shot. Old caption drop for the sneaker end shot removed."),
)

# ---------------------------------------------------------------- 655a1328
SPECS["655a1328"] = dict(
    plan={
        1: dict(en="Let's make her skin look dull!",
                bn="চল, ওর স্কিনটা ডাল করে দিই!",
                ta="வா, இவ ஸ்கின்ன டல்லாக்கிடலாம்!",
                te="పదా, దీని స్కిన్‌ని డల్ చేసేద్దాం!",
                ml="വാ, ഇവളുടെ സ്കിൻ ഡൾ ആക്കാം!",
                **{"or": "ଚାଲ, ତା ସ୍କିନକୁ ଡଲ କରିଦେବା!"}),
        3: dict(en="Yellow-looking dullness? Purple sits opposite, cancels it.",
                bn="হলদেটে ডালনেস? পার্পল ঠিক তার উল্টো দিকে, ক্যানসেল করে দেয়!",
                ta="மஞ்சளா டல்லா தெரியுதா? பர்பிள் அதுக்கு நேர் எதிர், கேன்சல் பண்ணிடும்!",
                te="పసుపు డల్‌నెస్సా? పర్పుల్ దానికి ఆపోజిట్, క్యాన్సిల్ చేస్తుంది!",
                ml="മഞ്ഞച്ച ഡൾനെസ്സ് ആണോ? പർപ്പിൾ അതിന്റെ നേരെ എതിരാ, ക്യാൻസൽ ചെയ്യും!",
                **{"or": "ହଳଦିଆ ଡଲନେସ? ପର୍ପଲ ଠିକ୍ ତା ବିପରୀତ, କ୍ୟାନସଲ କରିଦିଏ!"}),
        7: dict(en="Same skin tone, with an instant glow.",
                bn="একই স্কিন টোন, সাথে ইনস্ট্যান্ট গ্লো!",
                ta="அதே ஸ்கின் டோன், கூடவே இன்ஸ்டன்ட் க்ளோ!",
                te="అదే స్కిన్ టోన్, ఇంకా ఇన్‌స్టంట్ గ్లో!",
                ml="അതേ സ്കിൻ ടോൺ, കൂടെ ഇൻസ്റ്റന്റ് ഗ്ലോ!",
                **{"or": "ସମାନ ସ୍କିନ ଟୋନ, ସାଥିରେ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[{"start": 10.93, "end": 14.0, "y": 0.58}], elements=[
        dict(type="label", start=0.3, end=2.2, lines=["DULLNESS", "VILLAIN"], **P(0.18, 0.64), anim="pop"),
        dict(type="claim_bold", start=8.1, end=10.8, lines=["MADE FOR", "INDIAN SKIN TONES"], sub="NO WHITE CAST",
             **P(0.5, 0.76), anim="fade"),
        dict(type="label", start=10.93, end=14.0, lines=["BEFORE"], **P(0.5, 0.455), anim="pop"),
        dict(type="label", start=10.93, end=14.0, lines=["INSTANT GLOW"], **P(0.5, 0.955), anim="pop"),
        dict(type="hud", variant="corners", start=11.0, end=13.95),
        dict(type="pill", start=11.1, end=13.2, lines=["4% NIACINAMIDE"], **P(0.6, 0.075), anim="pop"),
        dict(type="pill", start=14.1, end=16.4, lines=["SPF 50 PA+++", "UVA + UVB"], **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=16.8, end=19.95, lines=["INSTANT GLOW"], sub="NO WHITE CAST", **P(0.5, 0.12),
             anim="fade"),
    ], notes="Text pass (EDL): DULLNESS VILLAIN tag under the dullness cloud of the shared villain-hook clip; no supers "
             "in the colour-wheel window 4.0-7.43; MADE FOR INDIAN SKIN TONES / NO WHITE CAST below the chin on PS05; "
             "top/bottom B/A split 10.93-14.0 with BEFORE over the divider and INSTANT GLOW under the after face, "
             "captions moved to 0.58 under the divider, corner HUD, 4% NIACINAMIDE pill on the hair above the split; "
             "SPF pill below the chin on PS09; INSTANT GLOW / NO WHITE CAST above Meera's head on PSA3."),
)

# ---------------------------------------------------------------- 74495eba
SPECS["74495eba"] = dict(
    plan={
        4: dict(en="Purple sits opposite yellow, so it helps cancel dullness.",
                bn="পার্পল হলুদের ঠিক উল্টো, তাই ডালনেস ক্যানসেল করতে হেল্প করে।",
                ta="பர்பிள் மஞ்சளுக்கு நேர் எதிர், அதனால டல்னஸ்ஸ கேன்சல் பண்ண உதவும்!",
                te="పర్పుల్ పసుపుకి ఆపోజిట్, సో డల్‌నెస్ క్యాన్సిల్‌కి హెల్ప్ చేస్తుంది!",
                ml="പർപ്പിൾ മഞ്ഞയുടെ എതിരാണ്, അതുകൊണ്ട് ഡൾനെസ് ക്യാൻസൽ ചെയ്യാൻ സഹായിക്കും.",
                **{"or": "ପର୍ପଲ ହଳଦିଆର ଠିକ ବିପରୀତ, ତେଣୁ ଡଲନେସ କ୍ୟାନସଲ କରିବାରେ ହେଲ୍ପ କରେ।"}),
        6: dict(en="Instant glow, protected and ready.",
                bn="ইনস্ট্যান্ট গ্লো, প্রোটেক্টেড আর রেডি!",
                ta="இன்ஸ்டன்ட் க்ளோ, ப்ரொடெக்டட், ரெடி!",
                te="ఇన్‌స్టంట్ గ్లో, ప్రొటెక్టెడ్ అండ్ రెడీ!",
                ml="ഇൻസ്റ്റന്റ് ഗ്ലോ, പ്രൊട്ടക്റ്റഡ് ആൻഡ് റെഡി!",
                **{"or": "ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ, ପ୍ରୋଟେକ୍ଟେଡ ଆଉ ରେଡି!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[{"start": 15.9, "end": 20.04, "y": 0.58}], elements=[
        dict(type="label", start=1.0, end=2.75, lines=["UV BOSS"], **P(0.17, 0.13), anim="pop"),
        dict(type="claim_bold", start=5.0, end=7.55, lines=["SPF 50 PA+++"], sub="UVA + UVB PROTECTION",
             **P(0.5, 0.1), anim="fade"),
        dict(type="claim_bold", start=12.9, end=15.85, lines=["MADE FOR", "INDIAN SKIN TONES"], sub="4% NIACINAMIDE",
             **P(0.5, 0.76), anim="fade"),
        dict(type="label", start=15.96, end=19.95, lines=["BEFORE"], **P(0.5, 0.455), anim="pop"),
        dict(type="label", start=15.96, end=19.95, lines=["INSTANT GLOW"], **P(0.5, 0.955), anim="pop"),
        dict(type="hud", variant="scan", start=15.96, end=19.95),
        dict(type="pill", start=16.2, end=19.95, lines=["NO WHITE CAST", "SPF 50 PA+++"], **P(0.6, 0.075), anim="pop"),
    ], notes="Text pass (EDL, shot 2 = PSA1 4.57-7.6, wheel 7.6-12.2): UV BOSS tag above the sun villain of the shared "
             "villain-hook clip; SPF 50 PA+++ / UVA + UVB PROTECTION above the PSA1 tube, ending before the wheel; no "
             "supers in the colour-wheel window 7.6-12.2; MADE FOR INDIAN SKIN TONES / 4% NIACINAMIDE below the chin "
             "on PS05; top/bottom B/A split 15.9-20.04 with BEFORE / INSTANT GLOW labels, captions at 0.58 under the "
             "divider, scan HUD, NO WHITE CAST / SPF pill on the hair above the split (the EDL's top claim, shortened "
             "to fit; Indian skin tones was just shown)."),
)

# ---------------------------------------------------------------- 7ea55172
SPECS["7ea55172"] = dict(
    plan={
        4: dict(en="Purple sits opposite yellow, so it cancels dullness.",
                bn="পার্পল হলুদের উল্টো, তাই ডালনেস ক্যানসেল করে।",
                ta="பர்பிள் மஞ்சளுக்கு நேர் எதிர், அதனால டல்னஸ்ஸ கேன்சல் பண்ணும்.",
                te="పర్పుల్ పసుపుకి ఆపోజిట్, అందుకే డల్‌నెస్ క్యాన్సిల్!",
                ml="പർപ്പിൾ മഞ്ഞയുടെ എതിരാണ്, അതുകൊണ്ട് ഡൾനെസ് ക്യാൻസൽ ചെയ്യും.",
                **{"or": "ପର୍ପଲ ହଳଦିଆର ଠିକ ବିପରୀତ, ତେଣୁ ଡଲନେସ କ୍ୟାନସଲ କରେ।"}),
        6: dict(bn="ফোর পারসেন্ট নায়াসিনামাইড, ব্রাইটে হেল্প!"),  # bn promised bare 'glow'; now matches 'helps brighten'
        8: dict(en="Instant glow, protected, and no morning drama.",
                bn="ইনস্ট্যান্ট গ্লো, প্রোটেক্টেড, আর সকালে নো ড্রামা!",
                ta="இன்ஸ்டன்ட் க்ளோ, ப்ரொடெக்டட், காலையில நோ ட்ராமா!",
                te="ఇన్‌స్టంట్ గ్లో, ప్రొటెక్టెడ్, మార్నింగ్ నో డ్రామా!",
                ml="ഇൻസ്റ്റന്റ് ഗ്ലോ, പ്രൊട്ടക്റ്റഡ്, രാവിലെ നോ ഡ്രാമ!",
                **{"or": "ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ, ପ୍ରୋଟେକ୍ଟେଡ, ସକାଳେ ନୋ ଡ୍ରାମା!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[{"start": 11.27, "end": 14.0, "y": 0.58}], elements=[
        dict(type="label", start=0.15, end=1.85, lines=["GREASINESS"], **P(0.18, 0.46), anim="pop"),
        dict(type="label", start=2.1, end=3.7, lines=["DULLNESS"], **P(0.2, 0.64), anim="pop"),
        dict(type="claim_bold", start=8.4, end=11.1, lines=["MADE FOR", "INDIAN SKIN TONES"], sub="NO WHITE CAST",
             **P(0.5, 0.76), anim="fade"),
        dict(type="label", start=11.27, end=14.0, lines=["BEFORE"], **P(0.5, 0.455), anim="pop"),
        dict(type="label", start=11.27, end=14.0, lines=["INSTANT GLOW"], **P(0.5, 0.955), anim="pop"),
        dict(type="hud", variant="scan", start=11.3, end=13.95),
        dict(type="pill", start=11.3, end=12.95, lines=["4% NIACINAMIDE"], **P(0.6, 0.075), anim="pop"),
        dict(type="pill", start=14.0, end=16.15, lines=["SPF 50 PA+++", "UVA + UVB"], **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=16.6, end=19.95, lines=["INSTANT GLOW"], sub="FOR INDIAN SKIN TONES",
             **P(0.5, 0.12), anim="fade"),
    ], notes="Text pass (EDL): GREASINESS / DULLNESS tags in the villain column of the shared villain-hook clip; no "
             "supers in the colour-wheel window 5.27-8.27 (COLOUR CORRECTION pill removed); MADE FOR INDIAN SKIN "
             "TONES / NO WHITE CAST below the chin on PS05; top/bottom B/A split 11.27-14.0 with BEFORE / INSTANT "
             "GLOW labels, captions at 0.58 under the divider, scan HUD, 4% NIACINAMIDE pill on the hair above the "
             "split; SPF pill below the chin on PS09; INSTANT GLOW / FOR INDIAN SKIN TONES above Meera's head on PSA3."),
)

# ---------------------------------------------------------------- c51221b6
SPECS["c51221b6"] = dict(
    plan={
        4: dict(en="I'm opposite yellow, so I cancel dullness.", tag="happy",
                bn="আমি হলুদের ঠিক উল্টো, তাই ডালনেস ক্যানসেল করি!",
                ta="நான் மஞ்சளுக்கு நேர் எதிர், அதனால டல்னஸ்ஸ கேன்சல் பண்றேன்!",
                te="నేను పసుపుకి ఆపోజిట్, అందుకే డల్‌నెస్‌ని క్యాన్సిల్ చేస్తా!",
                ml="ഞാൻ മഞ്ഞയുടെ എതിരാണ്, അതുകൊണ്ട് ഡൾനെസ് ക്യാൻസൽ ചെയ്യും!",
                **{"or": "ମୁଁ ହଳଦିଆର ଠିକ ବିପରୀତ, ତେଣୁ ଡଲନେସ କ୍ୟାନସଲ କରେ!"}),
        7: dict(en="See the instant glow, not the sunscreen.",
                bn="ইনস্ট্যান্ট গ্লো দেখো, সানস্ক্রিন নয়!",
                ta="இன்ஸ்டன்ட் க்ளோவ பாருங்க, சன்ஸ்க்ரீன இல்ல!",
                te="ఇన్‌స్టంట్ గ్లో చూడు, సన్‌స్క్రీన్ కాదు!",
                ml="ഇൻസ്റ്റന്റ് ഗ്ലോ കാണൂ, സൺസ്ക്രീനല്ല!",
                **{"or": "ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ ଦେଖ, ସନସ୍କ୍ରିନ ନୁହେଁ!"}),
    },
    caps={7: {"ta": "Instant Glow-வ பாருங்க, Sunscreen-ன இல்ல!", "ml": "Instant Glow കാണൂ, Sunscreen-നല്ല!"}},
    gfx=dict(caption_y=0.9, caption_moves=[], elements=[
        dict(type="hook_mono", start=0.2, end=2.6, lines=["TIRED OF", "WHITE CAST?"], **P(0.6, 0.085), anim="slide_up"),
        dict(type="claim_bold", start=8.6, end=10.8, lines=["SPF 50 PA+++"], sub="UVA + UVB PROTECTION",
             **P(0.5, 0.12), anim="fade"),
        dict(type="pill", start=11.15, end=12.8, lines=["4% NIACINAMIDE", "BRIGHTENS DULL-LOOKING SKIN"],
             **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=13.3, end=15.35, lines=["INSTANT GLOW", "NO WHITE CAST"],
             sub="MADE FOR INDIAN SKIN TONES", **P(0.5, 0.76), anim="fade"),
    ], notes="Text pass (EDL): hook kept, over the hair of the shared villain-hook clip; no supers in the colour-wheel "
             "window 5.13-8.3 (PURPLE TINT pill removed; the EDL's MADE FOR INDIAN SKIN TONES card there moved into "
             "the after claim's sub); SPF claim over the hair on PS04; 5 blur boxes and the hand-shot HUD removed; "
             "4% NIACINAMIDE pill below the chin on PS05; INSTANT GLOW / NO WHITE CAST + MADE FOR INDIAN SKIN TONES "
             "below the chin on PS06."),
)

# ---------------------------------------------------------------- ce849d3f
SPECS["ce849d3f"] = dict(
    plan={
        3: dict(en="I'm opposite yellow, so I cancel dullness.",
                bn="আমি হলুদের উল্টো, তাই ডালনেস ক্যানসেল করি!",
                ta="மஞ்சளுக்கு நான் எதிர், அதான் டல்னஸ் கேன்சல் ஆகுது!",
                te="నేను పసుపుకి ఆపోజిట్, సో డల్‌నెస్ క్యాన్సిల్!",
                ml="ഞാൻ മഞ്ഞയുടെ എതിര്, അതോണ്ട് ഡൾനെസ് ക്യാൻസൽ ആകും!",
                **{"or": "ମୁଁ ହଳଦିଆର ବିପରୀତ, ତେଣୁ ଡଲନେସ୍ କାଟିଦିଏ!"}),
        7: dict(en="And I help bring an instant glow.",
                bn="আর আমি ইনস্ট্যান্ট গ্লো আনতে হেল্প করি!",
                ta="நான் இன்ஸ்டன்ட் க்ளோ கொண்டுவர உதவுறேன்!",
                te="ఇన్‌స్టంట్ గ్లో తేవడంలో నేను హెల్ప్ చేస్తా!",
                ml="ഇൻസ്റ്റന്റ് ഗ്ലോ കിട്ടാൻ ഞാൻ സഹായിക്കും!",
                **{"or": "ମୁଁ ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ ଆଣିବାରେ ହେଲ୍ପ କରେ!"}),
        8: dict(en="Protected, comfortable, made for Indian skin.",
                bn="প্রোটেকশন, আরাম, ইন্ডিয়ান স্কিনের জন্যই!",
                ta="ப்ரொடெக்டட், கம்ஃபி, இந்தியன் ஸ்கின்னுக்கு!",
                te="ప్రొటెక్టెడ్, కంఫర్టబుల్, ఇండియన్ స్కిన్ కోసం!",
                ml="പ്രൊട്ടക്റ്റഡ്, കംഫർട്ടബിൾ, ഇന്ത്യൻ സ്കിന്നിന്!",
                **{"or": "ପ୍ରୋଟେକ୍ସନ୍, ଆରାମ, ଇଣ୍ଡିଆନ ସ୍କିନ ପାଇଁ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[], elements=[
        dict(type="hook_mono", start=0.15, end=2.3, lines=["GREASY, STICKY", "SUNSCREEN?"], **P(0.6, 0.085),
             anim="slide_up"),
        dict(type="claim_bold", start=7.0, end=9.5, lines=["LIGHTWEIGHT"], sub="BLENDS IN, NOT STICKY", **P(0.5, 0.76),
             anim="fade"),
        dict(type="pill", start=9.7, end=11.7, lines=["SPF 50 PA+++", "UVA + UVB"], **P(0.5, 0.76), anim="pop"),
        dict(type="pill", start=11.9, end=13.85, lines=["4% NIACINAMIDE", "INSTANT GLOW"], **P(0.5, 0.74), anim="pop"),
        dict(type="claim_bold", start=15.1, end=16.9, lines=["INSTANT GLOW", "NO WHITE CAST"],
             sub="FOR INDIAN SKIN TONES", position="top", anim="fade"),
    ], notes="Text pass (EDL): hook over the hair of the shared villain-hook clip; no supers in the colour-wheel window "
             "4.6-6.93 (HUD removed); texture claim LIGHTWEIGHT / BLENDS IN, NOT STICKY moved onto the PS05 blend; "
             "SPF pill on PS09 and 4% NIACINAMIDE / INSTANT GLOW on PS06, below the chin; end claim INSTANT GLOW / "
             "NO WHITE CAST / FOR INDIAN SKIN TONES in the sky above the kept tube end shot."),
)

# ---------------------------------------------------------------- e7e42eaf
SPECS["e7e42eaf"] = dict(
    plan={
        4: dict(en="I'm opposite yellow, so I cancel dullness.",
                bn="আমি হলুদের উল্টো, তাই ডালনেস ক্যানসেল করি!",
                ta="மஞ்சளுக்கு நான் எதிர், அதான் டல்னஸ் கேன்சல் ஆகுது!",
                te="నేను పసుపుకి ఆపోజిట్, సో డల్‌నెస్ క్యాన్సిల్!",
                ml="ഞാൻ മഞ്ഞയുടെ എതിര്, അതോണ്ട് ഡൾനെസ് ക്യാൻസൽ ആകും!",
                **{"or": "ମୁଁ ହଳଦିଆର ବିପରୀତ, ତେଣୁ ଡଲନେସ କାଟିଦିଏ!"}),
        5: dict(en="Made for Indian skin. Hello, instant glow!",
                bn="ইন্ডিয়ান স্কিনের জন্য! হ্যালো, ইনস্ট্যান্ট গ্লো!",
                ta="இந்தியன் ஸ்கின்னுக்காகவே! ஹலோ, இன்ஸ்டன்ட் க்ளோ!",
                te="ఇండియన్ స్కిన్ కోసమే తయారైంది! హలో, ఇన్‌స్టంట్ గ్లో!",
                ml="ഇന്ത്യൻ സ്കിന്നിനായി തന്നെ! ഹലോ, ഇൻസ്റ്റന്റ് ഗ്ലോ!",
                **{"or": "ଇଣ୍ଡିଆନ ସ୍କିନ ପାଇଁ ତିଆରି! ହେଲୋ, ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ!"}),
    },
    gfx=dict(caption_y=0.9, caption_moves=[{"start": 14.8, "end": 17.02, "y": 0.93}], elements=[
        dict(type="hud", variant="corners", start=0.0, end=2.9),
        dict(type="hook_mono", start=0.2, end=2.9, lines=["STEPPING OUT", "UNPROTECTED?"], **P(0.6, 0.085),
             anim="slide_up"),
        dict(type="claim_bold", start=5.5, end=8.2, lines=["SPF 50 PA+++"], sub="UVA + UVB PROTECTION",
             **P(0.5, 0.12), anim="fade"),
        dict(type="pill", start=11.3, end=12.6, lines=["4% NIACINAMIDE", "INSTANT GLOW"], **P(0.5, 0.76), anim="pop"),
        dict(type="claim_bold", start=12.6, end=13.95, lines=["MADE FOR", "INDIAN SKIN TONES"], sub="NO WHITE CAST",
             **P(0.5, 0.76), anim="fade"),
    ], notes="Text pass (EDL): hook kept, moved onto the hair of the shared villain-hook clip (was on her neck); SPF "
             "claim over the hair on PS04 (replaces the lost baked SPF text); no supers in the colour-wheel window "
             "8.27-11.13; 4% NIACINAMIDE / INSTANT GLOW then MADE FOR INDIAN SKIN TONES / NO WHITE CAST below the "
             "chin on PS05. caption_y back to 0.90 (the baked bottom titles it cleared are gone); end-card lift kept."),
)
