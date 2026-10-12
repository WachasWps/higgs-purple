# DERMDOC x Purplle: full project history (detailed appendix to HANDOVER.md)

Sources: the Claude Code working session (Oct 5 to Oct 12, 2026), the client WhatsApp chat (`dub/feedback/wa_raw/_chat.txt`), the Oct 11 review (`dub/feedback/CLIENT_REVIEW_OCT11.md`), `dub/feedback/issues_screens.json` and the briefs.
Times: logs are in UTC. The user works in IST (UTC+5:30), so "Oct 9 03:00Z" is about 8:30 AM IST on Oct 9.
Root: the `dub/` folder of this repo (all paths below are relative to it). Python: always `.venv/bin/python` (system python3 has no librosa, uharfbuzz or soundfile).

People:
- **wachas** ("Wachas Wp"): the user, who drives Claude.
- **Bhxdxx**: partner; does Higgsfield generations and wrote the Oct 7 status note.
- **Dhruv**: the account contact, who relays the client's (a woman at DERMDOC/Purplle) feedback in the WhatsApp group "Crazy Kaam".
- **Priyansh** ("my guy"): wrote the independent Oct 11 QC review.


---

## 1. Timeline of user instructions (deduplicated, near-verbatim, by phase)

### Phase 0: context before Claude was involved (WhatsApp, Oct 1 to Oct 8)
- **Oct 1:** client budget about 100k (Dhruv quoted 120k). Bhxdxx shared raw AI generations in 3 concepts: Product personification, Ingredients personification, UGC.
- **Oct 1, first client notes:**
  - nozzle wrong;
  - "pehle se hi glow hai" (skin already glowing before);
  - no English;
  - better BG and outdoor use-case;
  - before/after too exaggerated;
  - no hand application, face only;
  - tube shape changed;
  - weird shots;
  - font must be Lato or Roboto Mono;
  - no duration text top-left;
  - fake pigmentation;
  - ingredient pronunciation off.
- **Oct 1, languages:** "i want in languages. KL is Malayalam, TN Tamil, APTS Telugu, OD Odia, WB West Bengal. PS is purple sunscreen, KNC is kojic night cream". No Hindi and no English (later reversed for General Ads; see Oct 9).
- **Oct 6:** "Ingredients personified… more educational and less storytelling" (ref instagram.com/reels/DYE6011taRh). Deadline: everything by the 10th.
- **Oct 7:** Bhxdxx's status note.
  - Four categories: Ingredient Personified, Product Avatar, UGC, Normal AI Ads.
  - Everything to be dubbed into all languages.
  - Lip-sync probably won't match.
- **Oct 7, 7:17 PM: big client feedback (round 0), via Dhruv.**
  - Logo throughout plus an end slate in every category.
  - **Ingredient Personified:**
    - no skin-as-mountain; start on a face close-up;
    - product talks and the ingredients jump out of it;
    - KNC tub wrong; KNC texture not shown; KNC transformation must be shown (one good approved clip may be reused);
    - texture too watery.
  - **Product Avatar:**
    - product talks throughout; tub wrong in frames;
    - realistic spots;
    - full absorption, then a bit of glow;
    - check the DERMDOC pronunciation;
    - KNC transformation in all;
    - no spots after waking;
    - no hair on skin close-ups;
    - start and end on the face.
  - **PS:**
    - don't play on white cast; explain the purple tint as the USP (colour wheel, made for Indian skin tone, instant glow, no white cast);
    - max 15 s;
    - accurate tube with eyes and hands;
    - remove dandruff;
    - skin coming out of the face looks weird;
    - accurate texture;
    - super-smooth glowy face at the end;
    - properly blended, then instant glow.
  - **UGC KNC:**
    - no glow in the before; write "After 2 weeks";
    - before/after as a half-and-half vertical split, face not cropped;
    - duskier models; highlight concerns and benefits;
    - full absorption; exact packaging;
    - no KNC in the morning.
  - **UGC PS:** blended, then instant glow; accurate tube nozzle; long pauses ("Are we adding BG music?").

### Phase 1: dubbing 29 videos into 5 languages (Oct 5 to Oct 9 early)
- **Oct 5:** "connect higgsfield i have to download asset from there, use mcp" / "connected".
- **Oct 8 22:38Z:** "get the last generation from asset and help me dub it in bengali, tamil, telugu, malyalam, odia".
  - "check if there any open source model or some free way… it should be expressive natural".
  - "analyse my video then understand what kind of voice it need then decide which voice model, give me one video dubbed for now in bengali, if i like it then other languages".
- "where is the final dubbed video give me to review".
- **Oct 8 23:27Z:** "use multiple agents if needed, do parallel work, make it fast… i have 100+ more video to dub".
- **Oct 8 23:39Z:** "check higgsfield get all generation from 8 oct to today, you have to dub all video in all 5 languages".
  - "few video are brainrot video in which product is meme, so i need meme cartoon like voice, also there is villain character, i want proper character voice".
  - "do it parallel, use multiple agents, do whatever it takes to make this fast, but perfect".
  - Result: 29 videos, 145 dubs.
- **Oct 8 23:49Z:** "bro you overcooked my macbook, check the limits bro, dont cross my macbook limits, be smart understand my device capacity". The Mac had rebooted or swapped heavily.
- "tell me calculated time it will take for all video to get dubbed".
- "use as my agent subagent of claude you need to make this fast, no limit on that".
- "what if i get vm for this… give me vm hardware specs". The user pasted the GCP V100 specs: "is it good, does it will make process fast?"
- "why you stopped bro, you keep cooking… for now keep cooking in mac only".
- "okay good you make vm version, but are you generating audio and making video with that in parallel?"
- "can you use google colab code resource rather than vm" / "no no dont skip until i tell you" / "keep giving me status on each video final".
- "check is there any free vm provider which can provide ssh… this colab is too messy" / "also i will not be putting my credit or debit card to activate free credits".
- "give status out of total video ig its 145".
- Lightning AI: "will this 5 credits work here" / "bro this also asking for card, wtf" / "i think only cpu is free".
- "kaggle api key". The user provided a Kaggle token (stored at `~/.kaggle/access_token`, never echoed).
- "i want both my mac engine and kaggle work parallel".

### Phase 2: post-production graphics, captions, logo, outro (Oct 9 01:35Z to 02:55Z)
- **Oct 9 01:35Z, the main post-production spec:**
  1. "check Sunscream-5 T.mp4 in download, this is one of my final videos delivered to client… on screen text like chemical name… and also proper caption, i need this in all 145 video… only required places… style text according to video… looking perfect like ad".
  2. "put caption (subtitle) as in my final video, small and proper highlighting word by word, 2 words at a time or 1 word".
  3. "add dermdoc logo on top left" (`Dermdoc Logo in White (1) (1).png` / `Dermdoc Logo (2) (1).png` in Downloads).
  4. "outro video to add in each video according to product - last 2 whatsapp videos in downloads".
  - Do it in parallel within Mac limits.
- **Typo-cover rules:**
  - "a few videos already have text on the video… typos… suggest and decide".
  - "not on product jar… we can do only on the onscreen text fixing".
  - "skipping all the text on the products, or reflection of it… it stays the same".
- **Oct 9 01:55Z:** "i just did generic ai ads currently on higgsfield check the last 10 generated videos 5 is of KNC and 5 is of PS, i want captions on screen text captions logos endslate on them as well… only the last 10". These are the General Ads (Hinglish at that point).
- "3xpert is correct btw dont fix 3xpert typo because its 3xpert night cream".
- "nah mate this is looking yucks, pls dont make things look bad". This was about white cover boxes, which were then replaced with feathered blur.
- **Captions in each video's language:** "are they in their respective languages? … keeping enough space between words… all the english ingredients should be in english, but the script should have captions in their respective languages".
- "now stop checking all the images… stop reading images bro stop apple vision… stop image analysis". The user was near the usage limit.
- "leaving ocr thing, do rest of the things, i need a final video, already i have 99% limit reached" / "okay start rendering".

### Phase 3: music and SFX, folder structure, 5th KNC UGC (Oct 9 02:59Z to 03:25Z)
- "the task was there you're said to put sfx and subtle background music". Earlier wording: "very subtle… ncs no copyright as it is a commercial ad".
- "the sfx are not that effective, try to put some more sfx but perfect one, also the music is too low cant hear any".
- **Oct 9 03:10Z:** "make 4 folders: ingredient personified, product avatar, ugc ads, ai general ads; Purple sunscreen and KNC as sub folders in each of these 4 and then language folders… general ads are the hinglish ads… first give me the folder structure i will approve".
- "this knc ugc 2 is the 5th ugc we need to add in ugc knc now… convert the script into multiple languages and add the overlay text… sfx and bgm" / "also we would need to caption it" / "dont add logo and outro to this then". This became `a5c00002`.
- "can we have a better bg music??? this is humming sound and irritating".
- **Oct 9 ~03:35Z (9:04 AM IST):** the first full delivery of 160 files was uploaded to Drive folder `19w34s79NseHTH5C6Nq-9jpYUtA0bPfR0`.

### Phase 4: client feedback round 1, Dhruv's WhatsApp of Oct 9 (Oct 9 10:33Z to Oct 10)
- **Oct 9 10:33Z:** shared 4 screenshots: "these were feedback, what can be done".
- Codex setup:
  - "download codex cli… i want to change login";
  - tried to reach ChatGPT/Codex chat 6ac760a1-…;
  - "check locally it must've stored the session somewhere".
- **Oct 9 11:55Z: the main fix instruction (near-verbatim).**
  - "WhatsApp Chat - Crazy Kaam.zip in downloads folder, check the whole chat with screenshots, check where what need to be corrected".
  - "…take frames from those videos, go to gpt and get it new frames as codex cli has image gen capabilities… give him correct prompts and get perfect images".
  - "…then generate videos from higgsfield, dont generate long videos but generate like 5s videos using wan 3.0 480p so you wont require a lot of credits".
  - "…we only have 300-400 credits so you cannot use bigger models or bigger quality… give reference images and exact describe prompts".
  - "we need everything fixed and the client happy".
- **Product references:**
  - "i have just downloaded product images in the downloads folder… use it";
  - "give it to codex whenever generating images, give it to higgsfield whenever generating videos";
  - "remember the nozzle and texture and everything should be correct always";
  - "one more knc image downloaded… so that you have the open cream as well".
- "keep giving current status after any change or final output correction" / "paralalley try it bro".
- **Higgsfield connection:**
  - "give me a link to connect higgsfield" → `https://mcp.higgsfield.ai/mcp` → "not happening";
  - the user pasted the CLI setup: `npm i -g @higgsfield/cli`, `higgsfield auth login`, `npx skills add higgsfield-ai/skills`;
  - "bro for images pls use codex cli as i told ya".
- **Scope and progress checks:**
  - "i thought you only had to generate those specific clips that client had the issues with not the full videos?"
  - "but as i just saw you generated 5 clips of the same girl??"
  - "what about the colour wheel clips?"
  - "how many images and frames the client asked us to fix on whatsapp were you able to see the frames?"
  - "what all edits were there per category… what we are doing for each?"
  - "so how many clips needed?"
  - "Exact PS tube (nozzle, cap, two products) show me this".
- **Oct 9 13:28Z, course correction (important):**
  - "the old one they flagged is like a villain script and all and the new one doesn't match it?? you've changed the story line????"
  - "for most of them you have messed up the story line?? before generating more videos consult with me na"
  - "like tell me your plan first na"
  - This created the memory `consult-before-generating`.
- **AskUserQuestion answers:**
  - UGC: "Back to original creators".
  - General Ads: "Show me one first".
  - IP/Avatar: "how did codex limit get full?"
- "[3 images] can you see how the prompting has happened in these videos, how the reference images were given… this is how you could fix the videos". The original Higgsfield recipe: frame-sheet plus product refs plus shot-by-shot prompt.
- **Colour wheel:** "look at their colour wheel and look at our colourwheel… check colorwheel in this video, i want such color wheel". The reference is `~/Downloads/Sunscream-1 T.mp4` (first said Sunscream-5 T, then corrected).
- "so how many videos are remaining" / "show ugc videos" / "okay ugc is good, do others".
- Codex limit hit ("locked until 10:13 PM"): "what model you are using for codex?" → "effort set to low buddy".
- "what ads category is this" → **"okay we have to keep general in english no other language"** (memory: general-ads-english-only).
- "go" (UGC credit shots plus the 33c29291 pilot) / "yes it works" (pilot approved).
- **User-supplied product shots:**
  - "can you see my recent downloads it has product shots… does it solve our needs?" → "yes" (priorities 1+2);
  - "more downloads just done";
  - Drive folder `1_2MGBA6Et4q7ZfEuY5Byh_gpfepJBU_S` (SS-1…SS-8) "might even use these";
  - "all of these can also be used in general ads… multiple shots".
- "HOW MUCH TIME TO FINISH EVERYTHING?" / "WHICH 2 PAUSES" / "OK OPEN THEM" / "this video is okay, nice, proceed with other videos" / "use higgsfield credit accordingly to complete all videos".
- **English voice:**
  - "the voice is not good, its bad" (the Indic-Mio English for General Ads);
  - "use the free model, but remember i need indian english and also expressive and natural";
  - "4 is better, just check if you can enhance the quality of voice" (Kokoro option 4).
- "everything is done now???" / "pls check everything again".
- **Oct 9 20:58Z:** "put this all correct videos in same drive link replacing the existing one". Chrome upload was capped at 10 MB, so: "let it i will do it". The user uploads to Drive manually; the old folders go to Drive trash.

### Phase 5: client review Oct 11 (Priyansh's QC), wheel scripts, before/afters (Oct 11 09:09Z to 19:30Z)
- **Oct 11 09:09Z:** pasted the long review (saved as `feedback/CLIENT_REVIEW_OCT11.md`): "this is what my guy got me is he right or wrong tellme!!" Claude's answer: mostly right.
- "will it be possible for you to give me each clip in canva with editable elements or is that too much work?? say only one language". Claude offered a per-clip kit or CapCut/Premiere files; not done at the time.
- "can you use google flow to generate videos?" Answer: browser only, or Veo via the Gemini API. Not used.
- **Oct 11 09:45Z:**
  - "A. you have wheel in every video but we are not explaining the wheel in the scripts right??"
  - "B. the before after images… why do they look so weird?? … use chat gpt image gen with the lowest model so we dont exhaust it".
- "wait you dont need to make image of codex to change the wheel. the wheel is ok". Claude had wrongly edited the wheel graphic and reverted it.
- **Frame-by-frame rescript:**
  - "the script and VO doesnt explain the wheel in most places even in ingredient personified, avatar personified";
  - "you need to actually rescript each of them accordingly… for each frame";
  - "first look at each frame what is happening and then rewrite the script".
- "?so" / "continue" / "done?? is everything ready?" / "lets do it bro??" / "alright do it" (approved 52 line changes across 35 videos).
- "are the before after fixed in all the frames" / "where are they waiting?" / "generate images for codex bro".
- "how many videos are getting re voiced? and how much time" / "why not do parallelly".

### Phase 6: General Ads redo with the user's own footage (Oct 11 19:30Z to 21:30Z)
- "also can you package canva kit for me for the general ads".
- "just give me the videos and their cut how much you have cuts, dont give me text… i will just give the videos to you" / "ok cool i just want video cuts so pls give me fast" / "can you show me your versions as well of each". Result: `post/export_cuts.py` → General_Ads_Cuts.
- **Oct 11 20:42Z:** "look at the KNC general ads i just downloaded, you need to now look at each frame and write the scripts for it and write the onscreen text for it… look how good i did it they are better than yours fs". Output: `feedback/user_knc_ads/KNC_SCRIPTS.md`.
- **Oct 11 21:23Z:** "NOW THE SUNSCREEN GENERAL" (`feedback/user_ps_ads`).
- "HAVE YOU NOT PUT MY GENERAL ADS IN THE FINAL DELIVERABLES FOLDER YET".
- **General Ads audio and timing:**
  - "THE VIDEO HAS SOME OLD SOUND KEEP ONLY OUR VO SFX AND BG MUSIC, NOT THE VOICE FROM THE VIDEO";
  - "PLS USE INDIAN ENGLISH ACCENT AND HAVE A BETTER SCRIPT";
  - "CHECK IF THE WORDS ARE SPOKEN ON THE CORRECT FRAME FOR GENERAL ADS THAT IS IMP".
- Voice choice "C: hf_alpha, Indian" (Kokoro hf_alpha, lang "h").
- **"IT SHOULD SAY SHOP AT PURPLE.COM AT THE END ALWAYS OK?? NOT AVAILABLE AT PURPLE".**
- "WHICH OF THE 10TH GENERAL AD IS MISSING WHY YOU HAVE 9". GENERAL SS 3 was byte-identical to SS 2. The user later: "I HAVE REDOWNLOADED THE GENERAL 3 CONSIDER IT AS 5TH". It went into slot 06, `4010f985`, as "tired-of-sun-damage".
- "IS THE GENERAL VIDEOS FIXED? SHOW ME THOSE".

### Phase 7: PS UGC redo with new creator footage (Oct 11 21:30Z to Oct 12 00:00Z)
- **Oct 11 21:30Z:** "I HAVE DOWNLOADED 2 UGC ADS, CAN YOU ADD IN CLIPS TO IT AND MAKE THEM A COMPLETE UGC AD AS PER OUR GUIDELINE, AND EXCHANGE THEM WITH 2 OF OUR SUNSCREEN UGC ADS? REMOVE THESE 2" (the-tint-is-made-for-indian-skin, and-no-it-doesn-t-stay-purple).
- "SHOW ME THESE VIDEOS" / "WHERE???"
- **Oct 11 21:49Z:** "I THINK YOU NEED TO UNDERSTAND WHAT SCRIPT YOU ARE GOING TO SHOW AND REDO THE VO AND THEN ALSO THE BEFORE AFTER SCENE GET IT FROM CODEX… YOU DO V BAD… ADD OTHER PRODUCT SHOTS IN IT THAT AT LEAST LASTS 2S YOU JUST CUT WITHIN 1S… SEE MY GENERAL ADS THEY HAVE SUCH GOOD PRODUCT SHOTS AND LONG SHOTS WE CAN USE THOSE".
- "I THINK NOW THEY NEED NEW SCRIPTS, FULL NEW IDEATION OF THE SCRIPTS VO AS PER THE FRAMES, AND WE WOULD NEED TO MATCH THE LIPSYNC AS WELL SOMEHOW".
  - Lip-sync answer: "AI lip-sync, local + free" / "YOU CAN USE KAGGLE AS WELL IT HAS GPUS RIGHT".
- "CHECK NEW 3 DOWNLOADS… THEY HAVE THE BEST POTENTIAL TAKE THOSE 3 AND CONVERT INTO A SUNSCREEN UGC AND REMOVE ONE OF THE ONES PRESENT" → UGC 3.
- "IN THE UGC NEW ONE… FIRST HEAR WHAT IS SHE SAYING WHERE IS SHE SAYING WHAT THEN CLIP IT".
- "I GAVE YOU 2 ALREADY SO THOSE 2 STAYS THIS IS THE THIRD, NOW YOU CAN REMOVE ANY OF THE LEFT 3".
- **Blur and font:**
  - "ONE OF THE INGREDIENT PERSONIFIED OR AVATAR AD HAD A BLURRED TEXT DIRECTLY IN THE MIDDLE OF THE SCREEN";
  - "CLIENT HAS ASKED TO GIVE ALL THE ACIDS THE SAME FONT NA?";
  - "THIS ONE IS THE ISSUE / NOT THE OTHERS BUT THIS ONE" (7558fbf1 halos).
- **Oct 11 22:36Z:** "A NEW UGC VIDEO MODEL DOWNLOADED… TAKE THOSE VIDEOS TO MAKE OUR 4TH SS UGC, I WILL ALSO GIVE 5TH SO YOU CAN REMOVE BOTH… SHOW ME UGC 3".
- **Length:**
  - "GREAT VIDEO… BUT ITS 45S WE SHOULD MAKE IT SHORTER, SO WHILE SHE IS TALKING WE COULD SHOW SOME OVERLAY SHOTS ON IT RIGHT??? INSTEAD OF WAITING FOR HER TO FINISH TALKING";
  - "THE VIDEO SHOULDN'T BE VERY VERY LONG" / "30-35 IS STILL FINE".
- "SHOW ME THE LIPSYNC VIDEO" → **"HMMM WHAT IF WE DONT DO THE LIPSYNC CAN YOU DO THEIR BENGALI GENERATIONS WITH THE NEW SCRIPTS PLS WITHOUT THE LIPSYNC"**.
- "ARE YOU GIVING ME UGC 1 2 3 4 WITH A NEW SCRIPT WHICH IS FRAME BY FRAME SCRIPT… IN BANGLA NOW???"
- "ALSO UGC 5 - 4 DOWNLOADS JUST LANDED" / "LETS GET THE 5 UGCS BUILD OUT" / "GET ALL THE LANGUAGES ADDED" / "AND ADDED TO THE FINAL DELIVERABLES".
- "SHOW ME THE BANGLA CUT OF THE UGC 1234. ALSO IF POSSIBLE MAKE A HINDI CUT OF THE SAME SCRIPT SO I CAN UNDERSTAND… ADD GOOD SFX, CLICKS SHOOSH SWOOSHES".
- "IN THE UGC 5 SEE WHEN SHE IS POURING THE CREAM THE BOTTLE IS WRONG SO PLS HANDLE AT THAT TIME". Handled by starting clip e3 at 1.7 s.
- **"HINDI WONT BE REQUIRED… PLS TRY TO PLACE DIALOGUES WHEN THE LIPS ARE MOVING SO EVEN IF WE CANNOT GET THE LIPSYNC RIGHT LETS GET THE AUDIO ON TEXT"** → lipfit.

### Phase 8: final fixes and client message (Oct 11 23:00Z to Oct 12 00:03Z)
- "DHRUV SENT THAT FULL BIG MSG… WHAT WERE THE CHANGES HE REQUESTED DID WE GET THOSE IN?? … CHECK EVERYTHING" / "THIS WAS WHAT HE SENT LETS JUST REVIEW EVERYTHING AND ALSO THAT CHAT".
- "CAN YOU FIX THIS BLURRED TEXT HERE?? WTF!!!!" → `detext.py` inpaint.
- "[key] USE THIS API KEY AND THIS MALAR SOUND TO GENERATE VOICE FOR THE GENERAL ADS". ElevenLabs was blocked: a free plan can't use library voices via the API. The key is saved at `dub/.env.elevenlabs` (chmod 600).
- "SO HAVE WE ADHERED TO ALL THE FEEDBACKS FROM DHRUV AND FROM CLIENT?? DONT CHANGE VIDEOS JUST TELL ME YES OR NO". Answer: no; there was a list of 10 open items.
- **Oct 11 23:32Z:** "WHAT ARE WE GONNA DO ABOUT THE STILL LEFT, CAN WE DO IT WITHOUT GENERATION… I DONT THINK WE CAN DO BLENDING, SS UGCS HAVE THOSE, MORNING TEXT CAN BE FIXED, NIACINAMIDE CAN BE, INGREDIENTS CAN BE, WRONG TUBES ARE FIXED NOW IG, YOU CAN FIX THE GROK WATERMARK, END CARDS CAN BE FIXED, HAVE THE END SLATE PLS. SMALLER ISSUES CAN BE FIXED".
- "GENERAL ADS ARE DONE DONT THINK MUCH ABOUT THEM" / "WHAT NEEDS TO BE FIXED I THOUGHT WE HAD DONE THE HEAVY LIFTING".
- **"U R NOT ALLOWED TO CHANGE THE ENDSLATE IS GIVEN BY THE COMPANY FORGET THE ENDSLATE JUST MAKE SURE FOR IT TO BE IN ALL THE VIDEOS"**. Claude had built a "SHOP AT PURPLLE.COM" slate (`post/make_outro_shop.py`); it was reverted.
- "RUN IT PARALLELY I WANT TO GET THIS DONE IN 10MINS" / "UGC LENGTH IS OK" / "WAS THE GENERAL ADS VOICE GENERATED THROUGH ELEVEN LABS OR NO?" (no, Kokoro).
- "DID YOU ALSO READ CLIENTS ORIGINAL CORRECTIONS LONG ASS CORRECTIONS?"
- **Client message:**
  - "OK NOW CAN WE WRITE A MESSAGE TO THEM THAT WHAT HAS BEEN FIXED, DONT EVEN MENTION WHATS NOT FIXED!"
  - "ALSO WRITE REDID THE WHOLE AI GENERAL COMMERCIALS WITH LONGER SEGMENTS SO THEY FEEL REAL GOOD. UGC FOR SS IS ALSO REDONE ALL, NEW UGC DONE IN THE SUNLIGHT SO THEY FEEL REAL AND GOOD"
  - "SO WRITE A NEW MSG NOW FOR ALL OF THIS"
  - The final message (5 sections: General Ads redone, PS UGC redone, fixes across all, Night Cream specific, PS specific) was written at Oct 11 23:54Z.
- **Oct 12 00:03Z:** Claude reports both final runs done; Final_Deliverables holds 160 files; the user uploads to Drive and sends the message.

### Phase 9: handover (Oct 12 20:36Z)
- The user asks for a full handover package so a friend can continue alone (the user is called into the office):
  - a doc explaining everything (what was done manually, what Claude did, prompts, client issues and wants, models, videos);
  - a Canva kit of all clips for every video;
  - the higgs-purple repo shared;
  - a zip;
  - "we dont have any credits left in higgsfield".

---

## 2. Who did what

**The user (wachas) and team, manually:**
- Wrote the concepts and scripts with Bhxdxx. Generated the original keyframes and frame sheets in ChatGPT/Codex image gen.
- Generated all original videos on Higgsfield with Wan 3.0. Original recipe (from job 33c29291): 480p, 20 s, generate_audio on, references = 2 product photos plus a 5-panel frame sheet, and a shot-by-shot prompt with character dialogue. The Hinglish VO came from the generation itself.
- Downloaded product reference photos (PS tube, box, swatch, texture drip; KNC tub incl. open cream) into Downloads → `feedback/product_refs/`.
- Supplied the reference final video `Sunscream-5 T.mp4` (style for text and captions, now `post/assets/reference_final.mp4`) and `Sunscream-1 T.mp4` (colour-wheel style), the DERMDOC logos, and the 2 company outro videos (WhatsApp), which are the company end slates.
- **Oct 9 evening:** generated or downloaded extra product and B-roll clips: `feedback/user_clips/` (U01–U24…) and Drive SS-1…SS-8.
- **Oct 11:** made the **10 new General Ads** footage himself (KNC 1–5, PS 1–5, numbered in Downloads; Grok/Gemini generations, hence watermarks) → `feedback/user_knc_ads`, `feedback/user_ps_ads`.
- **Oct 11:** downloaded the **new PS UGC creator clips** shot in sunlight: UGC 1–2 (2 ads), UGC 3 (3 clips), UGC 4 ("new UGC video model"), UGC 5 (4 clips) → `feedback/user_ugc*`.
- Managed the Codex login (logout/login, second account) and the Higgsfield CLI login. Provided the Kaggle token and the ElevenLabs key.
- Uploaded to Google Drive by hand and wrote to the client.

**Claude, in Claude Code:**
- Built the whole dubbing engine: stem split, transcription, cast and plan, Indic-Mio voice clone, QA, repair and assembly. Ran it on the Mac plus Kaggle T4.
- Built the post engine:
  - ASS captions with word highlight, English supers, logo, outro, typo covers;
  - synthesized music beds and SFX, ducking, loudness;
  - folder packaging.
- **Round-1 fixes:**
  - mapped all 39 screenshots to video and second;
  - wrote EDLs per video;
  - Codex keyframe redraws (`codex exec`) plus Higgsfield Wan 3.0 5 s 480p clips through the CLI;
  - assembled the fixes (assemble_fix);
  - female recast;
  - colour wheel v2 graphic;
  - before/after split builder;
  - English VO for General Ads (Kokoro).
- **Round-2 fixes:**
  - frame-by-frame script audit (52 line changes);
  - Codex before/after pairs;
  - General Ads VO and timing on the user's footage;
  - PS UGC timeline builder with B-roll cutaways and lipfit;
  - Grok/Gemini watermark removal;
  - detext inpainting;
  - the final QC agents.

---

## 3. Models and tools used

| Purpose | Tool / model | Notes |
|---|---|---|
| Source video gen (original ads) | Higgsfield **Wan 3.0** (`wan3_0`) | By the user/team. 480p, 20 s, audio on, frame-sheet plus product refs. |
| Fix clips | Higgsfield CLI 1.1.26, `higgsfield generate create wan3_0 --prompt … --start-image <png> --resolution 480p --duration 5 --aspect_ratio 9:16 --generate_audio false --wait --json` | **5 credits per clip.** start_image can't combine with image_references. Workspace a5287068-…. `higgsfield generate get <job> --json` returns the original prompts and media. |
| Keyframe edits (5 leftover shots) | Higgsfield **nano_banana_pro** (2 credits), `feedback/hf_keyframe.py` | Used when Codex was locked. |
| Credits | ~240.8 at the start of round 1 → 155.8 after 17 clips → ~110 → 35.8 → **0.8 left (exhausted)** by Oct 10 | The user said 300–400 originally. No Higgsfield credits remain; no new generation was possible after Oct 10. |
| Image gen / redraws | **Codex CLI** 0.162.0, `codex exec --skip-git-repo-check -s workspace-write -C <dir> --image a.png,b.png -` (prompt on stdin), built-in `image_gen` tool → **gpt-image-2** (fallback gpt-image-1.5) | Initially gpt-5.6-sol at reasoning max plus the priority tier, which hit the usage limit ("locked until 10:13 PM"). Then reasoning low (`~/.codex/config.toml`, backup `config.toml.bak_max`). Oct 11: `-m gpt-5.6-luna -c model_reasoning_effort=low` (smallest). Runner: `feedback/codex/gen.py` + `library.json` + `CODEX_BRIEF.md`. |
| Indic TTS (all regional dubs) | **Indic-Mio** (SPRINGLab, Apache-2.0, Qwen3-0.6B based) via mlx-lm batch_generate, plus **MioCodec-25Hz-24kHz** voice cloning (global embedding from ref ranges) | Emotion tags `<happy>`, `<surprise>`, `<angry>`… 4 takes per line; the best Whisper CER that fits. |
| Rejected TTS options | AI4Bharat **IndicF5** (hosted quota ran out after 3 tries, stray syllables), Indic Parler-TTS (HF login), Gemini TTS (key needed), Sarvam Bulbul (paid credit) | |
| English TTS (General Ads) | **Kokoro-82M** (hexgrad), in .venv | Oct 9–10: hf_beta lang "a", "option 4", with a broadcast finish (EQ, de-ess, compression). **Oct 11 final: hf_alpha lang "h" (Indian English, voice "C").** Phonemes forced: `[Dermdoc](/dˈɜɹmdˌɔk/)`, `[Kojic](/kˈOʤɪk/)`. Respellings: "Purplle.com" → "Purple dot com"; "SPF 50 PA+++" → "S P F fifty, P A triple plus". Script: `feedback/ads_english_kokoro.py`. |
| ElevenLabs | Voice "Malar" | **Blocked**: a free account can't use library voices via the API ($5 credits or the Starter plan needed). Not used. Key in `dub/.env.elevenlabs`. |
| Lip-sync | **LatentSync 1.5** on Kaggle 2× T4 (`feedback/lipsync_kaggle.py`, kernel wachaspati/dermdoc-lipsync, dataset wachaspati/dermdoc-lipsync-in) | 1.6 (512 px) didn't fit the GPU. The test worked (`feedback/LIPSYNC_TEST_*.mp4`). **Deferred and not shipped**; replaced by "lipfit" (dialogue placed on mouth-movement windows). |
| Stem split | **Demucs htdemucs** two-stem (vocals / no_vocals) | `prep.py` |
| ASR / QA | **mlx-whisper large-v3-turbo** (Mac); faster-whisper on CUDA | CER QA per language; Odia read through Bengali ASR (Unicode offset 0x180). Whisper loop detection. |
| GPU offload | **Kaggle** CLI 2.2.4 (`.venv/bin/kaggle`, user wachaspati), T4 | `vm/make_kaggle.py` and `make_colab.py` notebooks with an embedded payload (refs as deduped OGG; a 4 MB payload gave a 400 error). Dubbed the 10 ads (unused later). Colab notebook `vm/colab_dub.ipynb` was built but not run. GCP V100 / Lightning AI were rejected (card needed). |
| Video / render | **ffmpeg-full 9.0.2** (`/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`, libass + harfbuzz + h264_videotoolbox) | ASS subtitles at 1080×1920; uharfbuzz word measuring for the highlight box. |
| OCR | Apple Vision via ocrmac (`post/detect_text.py`) | User said stop; not to be used. |
| Music / SFX | Synthesized with numpy/scipy in `post/add_audio.py` | No external library, so copyright-safe. Sidechain ducking, pyloudnorm. |
| Inpaint / text removal | OpenCV Telea inpaint plus blur and grain (`feedback/detext.py`) | Replaced the frosted blur boxes. |
| Watermarks | ffmpeg delogo / crop / clone patch | Grok marks cropped 7%; Gemini sparkle (bottom-right ~x850,y1690) delogo or feathered clone patch. |
| Not used | Google Flow / Veo (offered: browser or Gemini API), Canva (no connector; kit offered) | |

**Mac limits** (16 GB RAM, M-series 4P+6E):
- `guard.py`: OMP 4 threads, `memory_pressure -Q` ≥ 25% free, thermal check, `nice -n 10`.
- One ML process at a time; MLX cache 512 MB; ffmpeg `-threads 4`; max 3 renders.

---

## 4. Client requirements and feedback: what we did and status (honest, internal)

### 4a. Dhruv's WhatsApp, Oct 9 (General Ads section plus per-category lists plus 39 screenshots)

| # | Point | What we did / where | Status |
|---|---|---|---|
| 1 | General Ads: language English | General Ads English-only (memory rule); `build_folders.py` skips their Indic dubs | Done |
| 2 | General Ads "not upto the mark", ref L'Oréal Glycolic-Bright short (youtube.com/shorts/yEy0lEG-UKk); "disappointed" | Round 1: rebuilt from library clips (17.8 s story). Round 2 (Oct 11): replaced by the user's own new footage (`setup_user_general_ads.py`) with new frame-by-frame English VO (`general_ads_vo.py`, Kokoro hf_alpha "h"), only our VO+SFX+music, ending "Shop now at Purplle.com" | Done (user: "GENERAL ADS ARE DONE"). See open issues for remaining footage gaps |
| 3 | Ingredients must be labelled ("3 drops not enough") | Supers/labels in graphics.json; three separate KNC labels | Done |
| 4 | Before/after rework: realistic before, glowy after | Codex BA images (`BA_*`, `BA2_*`, `ADS_*_AFTER`); top/bottom split `GRAPHIC_BA_SPLIT` in assemble_fix | Partly: images added everywhere, but many are still weak or grade-based (open) |
| 5 | Dark spots look like weird dots | Codex redraws of flagged hooks (02bad3b3, a5c00002, 89697c77…) | Partly: still dotty in spot-meeting-cancelled (f7ce58d4), 715b1b5c / 7558fbf1 hooks, bd3b8af7 cheek macro |
| 6 | PS colour wheel unexplained/random; "wrong, check google" (yellow must be opposite purple, not blue) | New full-screen wheel `feedback/graphics/colour_wheel_v2.py` → `cw_v2.mp4` in the Sunscream-1 T style; inserted as `GRAPHIC_COLOUR_WHEEL`; Codex corrected mascot-held wheels; Oct 11 script audit added VO/caption explanation ("purple sits opposite yellow… cancels yellow-looking dullness… made for Indian skin tones") | Done |
| 7 | PS tube has no nozzle; cap missing | Codex+Wan redraws of mascot and tube shots; nozzle shots removed or replaced with exact-tube clips | Mostly done. Leftovers: a nozzle tube in 1 shot of PS purple-tint IP, a clear-cap tube in 1 shot of uv-villain, a carton next to the tube in 2 ads |
| 8 | "Instant Glow" wherever glow is said | Script/caption pass (TEXT_BRIEF), `validate_captions` allows "Instant"; labels AFTER / INSTANT GLOW | Done |
| 9 | Female VO only ("Male vo voice is very scary") | `feedback/apply_voices.py`: female recast of 31 lines in 18 videos (refs: narrator 71e0977a, hero 51440b1f, villain 46d965c9 with fx villain_f) | Done |
| 10 | Likes the "yellow dullness" concept in the PS general ad | Kept in the wheel explanation | Done |
| 11 | PS transformation / instant glow after application | BA splits with INSTANT GLOW; blend clips (U09 etc.) | **Not really done**: application → fully blended → glow is not shown in most videos |
| 12 | Random fancy shots before the end slate | Removed in rebuilt ads | Done |
| 13 | KNC IP: duskier model | Library/Codex models dusky where redrawn | Partial (original shots unchanged; redrawing ~90 shots wasn't affordable) |
| 14 | KNC IP and Avatar: before/after split missing | Added to every video | Done |
| 15 | "2 weeks" call-out only under the after image in the B/A frame | Label AFTER 2 WEEKS on the split only | Done (3xpert's baked "2 weeks" on the sleep shot was erased Oct 11) |
| 16 | Morning wake-up frame text should be "Glowing/Brighter/Clearer skin in the morning" | Text changed; Oct 11 night shots got "WORKS WHILE YOU SLEEP" (390113f1, 46d965c9, 595689d8, 7558fbf1, 89697c77, cd5a6fe8) | Done |
| 17 | Wherever cream is applied it must blend, then show the transformation ("told before as well") | Some blend clips; scoop shots used to hide blobs | **Not done** (the client's #1 ask; would need new generation) |
| 18 | Don't say KNC; say the full product name | Script pass; "Kojic Acid Night Cream" | Done |
| 19 | Label the three ingredients | 2% KOJIC ACID / NIACINAMIDE / ALPHA ARBUTIN; Oct 11 orb labels → single card (715b1b5c, 784c77c5, 02bad3b3, 46d965c9, cd5a6fe8); 7558fbf1 glow halos | Done |
| 20 | After = spotless glowing skin, no tone change | Codex AFTERs, medium grade | Partial (some afters still spotty) |
| 21 | BG music too slow/boring | `post/add_audio.py` music rewritten: PS 124 BPM dance-pop, KNC 118 BPM chill-house | Done |
| 22 | PS IP: why purple tint means no white cast (wheel animation) | See #6 | Done |
| 23 | KNC Avatar: no dark spots in after/morning shots | Redraws for 7558fbf1 S9, 89697c77 S7 | Mostly done |
| 24 | PS Avatar: lipsync between model and product; "under After write instant glow" | AFTER + INSTANT GLOW label | Label done; lipsync not addressed |
| 25 | UGC KNC/PS: lip-sync not synced with VO; VO too animated, make natural | UGC tags set to null (calm); PS UGC fully replaced, lipfit timing; LatentSync tested but deferred | Partial: no true lip-sync |
| 26 | UGC KNC: label the three ingredients; after spotless and glowier; before dull; missing transformation / B/A frame | Ingredient labels, creator's own split graded, Codex stills (a5c00002) | Mostly done |
| 27 | UGC must look much more realistic ("I can make out very easily it is AI") | PS UGC all 5 replaced with new sunlight creator footage (Oct 11) | Done for PS; KNC UGC unchanged |
| 28 | QC all languages yourself | Automated QC (`qc_all.py`, final_qc.json), agent audits | Ongoing |

**Screenshot comments (39, `feedback/issues_screens.json`, frames in `feedback/issue_frames/`):**
- **Nozzle/cap:** PS IP purple-tint 13.3 s; courtroom 2.7 s (cap not on top); PS Avatar purple-tint 7.7 s; 33c29291 8.0 s and 3.0 s (cap missing throughout); 7ea55172 8.3 s; PS UGC tint 6.3 s / 10 s / 19 s.
- **Colour wheel wrong:** PS Avatar 6.0 s; 74495eba 9.3 s; 33c29291 6.3 s and 16.7 s; 7ea55172 7.0 s; UGC tint 5.3 s; UGC both-hands 5.3 s.
- **KNC Avatar:**
  - we-re-moving-in (7558fbf1): spots visible / still night at 15.7 s; "leader of dark spots" at 2.3 s; Kojic twice and Arbutin misspelled at 7.7 / 8.7 s.
  - sleep-to-glow (89697c77): chicken-pox spots at 1.0 s; spots after application at 14 s; third ingredient separate at 7.7 s.
  - night-time-my-time (906fbf3c): same text style at 6.3 s.
  - glow-fusion (715b1b5c): third ingredient separate, align VO at 7.3 s.
- **PS Avatar purple-tint:** two products at 18.7 s; after skin must be healthier/glowier at 18.3 s; "difference?" at 15 s.
- **KNC UGC so-this-became-part-of-every-night:** after shot not good enough at 16.3 s.
- **PS UGC:**
  - tint: "where is the difference, write instant glow under After", residue, "???";
  - both-hands: "remove this" at 19.3 s, not blended at 8.3 s;
  - one-side: "weird shot, it's a sunscreen not a mask/ubtan";
  - how-it-blends: "why is she glowing beforehand";
  - doesn't-stay-purple: "no difference", "looks like a cast, pls blend", "what is she looking into? dull in sunlight makes no sense".
- **Status:**
  - All the PS UGC items were cleared by replacing all 5 PS UGCs.
  - Wheel and nozzle items: fixed via redraws and the wheel graphic.
  - KNC Avatar spelling, labels and "leader": fixed.

### 4b. The Oct 11 review (Priyansh; `feedback/CLIENT_REVIEW_OCT11.md`): main themes and outcome

| Theme | What we did | Status after the Oct 11–12 final pass |
|---|---|---|
| Incomplete application/blending (KNC scoop-only, PS purple face dots, cut to clean face) | Nothing new (no credits); user: "I DONT THINK WE CAN DO BLENDING" | **NOT FIXED** (about 25/30 regional ads, 4/5 new PS UGCs, all 5 KNC General Ads and 2 PS General Ads) |
| Weak or artificially graded before/afters (exposure, blur, angle changes, same stock woman) | Codex BA2 pairs for 5 PS IP and ADS AFTERs (Oct 11 batch `ba3.sh`) | **Partly**: still weak in many PS ads; some KNC splits show spots or mismatched framing |
| Visible blur patches (two-week-face-off 71e0977a, three-step-night-class 23850d94, 715b1b5c) | `feedback/detext.py` inpaint. On 23850d94/71e0977a the inpaint smudged the eyebrow → restored the original footage and removed our duplicate pills. 715b1b5c kept a frosted mask (erase left golden ghost text) | Mostly done; 715b1b5c still has a blur disc at 4.75–6.25 s (user said low priority) |
| "Alpha Arbutin" overlay over a "2% Kojic Acid" graphic (night-time-my-time 906fbf3c) | Label timing fixed | Done |
| Morning wording over night shots (906fbf3c, 89697c77, 46d965c9, cd5a6fe8…) | "WORKS WHILE YOU SLEEP" | Done |
| "After 2 Weeks" on the 3xpert sleep transition | Erased (detext thr 7 from 14.5 s) | Done |
| Duplicated Niacinamide (ce849d3f, 291827ba, c51221b6, 74495eba, 7ea55172, 751fe1db); curved "NIACINAMI" | Removed our duplicate copies; clean erase | Done |
| Ingredient labels not following moving orbs | Replaced with one fixed card listing all 3 (5 ads); 7558fbf1 labelled glow halos | Done |
| Missing "After" above "Instant Glow" | Labels: AFTER (y .895) + INSTANT GLOW (y .955) | Done |
| Subtitle across the after-face forehead | caption_moves y 0.497 (on the divider) | Done |
| Duplicate "purple-tint" filename (ce849d3f) | Renamed "personification-no-more-greasy-sunscreen" (`TITLE_FIX`) | Done |
| Redundant "DARK SPOTS" headline (7558fbf1 ~19 s) | Covered | Done |
| Wheel blurred entrance (skin-protection-department) | Not specifically addressed | Unknown/open |
| Animated jar differs from the pack (shhh-she-s-sleeping) | Not addressed | Open |
| Tube + carton "two products" (655a1328 ~3 s, skin-protection-department 00b304b4) | Not addressed | Open |
| Extra hand/finger artefact; doorway cut; "both hands" concept (old PS UGC) | Old PS UGCs replaced entirely | Done by replacement |
| KNC UGC forgot-your-night-skincare: 3 ingredient labels missing | Not added (Claude argued it has no ingredient elements) | Open |
| General Ads issues (blending, ingredient tags baked wrong in dark-spots-stealing-your-glow, "ONE JAR. ONE STEP." baked text vs VO, labels crossing the eye, Dermdoc heard as "Termdok") | User: "GENERAL ADS ARE DONE DONT THINK MUCH" | **Not fixed** |
| End cards: baked "Available on Purplle" | User forbade changing the company end slate; our VO and pills say "Shop at Purplle.com" | As instructed: end slate unchanged and present on all 30 regional ads |
| Grok watermark on new PS UGCs (d6c1e78e, b876bd3c, a135c7dc, 010ea465) | Cropped / patched | Done |
| Logo overlapping the end slate's logo | `logo_until` in graphics.json | Done |

---

## 5. Standing rules and preferences
1. **Product accuracy** (memory dermdoc-product-accuracy).
   - **PS tube:** white squeeze tube, lavender "ULTRA VIOLET" vertical band, wide flat translucent lavender cap, **never a nozzle, cap always on**. Cream is pale lavender, blends invisibly (no residue, cast, watery look or mask/ubtan).
   - **KNC jar:** blue base, white lid, white label "2% KOJIC ACID / GLOW FUSION FORMULA with Niacinamide & Alpha Arbutin / NIGHT CREAM"; thick white cream; night use only.
   - Always attach `feedback/product_refs/*` to image and video generations.
   - Never alter text on the product, the packaging or its reflections.
2. **Consult before generating** (memory): show the plan plus credit cost and get a yes. Never change an ad's storyline or characters; redraw the flagged frame with the same composition.
3. **Regen workflow** (memory): Codex for images, Higgsfield Wan 3.0 480p 5 s for video, cheapest settings. Higgsfield credits are now **0**.
4. **General Ads English only** (memory). Indian-English female VO (Kokoro hf_alpha "h"). Only our VO + SFX + music (strip the footage audio). Words must land on the right frame.
5. **CTA:** "Shop at Purplle.com" / "Shop now at Purplle.com". Never "Available on Purplle" in our text or VO.
6. **The company end slate** (`post/assets/outro_uv_sunscreen.mp4`, `outro_kojic_night_cream.mp4`, or the baked company card in 6 UGCs and a5c00002) **must never be changed** and must be in every video. Our logo stops where the slate starts (`logo_until`).
7. **Female VO only**; natural, not over-animated (UGC lines have tag null).
8. **"Instant Glow"** wherever PS glow is mentioned. Sunscreen B/A label: AFTER with INSTANT GLOW under it. KNC: AFTER 2 WEEKS only on the split frame. Morning text only on morning shots; night shots say "WORKS WHILE YOU SLEEP".
9. **Never say "KNC"** in VO; use the full product name. Three ingredients are labelled separately as 2% KOJIC ACID, NIACINAMIDE, ALPHA ARBUTIN, in the same font.
10. **3XPERT** is the correct spelling (not EXPERT).
11. **Colour wheel:** purple opposite yellow, Sunscream-1 T style; the graphic is final ("the wheel is ok"), so don't edit it. The explanation goes in the VO and captions.
12. **Captions** are in the video's own language, 1–2 words at a time with a brand-blue (#2F4DB0) highlight box. English brand and ingredient terms stay in Latin (DERMDOC, Niacinamide, Kojic Acid, SPF 50 PA+++, Instant Glow). Comfortable word spacing.
13. **On-screen supers** are English, few and short, in brand fonts Lato and Roboto Mono (client wants Lato/Roboto Mono). Logo top-left throughout. No duration text.
14. **Languages:** Bengali (WB), Tamil (TN), Telugu (APTS), Malayalam (KL), Odia (Od). No Hindi or English for regional categories. Hindi review cuts were only for the user's understanding (not needed now).
15. **Hedged claims only** ("helps", "looking", "visibly"); no fairness or whitening.
16. **UGC:** 30–35 s is OK (UGC 2 at 37.5 s accepted: "UGC LENGTH IS OK"). Product B-roll shots ≥ 2 s. Cut away to B-roll while she talks rather than waiting. Swoosh+click SFX on cuts.
17. **Music:** upbeat, not slow, not droney; audible but under the VO; copyright-free (synthesized).
18. **Process:**
    - Respect Mac limits (one ML job, ≤ 3 renders).
    - No credit cards for any service.
    - Don't read lots of images or OCR (the user's usage limits).
    - Run in parallel when possible.
    - Give status updates.
    - Never echo the Kaggle or ElevenLabs keys.
19. **Client messages:** list only what's fixed ("DONT EVEN MENTION WHATS NOT FIXED").
20. **Drive:** the user uploads manually to folder `19w34s79NseHTH5C6Nq-9jpYUtA0bPfR0` ("Final_Deliverables (1)"), replacing the old folders (to trash).

---

## 6. Known open issues (not fixed as of Oct 12)
1. **Application → full blending → transformation is not shown on screen.** This is the client's #1 repeated ask.
   - KNC ads mostly show a scoop from the jar.
   - PS ads cut from purple dots or a patch to a clean face.
   - 4 of 5 new PS UGCs have the same problem.
   - The General Ads leave cream on the cheek or hand (all 5 KNC; PS greasy-sunscreen and water-resistant).
   - Three PS General Ads (stepping-out, worried-about-sun-damage, tired-of-sun-damage) use an animated skin-coating instead of real application and have no real B/A.
   - Needs new generation (none possible: 0 credits).
2. **Weak before/afters:** the difference reads as exposure, colour or blur. The PS ads reuse the same stock woman. Some KNC afters keep spots, mismatched framing or a different woman.
3. **Dotty, chicken-pox-like spots:** spot-meeting-cancelled (f7ce58d4); hooks of 715b1b5c and 7558fbf1; bd3b8af7 cheek macro.
4. **Packaging leftovers:**
   - a nozzle tube in 1 shot of PS purple-tint IP (c51221b6);
   - a clear-cap tube in 1 shot of uv-villain (e7e42eaf);
   - a carton beside the tube in 655a1328 (~3 s) and 00b304b4;
   - the animated KNC jar in shhh-she-s-sleeping differs from the pack.
5. **Baked typos and text left in footage:**
   - 89697c77 end slate "2% KOJIC ACIC NIGHT CREAM" (noted Oct 9; check whether it is still visible);
   - the baked "The KNC Team" caption in 71e0977a S2;
   - 715b1b5c frosted blur disc with garbled text at 4.75–6.25 s.
6. **Duskier models:** only where shots were redrawn; original shots unchanged.
7. **No real lip-sync.** UGC dialogue is only placed on mouth-movement windows (lipfit). LatentSync 1.5 on Kaggle works but is deferred (`feedback/lipsync_kaggle.py` is ready: prep → push → pull → splice; add 010ea465 to SEGS).
8. **General Ads** (ignored per the user):
   - SS 3 "tired-of-sun-damage" (4010f985) is ~77% the same frames as stepping-out-unprotected (fe7174d4);
   - SS 3 had some of the footage's own music in its mix;
   - "…on the look of dark spots" plays as a fragment in 3 KNC ads;
   - "It works while you sleep" plays over baked "ONE JAR. ONE STEP.";
   - APPLY AT NIGHT labels cross the eye;
   - dark-spots-stealing-your-glow has baked wrong tags ("Kojic Arbutin", Niacinamide twice) plus our card;
   - Whisper heard "Termdok" once;
   - all 10 end on the footage's own "Available on purplle" card.
9. **Baked "Available on Purplle" company end cards** remain by instruction; the user forbade changing them.
10. **Other open items:**
    - KNC UGC forgot-your-night-skincare has no 3-ingredient labels;
    - the skin-protection-department wheel entrance is blurred;
    - Canva/CapCut editable kit not yet delivered (requested again in the handover).
11. The Kaggle Indic dubs of the 10 general ads, the Hindi review cuts and the `make_outro_shop.py` slate are unused leftovers.

---

## 7. The 40 ads (final set)
Naming in Final_Deliverables:
- regional: `<PS|KNC>_<Category>_<title>_<Language>.mp4` under `<N_Category>/<Product>/<Lang_Code>/`;
- General Ads: `4_AI_General_Ads/<Product>/<PS|KNC>_General-Ad_<title>_English.mp4`.

The number prefix is the deliver/ order. Counts: 30 regional × 5 languages = 150, plus 10 English General Ads = **160 files**.

**1_Ingredient_Personified (style personification), 17 s each**

| # | id | Prod | Title |
|---|---|---|---|
| 01 | bd3b8af7 | KNC | the-night-team-clocks-in (15 s) |
| 02 | f7ce58d4 | KNC | spot-meeting-cancelled |
| 03 | 23850d94 | KNC | three-step-night-class |
| 04 | 71e0977a | KNC | the-two-week-face-off |
| 05 | 390113f1 | KNC | shhh-she-s-sleeping |
| 06 | e7e42eaf | PS | uv-villain-attack |
| 07 | c51221b6 | PS | purple-tint |
| 08 | ce849d3f | PS | no-more-greasy-sunscreen (was a 2nd "purple-tint"; renamed) |
| 09 | 291827ba | PS | the-sunscreen-courtroom |
| 10 | 00b304b4 | PS | skin-protection-department |

**2_Product_Avatar (style product_avatar), 20 s each**

| # | id | Prod | Title |
|---|---|---|---|
| 11 | 5fd50ab8 | PS | morning-skin-drama-again |
| 12 | 655a1328 | PS | purple-tint |
| 13 | 33c29291 | PS | purple-tint (_33c29291 suffix; the pilot video) |
| 14 | 74495eba | PS | purple-tint (_74495eba) |
| 15 | 7ea55172 | PS | purple-tint (_7ea55172) |
| 16 | 906fbf3c | KNC | night-time-my-time |
| 17 | 595689d8 | KNC | 3xpert-control-panel |
| 18 | 7558fbf1 | KNC | we-re-moving-in-permanently |
| 19 | 89697c77 | KNC | sleep-to-glow |
| 20 | 715b1b5c | KNC | glow-fusion-night-patrol |

**3_UGC_Ads (style ugc)**

| # | id | Prod | Title | Notes |
|---|---|---|---|---|
| 21 | b876bd3c | PS | will-it-turn-me-purple | New SS UGC 2 (Oct 11), replaced dad2130b; 37.5 s |
| 22 | d6c1e78e | PS | it-actually-blends-in | New SS UGC 1, replaced caf29456; 34.3 s |
| 23 | a135c7dc | PS | can-we-talk-about-annoying-sunscreens | New UGC 3 (3 clips), replaced 3d01d9fc; 32.2 s |
| 24 | 010ea465 | PS | finding-a-good-sunscreen | New UGC 5 (4 clips), replaced 65a0c520; 34.0 s |
| 25 | 751fe1db | PS | it-is-literally-purple | New UGC 4, replaced 51440b1f; 32.8 s |
| 26 | 02bad3b3 | KNC | look-at-that-thick-rich-texture | 20 s, original creator plus fixes |
| 27 | 46d965c9 | KNC | so-my-nighttime-reset-starts-with-this | 20 s |
| 28 | 784c77c5 | KNC | dermdoc-2-kojic-acid-night-cream | 20 s |
| 29 | cd5a6fe8 | KNC | so-this-became-part-of-every-night | 20 s |
| 40 | a5c00002 | KNC | forgot-your-night-skincare | "KNC UGC 2.mp4", added Oct 9 as the 5th KNC UGC; no logo, no outro (baked card); 23 s |

The old PS UGCs (caf29456, dad2130b, 3d01d9fc, 51440b1f, 65a0c520) are archived in `post/superseded/replaced_ugc`. Their old titles were the ones the client flagged: the-tint-is-made-for-indian-skin, and-no-it-doesn-t-stay-purple, now-watch-both-hands, let-s-test-it-on-one-side, but-the-real-test-is-how-it-blends.

**4_AI_General_Ads (style product_ad, kind ad_dub), English only, the user's own footage since Oct 11**

| # | id | Prod | Title | User file |
|---|---|---|---|---|
| 01 | a9be56d9 | KNC | dark-spots-stealing-your-glow | knc1 |
| 02 | 426b77bb | KNC | night-is-when-your-skin-does-its | knc2 |
| 03 | eab38211 | KNC | new-dark-spots-again | knc3 |
| 04 | e9528636 | KNC | the-overnight-brightener | knc4 |
| 05 | b4c787e1 | KNC | those-dark-spots-again (35.8 s) | knc5 |
| 06 | 4010f985 | PS | tired-of-sun-damage | ps3 (re-downloaded "General 3") |
| 07 | c01adcce | PS | worried-about-sun-damage | ps1 |
| 08 | fe7174d4 | PS | stepping-out-unprotected | ps2 |
| 09 | fb3fa838 | PS | greasy-sunscreen | ps4 |
| 10 | ce52c347 | PS | water-resistant-sweat-proof (first caption changed to avoid a duplicate title) | ps5 |

- The previous Hinglish titles the client saw (e.g. dark-spots-scattered-hain, yellow-looking-dullness-ko-balance-karne, ek-sunscreen-two-smart-actions) were our rebuilt versions; they are now superseded in `post/superseded/general_ours/`.
- Cast types: the IP and Avatar ads have villain / product_mascot / hero / narrator voices (brainrot / meme style); the UGCs have one creator; the General Ads have one female narrator.

---

## 8. Key scripts and pipeline order

**A. Dubbing (regional languages)**
1. `prep.py`: downloads or reads source.mp4 → `work/<id>/` (meta.json, frames, Demucs stems, mlx-whisper transcript.json with f0).
2. Director agents write `work/<id>/plan.json` (cast with ref_ranges/fx, lines with en+bn/ta/te/ml/or) per `DIRECTOR_BRIEF.md`.
3. `validate_plan.py`:
   - per-language CPS budgets `{"bn":13.0,"or":12.5,"te":14.5,"ml":15.5,"ta":15.5}`;
   - script-only characters (no Latin or digits; ':' not allowed in te);
   - writes plan.ok.
4. `dubplan.py` (engine), with `--watch` and `dub.lock` claiming:
   - voices (MioCodec embedding from ref_ranges or `ref_file`);
   - sample (Indic-Mio batched MLX, 4 takes);
   - check (Whisper CER);
   - finish (pitch match, fx cartoon / villain / villain_f);
   - `assemble.py` (layout, tempo ≤ 1.25, loudness match to the original vocals, -1 dBFS) → `out/<id>_<lang>.mp4` + `out/<id>_<lang>/` (line wavs, script.json, qa.json, layout.json).
5. Related scripts:
   - `repair.py`: re-voices failed lines (CER ≥ 0.6 or pitch off > 4 st).
   - `redub.py`: re-voices only the lines in `work/<id>/redub.json` in 5 languages and re-assembles over `source_fixed.mp4`.
   - `dubfast.py`, `gen_mio.py`: faster and experimental engines.
   - `guard.py`: the Mac safety guard.
6. GPU offload: `vm/` (`dubplan_cuda.py`, `make_kaggle.py`, `make_colab.py`, `setup.sh`, `run_all.sh`, `kaggle_watch.sh`).

**B. Picture fixes (round 1 and 2)**
- `feedback/match_screens.py`: ORB matching of client screenshots → `screens_match.json`, `issues_screens.json`.
- Shot detection → `feedback/shots/`.
- EDLs: `feedback/edl/<id>.json` (v1) and `feedback/edl_v2/<id>.json` (keep/replace per shot, GRAPHIC_COLOUR_WHEEL, GRAPHIC_BA_SPLIT with ba_pair, split_grade, zoom, clip_offset, use_rebuild).
- `feedback/codex/gen.py` (+ `library.json`, `CODEX_BRIEF.md`, `prompts/`, `out/`): Codex keyframes and BA images.
- `feedback/wan_gen.py` (+ `wan_jobs.json`): Higgsfield Wan 3.0 clips → `feedback/clips/`.
- `feedback/hf_keyframe.py`: nano banana keyframes.
- `feedback/composite_static.py`: locks a region (the wheel) to the keyframe.
- `feedback/spot_clear.py`: local spot inpaint (superseded).
- `feedback/graphics/colour_wheel_v2.py` → `cw_v2.mp4`: the approved wheel. Don't change it.
- **`feedback/assemble_fix.py` (key):**
  - builds `work/<id>/source_fixed.mp4` (1080×1920) from the EDL;
  - Ken Burns for stills; BA split top/bottom; join re-encoded;
  - `remux(id)` puts the fixed picture into `out/<id>_<lang>.mp4`.
- `feedback/apply_voices.py`: female recast.
- `feedback/apply_script.py`: applies the script-audit line changes (`feedback/script_audit/final_changes.json`, translations.json) to plan and captions, writes redub.json.
- `feedback/pipeline.py`: dub lane plus render lanes (round 1 orchestration).
- **General Ads (Oct 11):**
  - `feedback/setup_user_general_ads.py`: swaps the user's footage into the 10 slots;
  - `feedback/general_ads_vo.py` (VO per shot, check/apply);
  - `feedback/ads_english_kokoro.py hf_alpha h <ids>`.
- **PS UGC (Oct 11):**
  - `feedback/build_ugc_timeline.py`: PLANS of ("me", t0, t1), ("b", broll_key), ("WHEEL", s), ("BA", s) with the creator's audio continuing under cutaways; BROLL from `feedback/user_ps_ads`; builds edl_v2 plus source.mp4.
  - `feedback/lipfit/lipfit.py` + `analyze.py`: places dub phrases on lip-movement windows.
  - `feedback/lipsync_kaggle.py`: LatentSync, deferred.
- **Cleanup:**
  - `feedback/detext.py`: inpaint baked text. Always reads `source_fixed.pretext.mp4`, so list all boxes every run.
  - `degrok.py` (scratchpad): Grok watermark.
  - `feedback/find_endcards.py` → `endcards.json`: baked end-card start times.

**C. Post-production and packaging (per id × lang)**
1. `post/render_post.py` (`--ids --langs --ads --force --jobs ≤3 --preview ID LANG --times`).
   - Inputs: `work/<id>/graphics.json` (hook_mono, pill, claim_bold, label incl. style glow, hud, blur, caption_moves, no_logo, no_outro, logo_until, cut_sfx, own_music) and `captions_<lang>.json`.
   - Renders 1080×1920: ASS captions with highlight, supers, logo top-left, the company outro appended (5 s) unless no_outro.
   - Output: `deliver/<Language>/NN_…_<id>.mp4`.
   - Fonts are in `post/fonts` (Lato, Roboto Mono, Noto Indic).
   - Validators: `post/validate_graphics.py`, `post/validate_captions.py`.
2. `post/add_audio.py`:
   - synthesized music bed per product (PS 124 BPM, KNC 118 BPM);
   - SFX bank (pop, whoosh, hit, spark, tag, ding, swoosh…) mapped to graphics, plus cut_sfx;
   - sidechain ducking, limiter;
   - output to `deliver_music/`.
3. `post/build_folders.py`: `deliver_music/` → `Final_Deliverables/` (categories, products, language folders; English General Ads; TITLE_FIX).
4. Loudnorm to -16 LUFS plus the QC script (`qc_all.py`, `feedback/final_qc.json`); scratchpad `pack.sh` = build_folders + loudnorm.
5. Final orchestration scripts used Oct 11–12 (in the session scratchpad):
   - `final_all.sh`: renders all 30 regional ids × 5 languages, then add_audio and pack.
   - `final_fix4.sh`: re-renders 715b1b5c, 23850d94, 71e0977a and f7ce58d4.
   - Also `ugc_finish.sh`, `ugc5.sh`, `script2.sh`.
6. Other scripts:
   - `post/export_cuts.py`: General_Ads_Cuts/<name>/Cut_NN_*.mp4 + cuts.csv (raw cuts for an editor).
   - `post/review_hindi.py`: Hindi review cuts (not needed).
   - `post/make_outro_shop.py`: not to be used (end slate must not change).
   - `post/prep_ads.py`, `post/fix_ad_captions.py`, `post/export_layouts.py`, `organize.py`: earlier stages.
   - `post/detect_text.py`: OCR, don't use.

**Backups and archives:**
- `post/superseded/`: round1 deliveries, general_ours, replaced_ugc, old scripts.
- `feedback/plan_backup/`, `feedback/ads_backup/`, `feedback/edl_ads_v2_backup/`, `feedback/graphics_backup/`.

**Review folders:** `feedback/review/` (UGC, STORY_19, ADS, VOICE_SAMPLES), `feedback/REVIEW_UGC_BENGALI`, `feedback/REVIEW_UGC_HINDI`.
